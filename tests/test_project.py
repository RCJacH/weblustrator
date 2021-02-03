import pathlib

import pytest
from webtest import TestApp

from weblustrator.project import Project

RESOURCE_PATH = pathlib.Path(__file__).parent / 'project'


@pytest.fixture(scope='module')
def project():
    return Project(RESOURCE_PATH)


@pytest.fixture(scope='module')
def app(project):
    return TestApp(project.app)


def test_index(app):
    resp = app.get('/')
    assert resp.status == '200 OK'
    assert resp.content_type == 'text/html'
    assert len(resp.html.find_all('a')) == 7


def test_no_meta_no_template(app):
    resp = app.get('/no_meta_no_template.html')
    assert resp.status == '200 OK'
    assert resp.content_type == 'text/html'
    assert 'Hello World!' in resp


def test_template_no_meta(app):
    resp = app.get('/template_no_meta.html')
    assert resp.status == '200 OK'
    assert resp.content_type == 'text/html'
    assert 'Variable from: Project Config' in resp


def test_frontmatter_local(app):
    resp = app.get('/with_frontmatter/local.html')
    assert resp.status == '200 OK'
    assert resp.content_type == 'text/html'
    assert 'This file has local variable' in resp


def test_frontmatter_pug(app):
    resp = app.get('/with_frontmatter/folder.pug')
    assert resp.status == '200 OK'
    assert resp.content_type == 'text/html'
    assert 'Pug file' in resp
    assert 'Folder Config' in resp


def test_tpl(app):
    resp = app.get('/with_frontmatter/subsubfolder/simple_template.tpl')
    assert resp.status == '200 OK'
    assert resp.content_type == 'text/html'
    assert 'Variable from Project Config' in resp
