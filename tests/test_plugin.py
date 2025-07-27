"""
Test the core functionality of the MkDocs Free-Text Plugin.

This test verifies that:
1. Plugin runs when !!! freetext syntax appears
2. Question and question config can be read correctly  
3. Rich markdown (images, mermaid diagrams, links) display properly once parsed
"""

import pytest
from mkdocs_freetext.plugin import FreetextPlugin
from mkdocs.structure.pages import Page
from mkdocs.structure.files import File
import tempfile
import os


def test_plugin_triggers_on_freetext_syntax():
    """Test that the plugin runs when !!! freetext syntax appears in HTML."""
    plugin = FreetextPlugin()
    plugin.load_config({})
    
    # Create mock page
    mock_file = type('MockFile', (), {'src_path': 'test.md'})()
    mock_page = type('MockPage', (), {'file': mock_file})()
    
    # HTML that contains freetext admonition (as it would appear after MkDocs processing)
    html_with_freetext = '''
<div class="admonition freetext">
    <p class="admonition-title">Freetext</p>
    <p>question: What is Python?</p>
    <p>marks: 3</p>
    <p>placeholder: Enter your answer here...</p>
</div>
'''
    
    # Process the HTML
    result = plugin.on_page_content(html_with_freetext, mock_page, {}, None)
    
    # Verify plugin ran and modified the HTML
    assert result != html_with_freetext, "Plugin should have processed the HTML"
    assert 'freetext-question' in result, "Should contain question class"
    assert 'data-question-id' in result, "Should contain question ID"
    assert 'textarea' in result, "Should contain textarea for answer input"
    
    print("✅ Plugin triggers correctly on !!! freetext syntax")


def test_question_config_parsing():
    """Test that question configuration is read and applied correctly."""
    plugin = FreetextPlugin()
    plugin.load_config({})
    
    # Create mock page
    mock_file = type('MockFile', (), {'src_path': 'test.md'})()
    mock_page = type('MockPage', (), {'file': mock_file})()
    
    # HTML with specific configuration
    html_with_config = '''
<div class="admonition freetext">
    <p class="admonition-title">Freetext</p>
    <p>question: Explain the concept of variables in Python.</p>
    <p>marks: 5</p>
    <p>placeholder: Write your explanation here...</p>
    <p>type: long</p>
    <p>show_answer: true</p>
    <p>answer: Variables are containers for storing data values.</p>
</div>
'''
    
    # Process the HTML
    result = plugin.on_page_content(html_with_config, mock_page, {}, None)
    
    # Verify configuration was applied
    assert '(5 marks)' in result, "Should show marks badge"
    assert 'Write your explanation here...' in result, "Should use custom placeholder"
    assert 'rows="6"' in result, "Should use long answer rows for type=long"
    
    # Verify question content is preserved
    assert 'Explain the concept of variables in Python.' in result, "Should preserve question text"
    
    print("✅ Question configuration parsing works correctly")


def test_rich_markdown_preservation():
    """Test that rich markdown content (images, mermaid, links) is preserved."""
    plugin = FreetextPlugin()
    plugin.load_config({})
    
    # Create mock page
    mock_file = type('MockFile', (), {'src_path': 'test.md'})()
    mock_page = type('MockPage', (), {'file': mock_file})()
    
    # HTML with rich content (as it would appear after MkDocs markdown processing)
    html_with_rich_content = '''
<div class="admonition freetext">
    <p class="admonition-title">Freetext</p>
    <p>question: Analyze the following diagram and code:</p>
    <p><img src="test-image.png" alt="Test Image" /></p>
    <pre class="mermaid"><code>graph TD
    A[Start] --> B[Process]
    B --> C[End]</code></pre>
    <div class="language-python highlight"><pre><span></span><code><span class="k">def</span> <span class="nf">hello</span><span class="p">():</span>
    <span class="k">return</span> <span class="s2">"Hello World"</span></code></pre></div>
    <p><a href="https://example.com">Reference Link</a></p>
    <p>marks: 10</p>
    <p>placeholder: Provide your analysis...</p>
</div>
'''
    
    # Process the HTML
    result = plugin.on_page_content(html_with_rich_content, mock_page, {}, None)
    
    # Verify rich content is preserved in question
    assert '<img src="test-image.png" alt="Test Image" />' in result, "Should preserve images"
    assert '<pre class="mermaid"><code>' in result, "Should preserve Mermaid diagrams"
    assert 'language-python highlight' in result, "Should preserve code blocks"
    assert '<a href="https://example.com">Reference Link</a>' in result, "Should preserve links"
    
    # Verify configuration still works
    assert '(10 marks)' in result, "Should show marks badge"
    assert 'Provide your analysis...' in result, "Should use custom placeholder"
    
    print("✅ Rich markdown content preservation works correctly")


