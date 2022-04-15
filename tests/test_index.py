import pathlib
import pytest
import webtest

from weblustrator.server import Server

PROJECT_PATH = pathlib.Path(__file__).parent / 'project'


@pytest.fixture(scope="module")
def server():
    s = Server(PROJECT_PATH)
    yield webtest.TestApp(s.app)
    s.close()


def test_server_online(server):
    resp = server.get('/')
    assert resp.status_int == 200


def test_home_page_list(server):
    resp = server.get('/')
    assert len(resp.lxml.xpath('//main//li/a')) == 7
    assert len(resp.lxml.xpath('//main//li/button')) == 7

