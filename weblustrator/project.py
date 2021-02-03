import asyncio
import configparser
import pathlib

from weblustrator.server import Server


class Project(object):
    def __init__(self, project_folder):
        self.path = pathlib.Path(project_folder)
        self.config = configparser.ConfigParser()
        self.config.read(self.path / 'config.ini')
        self._server = None
        self._browser = None

    @property
    def server(self):
        if not self._server:
            self._server = Server(self.path)
        return self._server

    def serve(self, **kwargs):
        self.server.run(**kwargs)


if __name__ == '__main__':
    project = Project(pathlib.Path(__file__).parent.parent / 'tests' / 'project')
    project.serve()
