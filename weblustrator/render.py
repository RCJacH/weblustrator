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

        query = []
        for arg in args:
            page_file = sorted(list(self.path.glob(arg)))
            query += page_file

        for each_page in query:
            relative_path = each_page.relative_to(self.path)
            self.render(relative_path, **kwargs)

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
            if render_to.is_path():
                render_to = render_to / path.with_suffix(f'.{ext}').name
        else:
            render_to = self.path / path.with_suffix(f'.{ext}')

        page = Page(path, self.path)
        if not page.content_parser:
            return

        page.parse(meta_only=True)
        canvas_size = page.meta.get('canvas_size', [800, 600])
        for i, v in enumerate(kwargs.pop('canvas_size')):
            canvas_size[i] = v
        asyncio.get_event_loop().run_until_complete(
            self._screenshot(
                url,
                render_to,
                canvas_size=canvas_size,
                **kwargs,
            ),
        )

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
        await page.goto(url)
        await page.setViewport({'width': width, 'height': height})
        await page.screenshot(path=render_to, omitBackground=True, **kwargs)
