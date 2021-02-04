import asyncio
import pathlib
import socket

import pyppeteer


class Photographer(object):
    def __init__(self, path, host, port):
        self.path = pathlib.Path(path)
        self.host = host
        self.port = port
        self._browser = None

    def __call__(self, *args, **kwargs):
        if not self._is_server_online():
            raise ConnectionError('Server not started.')

        query = []
        for arg in args:
            page_file = sorted(self.path.glob(arg))
            query += page_file

        for each_page in query:
            relative_path = each_page.relative_to(self.path)
            self.render(relative_path, **kwargs)

    @property
    async def browser(self):
        if not self._browser:
            self._browser = await pyppeteer.launch(headless=False)
        return self._browser

    def _is_server_online(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            return s.connect_ex((self.host, self.port)) == 0

    async def _screenshot(
        self,
        url,
        render_to,
        width,
        height,
        **kwargs,
    ):
        browser = await self.browser
        page = await browser.newPage()
        await page.goto(url)
        await page.setViewport({'width': width, 'height': height})
        await page.screenshot(path=render_to, omitBackground=True, **kwargs)

    def render(self, path, render_to=None, ext='png', **kwargs):
        url = fr'{self.host}:{self.port}/{path}'
        path = pathlib.Path(path)
        if render_to:
            render_to = pathlib.Path(render_to)
            if render_to.is_path():
                render_to = render_to / path.with_suffix(f'.{ext}').name
        else:
            render_to = self.path / path.with_suffix(f'.{ext}')

        asyncio.get_event_loop().run_until_complete(
            self._screenshot(url, render_to, **kwargs),
        )
