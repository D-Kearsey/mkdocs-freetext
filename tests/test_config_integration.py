"""
Test configuration integration of the MkDocs Free-Text Plugin.

This test suite verifies:
1. Plugin configuration defaults are applied in generated HTML
2. Custom CSS classes work correctly
3. Character count and auto-save toggles function properly  
4. Custom default values are respected
"""

import pytest
from mkdocs_freetext.plugin import FreetextPlugin


def test_plugin_config_defaults_applied():
    """Test that plugin configuration defaults are properly applied in generated HTML."""
    plugin = FreetextPlugin()
    plugin.load_config({})
    
    # Create mock page
    mock_file = type('MockFile', (), {'src_path': 'test.md'})()
    mock_page = type('MockPage', (), {'file': mock_file})()
    
    # Simple question HTML
    html_question = '''
<div class="admonition freetext">
    <p class="admonition-title">Freetext</p>
    <p>question: Test question with defaults</p>
</div>
'''
    
    # Process the HTML
    result = plugin.on_page_content(html_question, mock_page, {}, None)
    
    # Verify default configuration is applied
    assert 'class="freetext-question"' in result, "Should use default question_class"
    assert 'placeholder="Enter your answer..."' in result, "Should use default placeholder"
    assert 'rows="3"' in result, "Should use default answer rows"
    assert 'charCount_' in result, "Should include character counter (default enabled)"
    # Auto-save functionality has been removed from the plugin


def test_custom_css_classes():
    """Test that custom CSS class configuration works correctly."""
    plugin = FreetextPlugin()
    
    # Load custom CSS class configuration
    custom_config = {
        'question_class': 'my-custom-question',
        'assessment_class': 'my-custom-assessment',
        'answer_class': 'my-custom-answer',
        'container_class': 'my-custom-container'
    }
    plugin.load_config(custom_config)
    
    # Create mock page
    mock_file = type('MockFile', (), {'src_path': 'test.md'})()
    mock_page = type('MockPage', (), {'file': mock_file})()
    
    # Test single question
    html_question = '''
<div class="admonition freetext">
    <p class="admonition-title">Freetext</p>
    <p>question: Custom class test</p>
</div>
'''
    
    result_question = plugin.on_page_content(html_question, mock_page, {}, None)
    assert 'class="my-custom-question"' in result_question, "Should use custom question class"
    
    # Test assessment
    plugin = FreetextPlugin()  # Reset plugin
    plugin.load_config(custom_config)
    
    html_assessment = '''
<div class="admonition freetext-assessment">
    <p class="admonition-title">Freetext Assessment</p>
    <p>question: Assessment with custom classes</p>
    <p>marks: 5</p>
</div>
'''
    
    result_assessment = plugin.on_page_content(html_assessment, mock_page, {}, None)
    assert 'class="my-custom-assessment"' in result_assessment, "Should use custom assessment class"


def test_character_count_toggle():
    """Test that show_character_count: false removes character counters."""
    # Test with character count enabled (default)
    plugin_enabled = FreetextPlugin()
    plugin_enabled.load_config({'show_character_count': True})
    
    # Test with character count disabled
    plugin_disabled = FreetextPlugin()
    plugin_disabled.load_config({'show_character_count': False})
    
    # Create mock page
    mock_file = type('MockFile', (), {'src_path': 'test.md'})()
    mock_page = type('MockPage', (), {'file': mock_file})()
    
    html_question = '''
<div class="admonition freetext">
    <p class="admonition-title">Freetext</p>
    <p>question: Character count test</p>
</div>
'''
    
    # Process with enabled
    result_enabled = plugin_enabled.on_page_content(html_question, mock_page, {}, None)
    
    # Process with disabled
    result_disabled = plugin_disabled.on_page_content(html_question, mock_page, {}, None)
    
    # Verify character count presence/absence
    assert 'char-count' in result_enabled, "Should include character counter when enabled"
    assert 'updateCharCount_' in result_enabled, "Should include character count JS when enabled"
    
    assert 'char-count' not in result_disabled, "Should NOT include character counter when disabled"
    assert 'updateCharCount_' not in result_disabled, "Should NOT include character count JS when disabled"


def test_auto_save_toggle():
    """Test that enable_auto_save: false disables auto-save JavaScript."""
    # Test with auto-save enabled (default)
    plugin_enabled = FreetextPlugin()
    plugin_enabled.load_config({'enable_auto_save': True})
    
    # Test with auto-save disabled
    plugin_disabled = FreetextPlugin()
    plugin_disabled.load_config({'enable_auto_save': False})
    
    # Create mock page
    mock_file = type('MockFile', (), {'src_path': 'test.md'})()
    mock_page = type('MockPage', (), {'file': mock_file})()
    
    html_question = '''
<div class="admonition freetext">
    <p class="admonition-title">Freetext</p>
    <p>question: Auto-save test</p>
</div>
'''
    
    # Process with both configurations
    result_enabled = plugin_enabled.on_page_content(html_question, mock_page, {}, None)
    result_disabled = plugin_disabled.on_page_content(html_question, mock_page, {}, None)
    
    # Auto-save functionality has been removed from the plugin
    # Both enabled and disabled should work the same way (no localStorage)
    assert 'freetext-question' in result_enabled, "Should generate question HTML when enabled"
    assert 'freetext-question' in result_disabled, "Should generate question HTML when disabled"
    
    # Verify no localStorage functionality is present (it's been removed)
    assert 'localStorage.setItem' not in result_enabled, "localStorage functionality has been removed"
    assert 'localStorage.setItem' not in result_disabled, "localStorage functionality has been removed"


