"""
Test CSS and styling functionality of the MkDocs Free-Text Plugin.

This test suite verifies:
1. CSS generation when enabled/disabled
2. Dark/light mode theme integration
3. Responsive design elements
4. Custom styling configuration
"""

import os
import tempfile
from mkdocs_freetext.plugin import FreetextPlugin


def test_css_generation_enabled():
    """Test that CSS is generated when enable_css: true."""
    plugin = FreetextPlugin()
    plugin.load_config({'enable_css': True})
    
    # Create mock page
    mock_file = type('MockFile', (), {'src_path': 'test.md'})()
    mock_page = type('MockPage', (), {'file': mock_file})()
    
    html_question = '''
<div class="admonition freetext">
    <p class="admonition-title">Freetext</p>
    <p>question: CSS generation test</p>
</div>
'''
    
    # First process the content (this generates questions)
    content_result = plugin.on_page_content(html_question, mock_page, {}, None)
    
    # Verify the question HTML was generated (but no CSS yet)
    assert 'freetext-question' in content_result, "Should generate question HTML"
    assert 'textarea' in content_result, "Should include textarea"
    assert '<style' not in content_result, "CSS should NOT be in content (should be in head)"
    
    # Create a mock HTML page with head section
    full_page_html = f'''
<!DOCTYPE html>
<html>
<head>
    <title>Test Page</title>
</head>
<body>
{content_result}
</body>
</html>
'''
    
    # Now process the full page (this adds CSS to head)
    final_result = plugin.on_post_page(full_page_html, mock_page, {})
    
    # Verify CSS is properly added to head section
    assert '<style' in final_result, "Should include CSS in final page"
    assert '.freetext-question' in final_result, "Should include question styles"
    assert 'textarea' in final_result, "Should include textarea styles"
    assert 'char-count' in final_result, "Should include character counter styles"
    
    # Verify CSS is in head, not body
    head_section = final_result.split('</head>')[0]
    assert '<style' in head_section, "CSS should be in head section"


def test_css_generation_disabled():
    """Test that CSS is not generated when enable_css: false."""
    plugin = FreetextPlugin()
    plugin.load_config({'enable_css': False})
    
    # Create mock page
    mock_file = type('MockFile', (), {'src_path': 'test.md'})()
    mock_page = type('MockPage', (), {'file': mock_file})()
    
    html_question = '''
<div class="admonition freetext">
    <p class="admonition-title">Freetext</p>
    <p>question: CSS disabled test</p>
</div>
'''
    
    # First process the content (this generates questions)
    content_result = plugin.on_page_content(html_question, mock_page, {}, None)
    
    # Verify the question HTML was generated (but no CSS)
    assert 'freetext-question' in content_result, "Should generate question HTML"
    assert 'textarea' in content_result, "Should include textarea"
    assert '<style' not in content_result, "CSS should NOT be in content"
    
    # Create a mock HTML page with head section
    full_page_html = f'''
<!DOCTYPE html>
<html>
<head>
    <title>Test Page</title>
</head>
<body>
{content_result}
</body>
</html>
'''
    
    # Now process the full page (this should NOT add CSS when disabled)
    final_result = plugin.on_post_page(full_page_html, mock_page, {})
    
    # Verify CSS is NOT included anywhere
    assert '<style' not in final_result, "Should NOT include CSS when disabled"
    
    # But HTML structure should still be present
    assert 'class="freetext-question"' in final_result, "Should still have HTML structure"
    assert '<textarea' in final_result, "Should still have textarea element"


def test_dark_mode_css_variables():
    """Test that dark mode support uses Material Design CSS variables."""
    plugin = FreetextPlugin()
    plugin.load_config({'enable_css': True, 'dark_mode_support': True})
    
    # Create mock page
    mock_file = type('MockFile', (), {'src_path': 'test.md'})()
    mock_page = type('MockPage', (), {'file': mock_file})()
    
    html_question = '''
<div class="admonition freetext">
    <p class="admonition-title">Freetext</p>
    <p>question: Dark mode CSS test</p>
</div>
'''
    
    result = plugin.on_page_content(html_question, mock_page, {}, None)
    
    if '<style' in result:
        # Look for Material Design CSS variables
        assert 'var(--md-' in result, "Should use Material CSS variables for dark mode support"
        
        # Check for common Material variables
        material_vars = [
            'var(--md-default-bg-color)',
            'var(--md-default-fg-color)',
            'var(--md-code-bg-color)',
            'var(--md-primary-fg-color)'
        ]
        
        found_material_vars = any(var in result for var in material_vars)
        assert found_material_vars, "Should include at least one Material CSS variable"


def test_light_mode_only_css():
    """Test CSS without dark mode support uses static colors."""
    plugin = FreetextPlugin()
    plugin.load_config({'enable_css': True, 'dark_mode_support': False})
    
    # Create mock page
    mock_file = type('MockFile', (), {'src_path': 'test.md'})()
    mock_page = type('MockPage', (), {'file': mock_file})()
    
    html_question = '''
<div class="admonition freetext">
    <p class="admonition-title">Freetext</p>
    <p>question: Light mode only CSS test</p>
</div>
'''
    
    result = plugin.on_page_content(html_question, mock_page, {}, None)
    
    if '<style' in result:
        # Should not use CSS variables when dark mode disabled
        assert 'var(--md-' not in result, "Should NOT use Material CSS variables when dark mode disabled"
        
        # Should use static color values
        static_colors = ['#fff', '#000', 'white', 'black', 'rgb(', 'rgba(']
        found_static_colors = any(color in result for color in static_colors)
        assert found_static_colors, "Should use static color values when dark mode disabled"


