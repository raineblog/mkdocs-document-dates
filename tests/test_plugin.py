import pytest
from unittest.mock import MagicMock, patch
from mkdocs_document_dates.plugin import DocumentDatesPlugin, Author
from datetime import datetime, timezone

def test_plugin_init():
    plugin = DocumentDatesPlugin()
    assert plugin.data_cached == {}

def test_author_class():
    author = Author(name="Test", email="test@example.com")
    assert author.name == "Test"
    assert author.email == "test@example.com"

def test_on_config_basic():
    plugin = DocumentDatesPlugin()
    plugin.config = {
        'type': 'date',
        'locale': 'en',
        'date_format': '%Y-%m-%d',
        'time_format': '%H:%M:%S',
        'position': 'top',
        'exclude': [],
        'show_created': True,
        'show_updated': True,
        'show_author': True,
        'readtime_wpm': 200,
        'readtime_wpm_cjk': 300,
        'recently-updated': {}
    }

    class Config(dict):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.docs_dir = 'docs'
            self.theme = MagicMock()
            self.theme.name = 'material'
            self.plugins = MagicMock()
            self['extra_css'] = []
            self['extra_javascript'] = []

    config = Config()

    # Patch only Path.exists to return False to avoid complex nested mocking of Path divisions and globbing
    with patch('mkdocs_document_dates.plugin.Path.exists', return_value=False):
        plugin.on_config(config)

    assert any('material-icons.css' in css for css in config['extra_css'])

def test_formatting_date():
    plugin = DocumentDatesPlugin()
    plugin.config = {
        'type': 'date',
        'locale': 'en',
        'date_format': '%Y-%m-%d',
        'time_format': '%H:%M:%S'
    }
    dt = datetime(2023, 5, 20, 12, 0, 0, tzinfo=timezone.utc)
    formatted = plugin._formatting_date(dt)
    assert formatted == '2023-05-20'

def test_insert_date_info_top():
    plugin = DocumentDatesPlugin()
    plugin.config = {'position': 'top'}
    markdown = "# Title\nContent"
    date_info = "<div>Date</div>"
    result = plugin._insert_date_info(markdown, date_info)
    assert "<div>Date</div>" in result
    assert "# Title" in result

def test_insert_date_info_bottom():
    plugin = DocumentDatesPlugin()
    plugin.config = {'position': 'bottom'}
    markdown = "# Title\nContent"
    date_info = "<div>Date</div>"
    result = plugin._insert_date_info(markdown, date_info)
    assert result.endswith("<div>Date</div>")


def _make_plugin_with_cache():
    plugin = DocumentDatesPlugin()
    plugin.config = {
        'type': 'date',
        'locale': 'en',
        'date_format': '%Y-%m-%d',
        'time_format': '%H:%M:%S',
        'position': 'top',
        'exclude': [],
        'show_created': True,
        'show_updated': True,
        'show_author': True,
        'readtime_wpm': 200,
        'readtime_wpm_cjk': 300,
        'recently-updated': {},
    }
    plugin._exclude_patterns = []
    plugin.data_cached = {
        'index.md': {
            'created': datetime(2023, 1, 1, 12, 0, 0, tzinfo=timezone.utc),
            'updated': datetime(2023, 6, 1, 12, 0, 0, tzinfo=timezone.utc),
            'authors': [{'name': 'gituser', 'email': 'g@example.com'}],
        }
    }
    return plugin


class _FakeFile:
    def __init__(self, src_uri):
        self.src_uri = src_uri


class _FakePage:
    def __init__(self, src_uri, url, meta):
        self.file = _FakeFile(src_uri)
        self.url = url
        self.meta = meta


def test_on_page_markdown_without_author_meta():
    plugin = _make_plugin_with_cache()
    page = _FakePage('index.md', '/index/', {})

    result = plugin.on_page_markdown('# Title\n\nContent', page, {}, None)

    assert 'document-dates-plugin' in result
    assert page.meta['document_dates']['authors'][0].name == 'gituser'
    assert page.meta['document_dates']['dates']['created'].year == 2023
    assert page.meta['document_dates_created'] == '2023-01-01 12:00'


def test_on_page_markdown_merges_and_dedupes_authors():
    plugin = _make_plugin_with_cache()
    plugin.authors_yml = {'jay': Author(name='jay', email='j@example.com')}
    plugin.data_cached['index.md']['authors'].append(
        {'name': 'jay', 'email': 'j@example.com'}
    )
    page = _FakePage('index.md', '/index/', {'authors': ['jay']})

    result = plugin.on_page_markdown('# Title\n\nContent', page, {}, None)

    assert 'document-dates-plugin' in result
    authors = page.meta['document_dates']['authors']
    assert len(authors) == 2
    assert {a.name for a in authors} == {'jay', 'gituser'}


def test_on_page_markdown_missing_dates_returns_markdown():
    plugin = _make_plugin_with_cache()
    plugin.data_cached['index.md'].pop('created')
    page = _FakePage('index.md', '/index/', {})

    result = plugin.on_page_markdown('# Title\n\nContent', page, {}, None)

    assert result == '# Title\n\nContent'
    assert page.meta['document_dates']['authors'][0].name == 'gituser'
