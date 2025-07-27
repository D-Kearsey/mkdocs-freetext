#!/usr/bin/env python3
"""Tests for the --- separator approach in freetext questions."""

import pytest
from mkdocs_freetext.plugin import FreetextPlugin


def test_separator_question_parsing():
    """Test that questions with --- separator parse correctly."""
    plugin = FreetextPlugin()
    plugin.load_config({})
    
    # Create mock page object
    mock_file = type('MockFile', (), {'src_path': 'test.md'})()
    mock_page = type('MockPage', (), {'file': mock_file})()
    
    # Test HTML with --- separator
    html = '''<div class="admonition freetext">
    <p class="admonition-title">Freetext</p>
    <p>Question with code</p>
    <div class="language-python highlight"><pre><code>print("hello")</code></pre></div>
    ---
    <p>marks: 7</p>
</div>'''
    
    result = plugin.on_page_content(html, mock_page, {}, None)
    
    # Verify the --- separator approach works
    assert '(7 marks)' in result, "Should display marks correctly"
    assert 'language-python' in result, "Should preserve code blocks"
    assert 'print("hello")' in result, "Should preserve code content"
    assert 'marks: 7' not in result, "Should not leak config into question content"


def test_separator_with_rich_content():
    """Test --- separator with complex rich content."""
    plugin = FreetextPlugin()
    plugin.load_config({})
    
    mock_file = type('MockFile', (), {'src_path': 'test.md'})()
    mock_page = type('MockPage', (), {'file': mock_file})()
    
    html = '''<div class="admonition freetext">
    <p class="admonition-title">Freetext</p>
    <p>Analyze this code and diagram:</p>
    <img src="images/architecture.png" alt="System Architecture">
    <div class="language-sql highlight"><pre><code>SELECT users.name, orders.total 
FROM users 
JOIN orders ON users.id = orders.user_id
WHERE orders.date > '2024-01-01'</code></pre></div>
    <p>How would you optimize this query?</p>
    ---
    <p>marks: 10</p>
    <p>type: long</p>
    <p>show_answer: true</p>
    <p>answer: Add indexes on user_id and date columns</p>
</div>'''
    
    result = plugin.on_page_content(html, mock_page, {}, None)
    
    # Verify rich content preservation
    assert '<img src="images/architecture.png"' in result, "Should preserve images"
    assert 'language-sql' in result, "Should preserve SQL code blocks"
    assert 'SELECT users.name' in result, "Should preserve SQL content"
    assert '(10 marks)' in result, "Should display marks correctly"
    assert 'rows="6"' in result, "Should use long answer rows for type=long"
    
    # Verify no config leakage
    assert 'marks: 10' not in result, "Should not leak marks config"
    assert 'type: long' not in result, "Should not leak type config"
    assert 'show_answer: true' not in result, "Should not leak show_answer config"


def test_separator_fallback_without_separator():
    """Test that questions without --- separator still work (backwards compatibility)."""
    plugin = FreetextPlugin()
    plugin.load_config({})
    
    mock_file = type('MockFile', (), {'src_path': 'test.md'})()
    mock_page = type('MockPage', (), {'file': mock_file})()
    
    # Old format without separator
    html = '''<div class="admonition freetext">
    <p class="admonition-title">Freetext</p>
    <p>question: What is Python?</p>
    <p>marks: 5</p>
    <p>type: short</p>
</div>'''
    
    result = plugin.on_page_content(html, mock_page, {}, None)
    
    # Should still work with old parsing logic
    assert 'freetext-question' in result, "Should generate question HTML"
    assert '(5 marks)' in result, "Should display marks correctly"


def test_separator_with_mixed_content_order():
    """Test that --- separator works regardless of content order."""
    plugin = FreetextPlugin()
    plugin.load_config({})
    
    mock_file = type('MockFile', (), {'src_path': 'test.md'})()
    mock_page = type('MockPage', (), {'file': mock_file})()
    
    html = '''<div class="admonition freetext">
    <p class="admonition-title">Freetext</p>
    <ul>
        <li>First requirement</li>
        <li>Second requirement</li>
    </ul>
    <p>Implement the following function:</p>
    <div class="language-python highlight"><pre><code>def process_data(data):
    # Your implementation here
    pass</code></pre></div>
    <blockquote>
        <p>Note: Consider edge cases</p>
    </blockquote>
    ---
    <p>marks: 15</p>
    <p>type: long</p>
    <p>rows: 10</p>
</div>'''
    
    result = plugin.on_page_content(html, mock_page, {}, None)
    
    # Verify all content types preserved
    assert '<ul>' in result, "Should preserve lists"
    assert '<li>First requirement</li>' in result, "Should preserve list items"
    assert '<blockquote>' in result, "Should preserve blockquotes"
    assert 'def process_data' in result, "Should preserve code content"
    assert '(15 marks)' in result, "Should display marks"
    assert 'rows="10"' in result, "Should use custom rows setting"
    
    # Verify no config leakage  
    assert 'marks: 15' not in result, "Should not leak config"
