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
        self.path = relative_path
        self._filepath = filepath
        self._ext = self.path.suffix[1:]
        self._meta = load_meta(filepath.parent, meta)
        self._content = None

    @property
    def content(self):
        if not self._content:
            self.parse()
        return self._content

    def parse(self):
        post = frontmatter.load(self._filepath)
        if post.metadata:
            self._meta.update(post.metadata)

        try:
            template = self._meta.pop('template')
        except KeyError:
            template = 'default'
        finally:
            template = template_func[template]

        self._content = getattr(self, f'_{self._ext}')(post.content, template)

    def _html(self, post, template):
        return template(post, **self._meta)

    def _pug(self, post, template, *args, **kwargs):
        html = pypugjs.process(
            post,
            filename=self._filepath.name,
            compiler=Compiler,
        )
        template = template_func['Jinja2']
        return self._html(html, template=template, *args, **kwargs)

    def _svg(self, *args, **kwargs):
        return self._html(*args, **kwargs)

    def _tpl(self, post, template, *args, **kwargs):
        template = template_func['SimpleTemplate']
        return self._html(post, template=template, *args, **kwargs)


class Server(object):
    def __init__(self, path):
        self.path = path
        self.meta = load_meta(self.path, {})
        self.app = bottle.Bottle()
        self._route()

    def _route(self):
        self.app.route('/', callback=self._index)
        self.app.route('/<filepath:path>', callback=self._add_post)

    def _index(self):
        posts = []
        self._add_contents('html', posts)
        self._add_contents('svg', posts)
        self._add_contents('pug', posts)
        self._add_contents('tpl', posts)
        posts.sort(key=lambda x: x.path)
        return bottle.template('index', posts=posts)

    def _add_contents(self, ext, posts):
        for allowed_file in self.path.rglob(f'*.{ext}'):
            page = Page(allowed_file, self.path)
            posts.append(page)

    def _add_post(self, filepath):
        page = Page(pathlib.Path(filepath), self.path, meta=self.meta)
        return page.content

    def run(self, host='localhost', port='5500', **kwargs):
        server = livereload.Server(self.app)
        server.watch(self.path)
        server.serve(host=host, port=port, **kwargs)
