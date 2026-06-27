import pytest
from mkdocs_document_dates.utils import (
    analyze_markdown,
    is_excluded,
    compile_exclude_patterns,
    DEFAULT_WPM,
    DEFAULT_WPM_CJK
)

def test_analyze_markdown_basic():
    md = """# Title
This is a test paragraph with some words.
"""
    minutes, summary = analyze_markdown(md)
    assert minutes == 1
    assert "This is a test paragraph" in summary

def test_analyze_markdown_cjk():
    md = "你好，这是一个测试。" # 9 characters
    minutes, summary = analyze_markdown(md)
    assert minutes >= 1
    assert "你好" in summary

def test_analyze_markdown_mixed():
    md = "Hello 你好"
    minutes, summary = analyze_markdown(md)
    assert minutes >= 1

def test_analyze_markdown_frontmatter():
    md = """---
title: My Page
date: 2023-01-01
---
# Actual Title
Content here.
"""
    minutes, summary = analyze_markdown(md)
    assert "title: My Page" not in summary
    assert "Content here" in summary

def test_analyze_markdown_fence():
    md = """
```python
print("hello")
```
Text after code.
"""
    minutes, summary = analyze_markdown(md)
    assert 'print("hello")' not in summary
    assert "Text after code" in summary

def test_exclude_patterns():
    patterns = ["temp.md", "blog/*", "*/index.md"]
    compiled = compile_exclude_patterns(patterns)

    assert is_excluded("temp.md", compiled) is True
    assert is_excluded("blog/post1.md", compiled) is True
    assert is_excluded("docs/index.md", compiled) is True
    assert is_excluded("other.md", compiled) is False

def test_analyze_markdown_images():
    md = "![alt](img.png)"
    minutes, summary = analyze_markdown(md)
    # Reading time for an image alone should be very low, but the function ceils to 1 minute
    assert minutes >= 1
    assert summary == ""

def test_analyze_markdown_long_content():
    # Create content long enough to exceed 1 minute
    # Default WPM is 200. 300 words should be ~1.5 minutes, ceiled to 2.
    md = "word " * 300
    minutes, summary = analyze_markdown(md)
    assert minutes == 2