def test_multiple_questions_on_page():
    """Test that multiple questions on the same page are processed correctly."""
    plugin = FreetextPlugin()
    plugin.load_config({})
    
    # Create mock page
    mock_file = type('MockFile', (), {'src_path': 'test.md'})()
    mock_page = type('MockPage', (), {'file': mock_file})()
    
    # HTML with multiple questions
    html_with_multiple = '''
<div class="admonition freetext">
    <p class="admonition-title">Freetext</p>
    <p>question: First question?</p>
    <p>marks: 2</p>
</div>

<p>Some content between questions.</p>

<div class="admonition freetext">
    <p class="admonition-title">Freetext</p>
    <p>question: Second question?</p>
    <p>marks: 3</p>
</div>
'''
    
    # Process the HTML
    result = plugin.on_page_content(html_with_multiple, mock_page, {}, None)
    
    # Count question elements
    question_count = result.count('freetext-question')
    textarea_count = result.count('<textarea')
    marks_count = result.count('marks')
    
    assert question_count == 2, f"Should have 2 questions, found {question_count}"
    assert textarea_count == 2, f"Should have 2 textareas, found {textarea_count}"
    assert '(2 marks)' in result, "Should show first question marks"
    assert '(3 marks)' in result, "Should show second question marks"
    
    # Verify content between questions is preserved
    assert 'Some content between questions.' in result, "Should preserve content between questions"
    
    print("✅ Multiple questions processing works correctly")


def test_question_without_config():
    """Test that questions work with minimal configuration (using defaults)."""
    plugin = FreetextPlugin()
    plugin.load_config({})
    
    # Create mock page
    mock_file = type('MockFile', (), {'src_path': 'test.md'})()
    mock_page = type('MockPage', (), {'file': mock_file})()
    
    # HTML with minimal configuration
    html_minimal = '''
<div class="admonition freetext">
    <p class="admonition-title">Freetext</p>
    <p>question: What is your favorite programming language?</p>
</div>
'''
    
    # Process the HTML
    result = plugin.on_page_content(html_minimal, mock_page, {}, None)
    
    # Verify defaults are applied
    assert 'freetext-question' in result, "Should use default question class"
    assert 'Enter your answer...' in result, "Should use default placeholder"
    assert 'rows="3"' in result, "Should use default answer rows"
    assert '(0 marks)' not in result, "Should not show marks when 0"
    
    # Verify question content is preserved
    assert 'What is your favorite programming language?' in result, "Should preserve question text"
    
    print("✅ Questions with minimal config work correctly")


def test_admonition_title_removal():
    """Test that admonition titles are properly removed from question output."""
    plugin = FreetextPlugin()
    plugin.load_config({})
    
    # Create mock page
    mock_file = type('MockFile', (), {'src_path': 'test.md'})()
    mock_page = type('MockPage', (), {'file': mock_file})()
    
    html_with_title = '''
<div class="admonition freetext">
    <p class="admonition-title">Freetext</p>
    <p>question: Simple question</p>
    <p>marks: 5</p>
</div>
'''
    
    result = plugin.on_page_content(html_with_title, mock_page, {}, None)
    
    # Verify the admonition title is completely removed
    assert 'admonition-title' not in result, "Admonition title class should be removed"
    assert '>Freetext<' not in result, "Freetext title text should be removed"
    
    # Verify the content is preserved and processed correctly
    assert 'Simple question' in result, "Question text should be preserved"
    assert '(5 marks)' in result, "Marks should be displayed"
    assert 'freetext-question' in result, "Should generate question container"
    
    print("✅ Admonition titles are properly removed")


