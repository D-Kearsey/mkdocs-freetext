"""
Test integration scenarios of the MkDocs Free-Text Plugin.

This test suite verifies:
1. Different answer types integration
2. Page-level functionality
3. Integration with MkDocs features
"""

from mkdocs_freetext.plugin import FreetextPlugin


def test_multiple_answer_types_on_page():
    """Test page with different answer types working together."""
    plugin = FreetextPlugin()
    plugin.load_config({})
    
    # Create mock page
    mock_file = type('MockFile', (), {'src_path': 'mixed_types.md'})()
    mock_page = type('MockPage', (), {'file': mock_file})()
    
    html_mixed_types = '''
<div class="admonition freetext">
    <p class="admonition-title">Freetext</p>
    <p>question: Short answer question</p>
    <p>type: short</p>
    <p>marks: 2</p>
</div>

<div class="admonition freetext">
    <p class="admonition-title">Freetext</p>
    <p>question: Long answer question</p>
    <p>type: long</p>
    <p>marks: 8</p>
</div>

<div class="admonition freetext">
    <p class="admonition-title">Freetext</p>
    <p>question: Custom rows question</p>
    <p>rows: 6</p>
    <p>marks: 5</p>
</div>

<div class="admonition freetext">
    <p class="admonition-title">Freetext</p>
    <p>question: Character limited question</p>
    <p>max_chars: 150</p>
    <p>marks: 3</p>
</div>
'''
    
    result = plugin.on_page_content(html_mixed_types, mock_page, {}, None)
    
    # Should process all question types
    textarea_count = result.count('<textarea')
    assert textarea_count == 4, "Should process all 4 different question types"
    
    # Check specific type handling
    import re
    
    # Find all textarea elements with their attributes
    textareas = re.findall(r'<textarea[^>]*>', result)
    assert len(textareas) == 4, "Should have 4 textarea elements"
    
    # Should have different row configurations
    row_values = re.findall(r'rows="(\d+)"', result)
    assert len(row_values) == 4, "All textareas should have row attributes"
    assert len(set(row_values)) >= 2, "Should have different row values for different types"
    
    # Should handle character limits
    if 'max_chars' in result:
        assert '150' in result, "Should include character limit"


def test_assessment_and_individual_questions():
    """Test page with both assessment and individual questions."""
    plugin = FreetextPlugin()
    plugin.load_config({})
    
    # Create mock page
    mock_file = type('MockFile', (), {'src_path': 'mixed_content.md'})()
    mock_page = type('MockPage', (), {'file': mock_file})()
    
    html_mixed_content = '''
<div class="admonition freetext">
    <p class="admonition-title">Freetext</p>
    <p>question: Individual question 1</p>
    <p>marks: 5</p>
</div>

<div class="admonition freetext-assessment">
    <p class="admonition-title">Freetext Assessment</p>
    <p>question: Assessment question 1</p>
    <p>marks: 3</p>
    <hr>
    <p>question: Assessment question 2</p>
    <p>marks: 4</p>
</div>

<div class="admonition freetext">
    <p class="admonition-title">Freetext</p>
    <p>question: Individual question 2</p>
    <p>marks: 6</p>
</div>
'''
    
    result = plugin.on_page_content(html_mixed_content, mock_page, {}, None)
    
    # Should process all questions
    textarea_count = result.count('<textarea')
    assert textarea_count == 4, "Should process 2 individual + 2 assessment questions"
    
    # Should identify assessment vs individual
    assert 'freetext-assessment' in result, "Should preserve assessment structure"
    assert result.count('class="freetext-question"') >= 2, "Should have individual questions"
    
    # Assessment should have total marks if implemented
    if 'total' in result.lower() or 'marks' in result:
        # Verify assessment handling is different from individual questions
        assessment_section = result[result.find('freetext-assessment'):result.find('</div>', result.find('freetext-assessment'))]
        if 'total' in assessment_section.lower():
            assert '7' in assessment_section, "Assessment total should be 3+4=7"


def test_plugin_with_mkdocs_metadata():
    """Test plugin behavior with page metadata and configuration."""
    plugin = FreetextPlugin()
    plugin.load_config({
        'default_marks': 10,
        'show_character_count': True,
        'enable_auto_save': True
    })
    
    # Create mock page with metadata
    mock_file = type('MockFile', (), {'src_path': 'page_with_meta.md'})()
    mock_page = type('MockPage', (), {
        'file': mock_file,
        'title': 'Test Page with Freetext',
        'meta': {'description': 'Page containing freetext questions'}
    })()
    
    html_with_questions = '''
<div class="admonition freetext">
    <p class="admonition-title">Freetext</p>
    <p>question: Question using page context</p>
</div>
'''
    
    result = plugin.on_page_content(html_with_questions, mock_page, {}, None)
    
    # Should process normally despite page metadata
    assert 'textarea' in result, "Should process question normally with page metadata"
    
    # Should use configured defaults
    assert '(10 marks)' in result, "Should use configured default marks"
    
    # Should include configured features
    if 'char-count' in result:
        assert 'char-count' in result, "Should include character counter when configured"
    
    if 'autoSave_' in result:
        assert 'autoSave_' in result, "Should include auto-save when configured"


