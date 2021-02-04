import pathlib

import bottle
import frontmatter
import pypugjs
from pypugjs.ext.jinja import Compiler

from weblustrator.utils import load_meta


class Page(object):
    template_func = {
        'default': bottle.template,
        'SimpleTemplate': bottle.template,
        'Jinja2': bottle.jinja2_template,
        'Mako': bottle.mako_template,
        'Cheetah': bottle.cheetah_template,
    }

    def __init__(self, file_path, project_path, meta=None):
        """Create a parser to build a web page with templates.

        Parameters
        ----------
        file_path : [str, Pathlike]
            The path to the source file
        project_path : [str, Pathlike]
            The path to the project, to calculate the relative path for
            the url.
        meta : dict, optional
            The fallback metadata from project, which will be updated
            with metadata from the file directory, and then updated with
            metadata in frontmatter.
        """
        path = pathlib.Path(file_path).resolve()
        filepath = project_path / path
        relative_path = pathlib.Path(filepath).relative_to(project_path)
        self.path = relative_path
        self._filepath = filepath
        self._ext = self.path.suffix[1:]
        self.meta = load_meta(filepath.parent, meta)
        self._content = None

    @property
    def content(self):
        """Return the actual content of the page.

        The content is the string data after parsing frontmatter and
        compilation.

        Returns
        -------
        str
            The html/xml data to be displayed in a web browser.
        """
        if not self._content:
            self.parse()
        return self._content

    def parse(self, meta_only=False):
        """Parse the content of the file.

        Parameters
        ----------
        meta_only : bool, optional
            Only parse the metadata from frontmatter, do not render
            content with templates.
        """
        post = frontmatter.load(self._filepath)
        if post.metadata:
            self.meta.update(post.metadata)

        try:
            template = self.meta.pop('template')
        except KeyError:
            template = 'default'
        finally:
            template = self.template_func[template]

        if meta_only:
            return
        self._content = getattr(self, f'_{self._ext}')(post.content, template)

    def _html(self, post, template):
        return template(post, **self.meta)

    def _pug(self, post, template, *args, **kwargs):
        html = pypugjs.process(
            post,
            filename=self._filepath.name,
            compiler=Compiler,
        )
        template = self.template_func['Jinja2']
        return self._html(html, template=template, *args, **kwargs)

    def _svg(self, *args, **kwargs):
        return self._html(*args, **kwargs)

    def _tpl(self, post, template, *args, **kwargs):
        template = self.template_func['SimpleTemplate']
        return self._html(post, template=template, *args, **kwargs)
