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