def test_responsive_design_css():
    """Test that CSS includes responsive design elements."""
    plugin = FreetextPlugin()
    plugin.load_config({'enable_css': True})
    
    # Create mock page
    mock_file = type('MockFile', (), {'src_path': 'test.md'})()
    mock_page = type('MockPage', (), {'file': mock_file})()
    
    html_question = '''
<div class="admonition freetext">
    <p class="admonition-title">Freetext</p>
    <p>question: Responsive design test</p>
</div>
'''
    
    result = plugin.on_page_content(html_question, mock_page, {}, None)
    
    if '<style' in result:
        # Check for responsive design elements
        responsive_elements = [
            '@media',  # Media queries
            'max-width: 100%',  # Responsive width
            'box-sizing: border-box',  # Proper box model
            'min-height:',  # Flexible heights
        ]
        
        found_responsive = any(element in result for element in responsive_elements)
        assert found_responsive, "Should include responsive design elements"
        
        # Check textarea is responsive
        assert 'width: 100%' in result or 'max-width' in result, "Textarea should be responsive"


def test_custom_css_classes_in_generated_css():
    """Test that custom CSS classes are used in generated CSS."""
    plugin = FreetextPlugin()
    custom_config = {
        'enable_css': True,
        'question_class': 'my-custom-question',
        'answer_class': 'my-custom-answer',
        'container_class': 'my-custom-container'
    }
    plugin.load_config(custom_config)
    
    # Create mock page
    mock_file = type('MockFile', (), {'src_path': 'test.md'})()
    mock_page = type('MockPage', (), {'file': mock_file})()
    
    html_question = '''
<div class="admonition freetext">
    <p class="admonition-title">Freetext</p>
    <p>question: Custom CSS classes test</p>
</div>
'''
    
    result = plugin.on_page_content(html_question, mock_page, {}, None)
    
    if '<style' in result:
        # Verify custom classes are used in CSS
        assert '.my-custom-question' in result, "Should use custom question class in CSS"
        assert '.my-custom-answer' in result, "Should use custom answer class in CSS"
        assert '.my-custom-container' in result, "Should use custom container class in CSS"
        
        # Should not use default classes
        assert '.freetext-question' not in result, "Should NOT use default question class when custom is set"


def test_assessment_specific_css():
    """Test that assessment-specific CSS is generated for assessments."""
    plugin = FreetextPlugin()
    plugin.load_config({'enable_css': True})
    
    # Create mock page
    mock_file = type('MockFile', (), {'src_path': 'test.md'})()
    mock_page = type('MockPage', (), {'file': mock_file})()
    
    html_assessment = '''
<div class="admonition freetext-assessment">
    <p class="admonition-title">Freetext Assessment</p>
    <p>question: Assessment CSS test</p>
    <p>marks: 5</p>
    <hr>
    <p>question: Second question</p>
    <p>marks: 3</p>
</div>
'''
    
    result = plugin.on_page_content(html_assessment, mock_page, {}, None)
    
    if '<style' in result:
        # Check for assessment-specific styles
        assert '.freetext-assessment' in result, "Should include assessment container styles"
        assert 'marks-display' in result or 'marks' in result, "Should include marks display styles"
        assert 'total-marks' in result or 'assessment-header' in result, "Should include assessment header styles"


def test_character_counter_css():
    """Test that character counter CSS is included when enabled."""
    plugin = FreetextPlugin()
    plugin.load_config({'enable_css': True, 'show_character_count': True})
    
    # Create mock page
    mock_file = type('MockFile', (), {'src_path': 'test.md'})()
    mock_page = type('MockPage', (), {'file': mock_file})()
    
    html_question = '''
<div class="admonition freetext">
    <p class="admonition-title">Freetext</p>
    <p>question: Character counter CSS test</p>
</div>
'''
    
    result = plugin.on_page_content(html_question, mock_page, {}, None)
    
    if '<style' in result:
        # Check for character counter styles
        assert 'char-count' in result, "Should include character counter styles"
        assert 'font-size' in result, "Should style character counter text"
        assert 'text-align: right' in result or 'float: right' in result, "Should position character counter"


def test_css_not_duplicated():
    """Test that CSS is not duplicated when multiple questions exist."""
    plugin = FreetextPlugin()
    plugin.load_config({'enable_css': True})
    
    # Create mock page
    mock_file = type('MockFile', (), {'src_path': 'test.md'})()
    mock_page = type('MockPage', (), {'file': mock_file})()
    
    html_multiple_questions = '''
<div class="admonition freetext">
    <p class="admonition-title">Freetext</p>
    <p>question: First question</p>
</div>
<div class="admonition freetext">
    <p class="admonition-title">Freetext</p>
    <p>question: Second question</p>
</div>
<div class="admonition freetext">
    <p class="admonition-title">Freetext</p>
    <p>question: Third question</p>
</div>
'''
    
    result = plugin.on_page_content(html_multiple_questions, mock_page, {}, None)
    
    # Count occurrences of style tags
    style_count = result.count('<style')
    
    # Should only have one style block even with multiple questions
    assert style_count <= 1, f"Should have at most 1 style block, found {style_count}"
    
    if style_count == 1:
        # But should have styles for all question elements
        assert result.count('.freetext-question') >= 1, "Should include question styles"
        assert result.count('textarea') >= 1, "Should include textarea styles"
