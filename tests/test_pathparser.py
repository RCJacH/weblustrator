import pytest

from weblustrator.render import _PathParser


@pytest.mark.parametrize(
    'path, relative', [
        ('https://host:port/local.html', '/local.html')
    ]
)
def test_urls(path, relative):
    parser = _PathParser(path)
    assert parser.relative == relative
    assert parser.netloc == 'host:port'


def test_locals():
    pass
