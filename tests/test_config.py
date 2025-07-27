"""
Test the configuration system for the MkDocs Free-Text Plugin.

This test verifies that:
1. Default config values are properly loaded
2. User config from mkdocs.yml properly overrides defaults
3. The plugin can access these config values correctly
"""

import pytest
from mkdocs_freetext.plugin import FreetextPlugin


def test_default_config_values():
    """Test that default config values are properly set."""
    plugin = FreetextPlugin()
    
    # Load empty config to get defaults - this simulates MkDocs loading process
    plugin.load_config({})
    
    # Validate that plugin config has all expected defaults
    expected_defaults = {
        'question_class': 'freetext-question',
        'assessment_class': 'freetext-assessment',
        'answer_class': 'freetext-answer',
        'container_class': 'freetext-container',
        'enable_css': True,
        'dark_mode_support': True,
        'shuffle_questions': False,
        'show_character_count': True,
        'enable_auto_save': True,
        'default_answer_rows': 3,
        'default_long_answer_rows': 6,
        'default_placeholder': 'Enter your answer...',
        'default_marks': 0,
        'default_show_answer': True,
        'default_question_type': 'short',
    }
    
    for key, expected_value in expected_defaults.items():
        actual_value = plugin.config[key]  # Access as dictionary
        assert actual_value == expected_value, f"Config {key}: expected {expected_value}, got {actual_value}"


def test_user_config_override():
    """Test that user config from mkdocs.yml properly overrides defaults."""
    plugin = FreetextPlugin()
    
    # Create config with user overrides
    user_config = {
        'show_character_count': False,
        'default_answer_rows': 5,
        'default_placeholder': 'Custom placeholder text',
        'default_marks': 10,
        'shuffle_questions': True,
    }
    
    plugin.load_config(user_config)
    
    # Verify user values override defaults
    assert plugin.config['show_character_count'] == False
    assert plugin.config['default_answer_rows'] == 5
    assert plugin.config['default_placeholder'] == 'Custom placeholder text'
    assert plugin.config['default_marks'] == 10
    assert plugin.config['shuffle_questions'] == True
    
    # Verify non-overridden values remain as defaults
    assert plugin.config['question_class'] == 'freetext-question'
    assert plugin.config['enable_css'] == True
    assert plugin.config['default_question_type'] == 'short'


def test_plugin_config_access():
    """Test that the plugin can properly access config values."""
    plugin = FreetextPlugin()
    
    # Mock the plugin config attribute
    user_config = {
        'show_character_count': False,
        'default_answer_rows': 8,
        'default_placeholder': 'Test placeholder',
        'default_marks': 5,
    }
    
    plugin.load_config(user_config)
    
    # Test accessing config values via plugin.config dictionary access
    assert plugin.config['show_character_count'] == False
    assert plugin.config['default_answer_rows'] == 8
    assert plugin.config['default_placeholder'] == 'Test placeholder'
    assert plugin.config['default_marks'] == 5
    
    # Test that we can also use get() method with fallbacks for defensive programming
    assert plugin.config.get('show_character_count', True) == False
    assert plugin.config.get('default_answer_rows', 3) == 8
    assert plugin.config.get('default_placeholder', 'Enter your answer...') == 'Test placeholder'
    assert plugin.config.get('default_marks', 0) == 5
    
    # Test accessing non-existent values with fallbacks
    assert plugin.config.get('non_existent_key', 'fallback') == 'fallback'


def test_config_scheme_completeness():
    """Test that the config_scheme includes all required keys."""
    plugin = FreetextPlugin()
    
    # Extract all config keys from the scheme
    scheme_keys = {key for key, _ in plugin.config_scheme}
    
    # Expected keys based on our defaults test
    expected_keys = {
        'question_class', 'assessment_class', 'answer_class', 'container_class',
        'enable_css', 'dark_mode_support', 'shuffle_questions', 'show_character_count',
        'enable_auto_save', 'default_answer_rows', 'default_long_answer_rows',
        'default_placeholder', 'default_marks', 'default_show_answer', 'default_question_type'
    }
    
    # Check that all expected keys are in the scheme
    missing_keys = expected_keys - scheme_keys
    assert not missing_keys, f"Missing keys in config_scheme: {missing_keys}"


def test_config_types():
    """Test that config values have correct types."""
    plugin = FreetextPlugin()
    plugin.load_config({})
    
    # Test string configs
    string_configs = ['question_class', 'assessment_class', 'answer_class', 'container_class', 
                     'default_placeholder', 'default_question_type']
    for key in string_configs:
        value = plugin.config[key]
        assert isinstance(value, str), f"Config {key} should be string, got {type(value)}"
    
    # Test boolean configs
    bool_configs = ['enable_css', 'dark_mode_support', 'shuffle_questions', 
                   'show_character_count', 'enable_auto_save', 'default_show_answer']
    for key in bool_configs:
        value = plugin.config[key]
        assert isinstance(value, bool), f"Config {key} should be boolean, got {type(value)}"
    
    # Test integer configs
    int_configs = ['default_answer_rows', 'default_long_answer_rows', 'default_marks']
    for key in int_configs:
        value = plugin.config[key]
        assert isinstance(value, int), f"Config {key} should be integer, got {type(value)}"