def test_marks_display_with_various_content():
    """Test that marks are displayed correctly across different content types."""
    plugin = FreetextPlugin()
    plugin.load_config({})
    
    # Create mock page
    mock_file = type('MockFile', (), {'src_path': 'test.md'})()
    mock_page = type('MockPage', (), {'file': mock_file})()
    
    test_cases = [
        # Simple question
        ('''
<div class="admonition freetext">
    <p class="admonition-title">Freetext</p>
    <p>question: Simple question</p>
    <p>marks: 3</p>
</div>
''', '(3 marks)'),
        # Question with image
        ('''
<div class="admonition freetext">
    <p class="admonition-title">Freetext</p>
    <p>question: Question with image</p>
    <p><img src="test.png" /></p>
    <p>marks: 5</p>
</div>
''', '(5 marks)'),
        # Question with code
        ('''
<div class="admonition freetext">
    <p class="admonition-title">Freetext</p>
    <p>question: Question with code</p>
    <div class="language-python highlight"><pre><code>print("hello")</code></pre></div>
    <p>marks: 7</p>
</div>
''', '(7 marks)')
    ]
    
    for i, (html, expected_marks) in enumerate(test_cases):
        result = plugin.on_page_content(html, mock_page, {}, None)
        assert expected_marks in result, f"Should display {expected_marks} for test case {i+1}"
    
    print("✅ Marks are displayed correctly with various content types")


def test_config_stripping_without_leakage():
    """Test that configuration is stripped and doesn't leak into question content."""
    plugin = FreetextPlugin()
    plugin.load_config({})
    
    # Create mock page
    mock_file = type('MockFile', (), {'src_path': 'test.md'})()
    mock_page = type('MockPage', (), {'file': mock_file})()
    
    html_with_config = '''
<div class="admonition freetext">
    <p class="admonition-title">Freetext</p>
    <p>question: Test question</p>
    <p>marks: 10</p>
    <p>placeholder: Your analysis...</p>
    <p>show_answer: true</p>
    <p>answer: Sample answer</p>
</div>
'''
    
    result = plugin.on_page_content(html_with_config, mock_page, {}, None)
    
    # Get the question content section (before textarea)
    if '<textarea' in result:
        question_section = result.split('<textarea')[0]
    else:
        question_section = result
    
    # Verify config is stripped from question display
    assert 'marks: 10' not in question_section, "Config should not appear in question text"
    assert 'placeholder: Your analysis...' not in question_section, "Config should not appear in question text"
    assert 'show_answer: true' not in question_section, "Config should not appear in question text"
    assert 'answer: Sample answer' not in question_section, "Config should not appear in question text"
    
    # Verify config is applied correctly
    assert '(10 marks)' in result, "Marks should be displayed"
    if '<textarea' in result:
        assert 'placeholder="Your analysis..."' in result, "Placeholder should be applied to textarea"
    
    print("✅ Configuration is properly stripped without leakage")


if __name__ == "__main__":
    print("🧪 Running MkDocs Free-Text Plugin Core Tests...")
    print()
    
    try:
        test_plugin_triggers_on_freetext_syntax()
        test_question_config_parsing()
        test_rich_markdown_preservation()
        test_multiple_questions_on_page()
        test_question_without_config()
        test_admonition_title_removal()
        test_marks_display_with_various_content()
        test_config_stripping_without_leakage()
        
        print()
        print("🎉 All core plugin tests passed! The plugin is working correctly.")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