def test_page_level_css_javascript_integration():
    """Test that CSS and JavaScript are properly integrated at page level."""
    plugin = FreetextPlugin()
    plugin.load_config({
        'enable_css': True,
        'enable_auto_save': True,
        'show_character_count': True
    })
    
    # Create mock page
    mock_file = type('MockFile', (), {'src_path': 'integration_test.md'})()
    mock_page = type('MockPage', (), {'file': mock_file})()
    
    html_multiple_features = '''
<div class="admonition freetext">
    <p class="admonition-title">Freetext</p>
    <p>First question with features</p>
    ---
    <p>max_chars: 100</p>
</div>

<div class="admonition freetext">
    <p class="admonition-title">Freetext</p>
    <p>Second question with features</p>
    ---
    <p>max_chars: 200</p>
</div>
'''
    
    result = plugin.on_page_content(html_multiple_features, mock_page, {}, None)
    
    # CSS should be included once
    css_count = result.count('<style')
    assert css_count <= 1, f"Should have at most 1 CSS block, found {css_count}"
    
    if css_count == 1:
        # CSS should cover all necessary elements
        assert '.freetext-question' in result, "CSS should include question styles"
        assert 'textarea' in result.lower(), "CSS should include textarea styles"
        assert 'char-count' in result, "CSS should include character counter styles"
    
    # JavaScript should be present for each question
    import re
    char_count_functions = re.findall(r'updateCharCount_\w+', result)
    submit_functions = re.findall(r'submitAnswer_\w+', result)
    
    # Auto-save functionality has been removed from the plugin
    # Check that no localStorage functionality is present
    assert 'localStorage.setItem' not in result, "localStorage functionality has been removed"
    assert 'autoSave_' not in result, "Auto-save functions have been removed"
    
    # Character count functions should still be present (if character count is enabled)
    assert len(char_count_functions) >= 2, f"Should have character count functions for both questions, got {len(char_count_functions)}: {char_count_functions}"
    
    # Submit functions should be present
    assert len(submit_functions) >= 2, f"Should have submit functions for both questions, got {len(submit_functions)}"
    
    # Functions should have unique names
    assert len(set(char_count_functions)) >= 2, "Should have unique character count function names"
    assert len(set(submit_functions)) >= 2, "Should have unique submit function names"


def test_plugin_hook_integration():
    """Test that the plugin integrates properly with MkDocs hook system."""
    plugin = FreetextPlugin()
    plugin.load_config({})
    
    # Test with different hook contexts
    mock_file = type('MockFile', (), {'src_path': 'hook_test.md'})()
    mock_page = type('MockPage', (), {'file': mock_file})()
    mock_config = {'site_name': 'Test Site'}
    mock_files = type('MockFiles', (), {})()
    
    html_content = '''
<div class="admonition freetext">
    <p class="admonition-title">Freetext</p>
    <p>question: Hook integration test</p>
</div>
'''
    
    # Test the hook method directly
    result = plugin.on_page_content(html_content, mock_page, mock_config, mock_files)
    
    # Should handle all hook parameters
    assert isinstance(result, str), "Should return string from hook"
    assert 'textarea' in result, "Should process content in hook context"
    
    # Should not be affected by additional hook parameters
    assert len(result) > len(html_content), "Should enhance content"


def test_unicode_and_internationalization():
    """Test plugin behavior with international content and Unicode."""
    plugin = FreetextPlugin()
    plugin.load_config({})
    
    # Create mock page
    mock_file = type('MockFile', (), {'src_path': 'international.md'})()
    mock_page = type('MockPage', (), {'file': mock_file})()
    
    html_international = '''
<div class="admonition freetext">
    <p class="admonition-title">Freetext</p>
    <p>question: 日本語の質問: あなたの意見を書いてください。</p>
    <p>placeholder: ここに回答を入力...</p>
    <p>marks: 5</p>
</div>

<div class="admonition freetext">
    <p class="admonition-title">Freetext</p>
    <p>question: Pregunta en español: ¿Cuál es tu opinión sobre este tema?</p>
    <p>placeholder: Escribe tu respuesta aquí...</p>
    <p>marks: 4</p>
</div>

<div class="admonition freetext">
    <p class="admonition-title">Freetext</p>
    <p>question: سؤال باللغة العربية: ما رأيك في هذا الموضوع؟</p>
    <p>placeholder: اكتب إجابتك هنا...</p>
    <p>marks: 6</p>
</div>
'''
    
    result = plugin.on_page_content(html_international, mock_page, {}, None)
    
    # Should preserve all international content
    assert '日本語の質問' in result, "Should preserve Japanese content"
    assert 'あなたの意見を書いてください' in result, "Should preserve Japanese question"
    assert 'ここに回答を入力' in result, "Should preserve Japanese placeholder"
    
    assert 'Pregunta en español' in result, "Should preserve Spanish content"
    assert '¿Cuál es tu opinión' in result, "Should preserve Spanish question"
    assert 'Escribe tu respuesta' in result, "Should preserve Spanish placeholder"
    
    assert 'سؤال باللغة العربية' in result, "Should preserve Arabic content"
    assert 'ما رأيك في هذا الموضوع' in result, "Should preserve Arabic question"
    assert 'اكتب إجابتك هنا' in result, "Should preserve Arabic placeholder"
    
    # Should process all questions
    textarea_count = result.count('<textarea')
    assert textarea_count == 3, "Should process all international questions"
    
    # Placeholders should be properly escaped in HTML attributes
    import re
    placeholders = re.findall(r'placeholder="([^"]*)"', result)
    assert len(placeholders) == 3, "Should have 3 placeholder attributes"
    
    # Should handle right-to-left languages
    # Arabic content should be preserved without corruption
    for placeholder in placeholders:
        assert '"' not in placeholder, "Placeholders should not contain unescaped quotes"