def test_default_marks_applied_to_questions():
    """Test that default_marks is applied when question doesn't specify marks."""
    plugin = FreetextPlugin()
    plugin.load_config({'default_marks': 10})
    
    # Create mock page
    mock_file = type('MockFile', (), {'src_path': 'test.md'})()
    mock_page = type('MockPage', (), {'file': mock_file})()
    
    # Question without marks specification
    html_no_marks = '''
<div class="admonition freetext">
    <p class="admonition-title">Freetext</p>
    <p>question: Test question without marks</p>
    <p>placeholder: Enter your answer</p>
</div>
'''
    
    result = plugin.on_page_content(html_no_marks, mock_page, {}, None)
    
    # Should use default marks from plugin config
    assert '(10 marks)' in result, f"Should show default marks of 10"


def test_default_placeholder_applied_to_questions():
    """Test that default_placeholder is applied when question doesn't specify placeholder."""
    plugin = FreetextPlugin()
    plugin.load_config({'default_placeholder': 'Write your response here...'})
    
    # Create mock page
    mock_file = type('MockFile', (), {'src_path': 'test.md'})()
    mock_page = type('MockPage', (), {'file': mock_file})()
    
    # Question without placeholder specification
    html_no_placeholder = '''
<div class="admonition freetext">
    <p class="admonition-title">Freetext</p>
    <p>question: Test question without placeholder</p>
    <hr>
    <p>marks: 5</p>
</div>
'''
    
    result = plugin.on_page_content(html_no_placeholder, mock_page, {}, None)
    
    # Should use default placeholder from plugin config
    assert 'Write your response here...' in result, f"Should use default placeholder"


def test_default_answer_rows_applied_to_questions():
    """Test that default_answer_rows is applied when question doesn't specify rows or type."""
    plugin = FreetextPlugin()
    plugin.load_config({'default_answer_rows': 8})
    
    # Create mock page
    mock_file = type('MockFile', (), {'src_path': 'test.md'})()
    mock_page = type('MockPage', (), {'file': mock_file})()
    
    # Question without rows or type specification
    html_no_rows = '''
<div class="admonition freetext">
    <p class="admonition-title">Freetext</p>
    <p>question: Test question without rows specification</p>
    <hr>
    <p>marks: 5</p>
</div>
'''
    
    result = plugin.on_page_content(html_no_rows, mock_page, {}, None)
    
    # Should use default answer rows from plugin config
    assert 'rows="8"' in result, f"Should use default answer rows of 8"


def test_default_long_answer_rows_applied_to_questions():
    """Test that default_long_answer_rows is applied for type=long questions."""
    plugin = FreetextPlugin()
    plugin.load_config({'default_long_answer_rows': 12})
    
    # Create mock page
    mock_file = type('MockFile', (), {'src_path': 'test.md'})()
    mock_page = type('MockPage', (), {'file': mock_file})()
    
    # Question with type=long but no explicit rows
    html_long_type = '''
<div class="admonition freetext">
    <p class="admonition-title">Freetext</p>
    <p>question: Test long answer question</p>
    <hr>
    <p>type: long,
    marks: 5</p>
</div>
'''
    
    result = plugin.on_page_content(html_long_type, mock_page, {}, None)
    
    # Should use default long answer rows from plugin config
    assert 'rows="12"' in result, f"Should use default long answer rows of 12"


def test_explicit_config_overrides_defaults():
    """Test that explicit question config overrides plugin defaults."""
    plugin = FreetextPlugin()
    plugin.load_config({
        'default_marks': 10,
        'default_placeholder': 'Default placeholder...',
        'default_answer_rows': 8
    })
    
    # Create mock page
    mock_file = type('MockFile', (), {'src_path': 'test.md'})()
    mock_page = type('MockPage', (), {'file': mock_file})()
    
    # Question with explicit configuration
    html_explicit = '''
<div class="admonition freetext">
    <p class="admonition-title">Freetext</p>
    <p>question: Test question with explicit config</p>
    <hr>
    <p>marks: 15,
    placeholder: Custom placeholder text,
    rows: 4</p>
</div>
'''
    
    result = plugin.on_page_content(html_explicit, mock_page, {}, None)
    
    # Should use explicit values, not defaults
    assert '(15 marks)' in result, "Should use explicit marks, not default"
    assert 'Custom placeholder text' in result, "Should use explicit placeholder, not default"
    assert 'rows="4"' in result, "Should use explicit rows, not default"
    
    # Should not use default values
    assert '(10 marks)' not in result, "Should not use default marks"
    assert 'Default placeholder...' not in result, "Should not use default placeholder"
    assert 'rows="8"' not in result, "Should not use default rows"


def test_mixed_default_and_explicit_config():
    """Test questions that use some defaults and some explicit config."""
    plugin = FreetextPlugin()
    plugin.load_config({
        'default_marks': 7,
        'default_placeholder': 'Enter your thoughts...',
        'default_answer_rows': 5
    })
    
    # Create mock page
    mock_file = type('MockFile', (), {'src_path': 'test.md'})()
    mock_page = type('MockPage', (), {'file': mock_file})()
    
    # Question with partial explicit configuration
    html_mixed = '''
<div class="admonition freetext">
    <p class="admonition-title">Freetext</p>
    <p>question: Test question with mixed config</p>
    <hr>
    <p>marks: 12</p>
    <!-- placeholder and rows not specified, should use defaults -->
</div>
'''
    
    result = plugin.on_page_content(html_mixed, mock_page, {}, None)
    
    # Should use explicit marks
    assert '(12 marks)' in result, "Should use explicit marks value"
    
    # Should use default placeholder and rows
    assert 'Enter your thoughts...' in result, "Should use default placeholder"
    assert 'rows="5"' in result, "Should use default answer rows"
