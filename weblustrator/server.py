import pathlib

import bottle
import livereload

from weblustrator.page import Page
from weblustrator.utils import load_meta

VIEWS_PATH = pathlib.Path(__file__).parent / 'views'
bottle.TEMPLATE_PATH.insert(0, VIEWS_PATH)
bottle.debug(True)


class Server(object):
    allowed_file_extensions = [
        'html', 'svg', 'pug', 'tpl',
    ]

    def __init__(self, path):
        """Create a server for preview and render.

        Parameters
        ----------
        path : string
            The path of the project for parsing configurations and files.
        """
        self.path = pathlib.Path(path)
        self.meta = load_meta(self.path, {})
        self.app = bottle.Bottle()
        self._route()

    def run(self, **kwargs):
        """Bring the server online, with live reload."""
        server = livereload.Server(self.app)
        server.watch(self.path)
        server.serve(**kwargs)

    def shutdown(self):
        """Shut the server down manually."""
        self.app.shutdown()

    def _route(self):
        self.app.route('/', callback=self._index)
        self.app.route('/static/<filepath:path>', callback=self._add_static)
        self.app.route('/<filepath:path>', callback=self._add_post)

    def _index(self):
        posts = []
        for each_ext in self.allowed_file_extensions:
            self._add_contents(each_ext, posts)
        posts.sort(key=lambda x: x.path)
        return bottle.template('index', posts=posts)

    def _add_contents(self, ext, posts):
        for allowed_file in self.path.rglob(f'*.{ext}'):
            page = Page(allowed_file, self.path)
            posts.append(page)

    def _add_post(self, filepath):
        page = Page(pathlib.Path(filepath), self.path, meta=self.meta)
        return page.content

    def _add_static(self, filepath):
        path = self.path / filepath
        filename = path.name
        if not path.exists():
            path = self.path / 'static' / filename
        folder = path.parent
        return bottle.static_file(filename, root=f'{self.path / folder}')
