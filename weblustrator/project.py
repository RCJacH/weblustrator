import configparser
import pathlib

import bottle
import frontmatter
import livereload
import pypugjs
import yaml
from pypugjs.ext.jinja import Compiler

VIEWS_PATH = pathlib.Path(__file__).parent / 'views'
bottle.TEMPLATE_PATH.insert(0, VIEWS_PATH)
bottle.debug(True)

template_func = {
    'default': bottle.template,
    'SimpleTemplate': bottle.template,
    'Jinja2': bottle.jinja2_template,
    'Mako': bottle.mako_template,
    'Cheetah': bottle.cheetah_template,
}


def load_meta(meta_file_folder, default=None):
    meta_file = meta_file_folder / 'config.yml'
    try:
        yaml_content = meta_file.read_text(encoding='utf-8')
    except FileNotFoundError:
        return default
    else:
        return yaml.safe_load(yaml_content)


class Page(object):
    def __init__(self, file_path, project_path, meta=None):
        path = pathlib.Path(file_path).resolve()
        filepath = project_path / path
        relative_path = pathlib.Path(filepath).relative_to(project_path)
        self.filepath = filepath
        self.path = relative_path
        self.ext = self.path.suffix[1:]
        self.meta = load_meta(filepath.parent, meta)
        self._content = None

    @property
    def content(self):
        if not self._content:
            self.parse()
        return self._content

    def parse(self):
        post = frontmatter.load(self.filepath)
        if post.metadata:
            self.meta.update(post.metadata)

        try:
            template = self.meta.pop('template')
        except KeyError:
            template = 'default'
        finally:
            template = template_func[template]

        self._content = getattr(self, f'_{self.ext}')(post.content, template)

    def _html(self, post, template):
        return template(post, **self.meta)

    def _pug(self, post, template, *args, **kwargs):
        html = pypugjs.process(
            post,
            filename=self.filepath.name,
            compiler=Compiler,
        )
        template = template_func['Jinja2']
        return self._html(html, template=template, *args, **kwargs)

    def _svg(self, *args, **kwargs):
        return self._html(*args, **kwargs)

    def _tpl(self, post, template, *args, **kwargs):
        template = template_func['SimpleTemplate']
        return self._html(post, template=template, *args, **kwargs)


class Project(object):
    def __init__(self, project_folder, host='localhost', port=8090):
        self.path = pathlib.Path(project_folder)
        self.config = configparser.ConfigParser()
        self.config.read(self.path / 'config.ini')
        self.meta = load_meta(self.path, {})
        self.host = host
        self.port = port
        self.app = bottle.Bottle()

        self.posts = []
        self.add_contents('html')
        self.add_contents('svg')
        self.add_contents('pug')
        self.add_contents('tpl')

        self._route()

    def _route(self):
        self.app.route('/', callback=self._index)
        self.app.route('/<filepath:path>', callback=self._add_post)

    def _index(self):
        return bottle.template('index', posts=self.posts)

    def _add_post(self, filepath):
        page = Page(pathlib.Path(filepath), self.path, meta=self.meta)
        return page.content

    def add_contents(self, ext):
        for allowed_file in self.path.rglob(f'*.{ext}'):
            page = Page(allowed_file, self.path)
            self.posts.append(page)

    def start(self, **kwargs):
        server = livereload.Server(self.app)
        server.watch(self.path)
        server.serve(host=self.host, port=self.port, **kwargs)


if __name__ == '__main__':
    project = Project(pathlib.Path(__file__).parent.parent / 'tests' / 'project')
    project.start()