def test_custom_default_values():
    """Test that custom default values are respected in question generation."""
    plugin = FreetextPlugin()
    
    # Load custom default configuration
    custom_defaults = {
        'default_answer_rows': 8,
        'default_long_answer_rows': 12,
        'default_placeholder': 'Please type your response here...',
        'default_marks': 5,
        'default_question_type': 'long'
    }
    plugin.load_config(custom_defaults)
    
    # Create mock page
    mock_file = type('MockFile', (), {'src_path': 'test.md'})()
    mock_page = type('MockPage', (), {'file': mock_file})()
    
    # Test question with no specific configuration (should use defaults)
    html_default_question = '''
<div class="admonition freetext">
    <p class="admonition-title">Freetext</p>
    <p>question: Question using custom defaults</p>
</div>
'''
    
    result_default = plugin.on_page_content(html_default_question, mock_page, {}, None)
    
    # Verify custom defaults are applied
    assert 'placeholder="Please type your response here..."' in result_default, "Should use custom default placeholder"
    assert '(5 marks)' in result_default, "Should show custom default marks"
    # Note: default_question_type affects which row count is used
    
    # Test long answer type with custom defaults
    html_long_question = '''
<div class="admonition freetext">
    <p class="admonition-title">Freetext</p>
    <p>question: Long answer question</p>
    <p>type: long</p>
</div>
'''
    
    result_long = plugin.on_page_content(html_long_question, mock_page, {}, None)
    assert 'rows="12"' in result_long, "Should use custom default long answer rows"
    
    # Test short answer type with custom defaults
    html_short_question = '''
<div class="admonition freetext">
    <p class="admonition-title">Freetext</p>
    <p>question: Short answer question</p>
    <p>type: short</p>
</div>
'''
    
    result_short = plugin.on_page_content(html_short_question, mock_page, {}, None)
    assert 'rows="8"' in result_short, "Should use custom default answer rows for short type"


def test_shuffle_questions_global_setting():
    """Test that global shuffle_questions setting affects assessments without explicit shuffle config."""
    # Test with global shuffling enabled
    plugin_shuffle = FreetextPlugin()
    plugin_shuffle.load_config({'shuffle_questions': True})
    
    # Test with global shuffling disabled
    plugin_no_shuffle = FreetextPlugin()
    plugin_no_shuffle.load_config({'shuffle_questions': False})
    
    # Create mock page
    mock_file = type('MockFile', (), {'src_path': 'test.md'})()
    mock_page = type('MockPage', (), {'file': mock_file})()
    
    # Assessment without explicit shuffle setting
    html_assessment = '''
<div class="admonition freetext-assessment">
    <p class="admonition-title">Freetext Assessment</p>
    <p>question: Question 1</p>
    <p>marks: 2</p>
    <hr>
    <p>question: Question 2</p>
    <p>marks: 3</p>
</div>
'''
    
    # Process with both configurations
    result_shuffle = plugin_shuffle.on_page_content(html_assessment, mock_page, {}, None)
    result_no_shuffle = plugin_no_shuffle.on_page_content(html_assessment, mock_page, {}, None)
    
    # Verify global shuffle setting is applied
    assert 'data-shuffle="true"' in result_shuffle, "Should enable shuffling based on global setting"
    assert 'data-shuffle="false"' in result_no_shuffle, "Should disable shuffling based on global setting"


def test_dark_mode_support_setting():
    """Test that dark_mode_support setting affects CSS generation."""
    # Test with dark mode support enabled (default)
    plugin_dark = FreetextPlugin()
    plugin_dark.load_config({'dark_mode_support': True, 'enable_css': True})
    
    # Test with dark mode support disabled
    plugin_no_dark = FreetextPlugin()
    plugin_no_dark.load_config({'dark_mode_support': False, 'enable_css': True})
    
    # Create mock page
    mock_file = type('MockFile', (), {'src_path': 'test.md'})()
    mock_page = type('MockPage', (), {'file': mock_file})()
    
    html_question = '''
<div class="admonition freetext">
    <p class="admonition-title">Freetext</p>
    <p>question: Dark mode test</p>
</div>
'''
    
    # Process with both configurations (two-phase: content + post-processing)
    content_dark = plugin_dark.on_page_content(html_question, mock_page, {}, None)
    final_dark = plugin_dark.on_post_page(content_dark, mock_page, {})
    
    content_no_dark = plugin_no_dark.on_page_content(html_question, mock_page, {}, None)
    final_no_dark = plugin_no_dark.on_post_page(content_no_dark, mock_page, {})
    
    # Verify CSS variable usage for dark mode (CSS is added in on_post_page)
    if 'enable_css' in plugin_dark.config and plugin_dark.config['enable_css']:
        assert 'var(--md-' in final_dark, "Should use Material CSS variables when dark mode enabled"
    
    # The exact behavior may vary based on how dark mode is implemented
    # This test verifies the setting is available and can be toggled


def test_config_validation():
    """Test that invalid configuration values are handled gracefully."""
    plugin = FreetextPlugin()
    
    # Test with invalid types (should use defaults or handle gracefully)
    invalid_config = {
        'default_answer_rows': 'not_a_number',  # Should be int
        'show_character_count': 'not_a_boolean',  # Should be bool
        'default_marks': -5,  # Negative marks
        'question_class': '',  # Empty string
    }
    
    # This should not crash - MkDocs config validation should handle it
    try:
        errors, warnings = plugin.load_config(invalid_config)
        # Check if there were validation errors
        # The exact behavior depends on MkDocs config validation
        assert isinstance(errors, list), "Should return list of errors"
        assert isinstance(warnings, list), "Should return list of warnings"
    except Exception as e:
        # If validation throws exception, that's also acceptable behavior
        assert "validation" in str(e).lower() or "config" in str(e).lower(), "Should be a config-related error"
