import asyncio
import pathlib
import socket

import pyppeteer

from weblustrator.page import Page


class Photographer(object):
    def __init__(self, path, host, port):
        self.path = pathlib.Path(path)
        self.host = host
        self.port = port
        self._loop = None
        self._browser = None

    def __call__(self, *args, **kwargs):
        """Render each file from input glob pattern to images.

        Raises
        ------
        ConnectionError
            The web server must be running to render.
        """
        if not self._is_server_online():
            raise ConnectionError('Server not started.')

        query = args
        if kwargs.get('from_cli'):
            query = []
            for arg in args:
                query.extend(sorted(self.path.glob(arg)))

        for each_page in query:
            path = pathlib.Path(each_page)
            if path.is_absolute():
                path = path.relative_to(self.path)
            self.render(path, **kwargs)

    @property
    async def browser(self):
        """Return the browser instance to take screenshots with.

        Returns
        -------
        [pyppeteer.Browser]
            [description]
        """
        if not self._browser:
            self._browser = await pyppeteer.launch(headless=False)
        return self._browser

    @property
    def loop(self):
        """Return the async loop associated with this instance."""
        if not self._loop or self._loop.is_closed():
            try:
                self._loop = asyncio.get_event_loop()
            except RuntimeError:
                self._loop = asyncio.new_event_loop()
        return self._loop

    def close(self):
        """Close the opened browser of this instance."""
        self.loop.run_until_complete(self._close())

    def render(self, path, render_to=None, ext='png', **kwargs):
        """Render a designated url to a target raster image file.

        Parameters
        ----------
        path : [str, Pathlike]
            The relative link to the url.
        render_to : [str, Pathlike], optional
            The target location to save the render result. If a folder,
            create a file with the same name as the filename from path.
        ext : str, optional
            The extension of the target file, by default 'png', ignored
            if provided in render_to.
        """
        url = fr'{self.host}:{self.port}/{path.as_posix()}'
        path = pathlib.Path(path)
        if render_to:
            render_to = pathlib.Path(render_to)
            if render_to.is_dir():
                render_to = render_to / path.with_suffix(f'.{ext}').name
        else:
            render_to = self.path / path.with_suffix(f'.{ext}')

        page = Page(path, self.path)
        if not page.content_parser:
            return

        page.parse(meta_only=True)
        canvas_size = page.meta.get('canvas_size', [800, 600])
        for i, v in enumerate(kwargs.pop('canvas_size', ())):
            canvas_size[i] = v
        self.loop.run_until_complete(
            self._screenshot(
                url,
                render_to,
                canvas_size=canvas_size,
                **kwargs,
            ),
        )

    async def _close(self):
        await self._browser.close()
        self._browser = None

    def _is_server_online(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            return s.connect_ex((self.host, self.port)) == 0

    async def _screenshot(
        self,
        url,
        render_to,
        canvas_size,
        **kwargs,
    ):
        width, height = canvas_size
        browser = await self.browser
        page = await browser.newPage()
        await page.setViewport({'width': width, 'height': height})
        await page.goto(url, options={'timeout': 0})
        await page.screenshot(path=render_to, omitBackground=True, **kwargs)
