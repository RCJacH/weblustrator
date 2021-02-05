import pathlib
from unittest import mock

import pytest
from click.testing import CliRunner

from weblustrator.cli import cli
from weblustrator.render import Photographer
from weblustrator.server import Server

PROJECT_PATH = pathlib.Path(__file__).parent / 'project'


@pytest.fixture()
def runner():
    return CliRunner()


def test_run(runner):
    cli_result = runner.invoke(cli)
    assert cli_result.exit_code == 0
    assert 'Options:' in cli_result.output
    assert 'Commands:' in cli_result.output
    assert 'serve' in cli_result.output
    assert 'render' in cli_result.output


@pytest.mark.parametrize(
    'args, expect', [
        ([], {'host': 'localhost', 'port': 5500}),
        (['--host', '::1', '--port', '8080'], {'host': '::1', 'port': 8080}),
    ])
@mock.patch.object(Server, 'run')
def test_serve(server_run, args, expect, runner):
    args.insert(0, 'serve')
    runner.invoke(cli, args)
    server_run.assert_called_once_with(**expect)


@pytest.mark.parametrize(
    'args, expect', [
        (
            ['no_meta_no_template.html'],
            [[
                'localhost:5500/no_meta_no_template.html',
                'no_meta_no_template.png',
            ]],
        ),
        (
            ['with_frontmatter/folder.pug', '**/local.html'],
            [[
                'localhost:5500/with_frontmatter/folder.pug',
                'with_frontmatter/folder.png',
            ], [
                'localhost:5500/with_frontmatter/local.html',
                'with_frontmatter/local.png',
            ]],
        ),
    ])
@mock.patch.object(Photographer, '_screenshot')
def test_render(
    render_screenshot,
    args,
    expect,
    runner,
):
    call_count = len(args)
    args = ['render', '--path', PROJECT_PATH] + args
    with mock.patch(
        'weblustrator.render.Photographer._is_server_online',
        return_value=True,
    ):
        runner.invoke(cli, args)
    assert render_screenshot.call_count == call_count
    for i, each_call in enumerate(render_screenshot.call_args_list):
        expect_args = expect[i]
        expect_args[1] = PROJECT_PATH / expect_args[1]
        assert list(each_call.args) == expect_args


@pytest.mark.parametrize(
    'args, expect', [
        pytest.param(
            ['**/local.html'],
            [[30, 20]],
            id='size_from_frontmatter',
        ),
        pytest.param(
            ['with_frontmatter/folder.pug', '--canvas_size', 400, 500],
            [[400, 500]],
            id='size_from_options',
        ),
        pytest.param(
            ['**/with_frontmatter/*.*'],
            [[60, 90], [30, 20]],
            id='frontmatter_overrides_folder_config',
        ),
        pytest.param(
            ['**/local.html', '--canvas_size', 32, 64],
            [[32, 64]],
            id='options_overrides_frontmatter',
        ),
    ])
@mock.patch.object(Photographer, '_screenshot')
def test_canvas_size(
    render_screenshot,
    args,
    expect,
    runner,
):
    args = ['render', '--path', PROJECT_PATH] + args
    with mock.patch(
        'weblustrator.render.Photographer._is_server_online',
        return_value=True,
    ):
        runner.invoke(cli, args)
    for i, each_call in enumerate(render_screenshot.call_args_list):
        expect_canvas_size = expect[i]
        assert each_call.kwargs['canvas_size'] == expect_canvas_size
