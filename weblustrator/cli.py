import os

import click

from weblustrator.render import Photographer
from weblustrator.server import Server

CONTEXT_SETTINGS = {
    'help_option_names': ['-h', '--help'],
}


@click.group(context_settings=CONTEXT_SETTINGS)
def cli():
    """Server and renderer for illustration made with web technology."""
    pass


@cli.command(context_settings=CONTEXT_SETTINGS)
@click.option(
    '-p',
    '--path',
    help='Base folder of the server, optional.',
)
@click.option(
    '--host',
    help='Host IP of the web server.',
    default='localhost',
    show_default=True,
)
@click.option(
    '--port',
    help='Port of the web server.',
    default=5500,
    show_default=True,
)
def serve(path, host, port):
    """Create server for livereload."""
    if not path:
        path = os.getcwd()

    server = Server(path)
    server.run(host=host, port=port)


@cli.command(context_settings=CONTEXT_SETTINGS)
@click.argument('url', nargs=-1, type=str)
@click.option(
    '-p',
    '--path',
    help='Base folder of the server, optional.',
)
@click.option(
    '--host',
    help='Host IP of the web server.',
    default='localhost',
    show_default=True,
)
@click.option(
    '--port',
    help='Port of the web server.',
    default=5500,
    show_default=True,
)
@click.option(
    '--canvas_size',
    type=int,
    nargs=2,
    help='The width and height of the viewport.',
)
def render(
    url,
    path,
    canvas_size,
    host,
    port,
):
    """Render a page or pages into rastered image."""
    if not path:
        path = os.getcwd()

    photographer = Photographer(path, host=host, port=port)
    photographer.render_from_cli(*url, canvas_size=canvas_size)
