"""
Test error handling and edge cases of the MkDocs Free-Text Plugin.

This test suite verifies:
1. Malformed syntax handling
2. Missing required fields
3. Invalid configuration values
4. Edge cases and boundary conditions
"""

from mkdocs_freetext.plugin import FreetextPlugin


def test_malformed_freetext_syntax():
    """Test handling of malformed freetext admonition syntax."""
    plugin = FreetextPlugin()
    plugin.load_config({})
    
    # Create mock page
    mock_file = type('MockFile', (), {'src_path': 'test.md'})()
    mock_page = type('MockPage', (), {'file': mock_file})()
    
    # Test various malformed syntaxes
    malformed_cases = [
        # Missing question
        '''
<div class="admonition freetext">
    <p class="admonition-title">Freetext</p>
    <p>marks: 5</p>
</div>
''',
        # Incomplete HTML
        '''
<div class="admonition freetext">
    <p class="admonition-title">Freetext</p>
    <p>question: Test without closing
''',
        # Empty admonition
        '''
<div class="admonition freetext">
    <p class="admonition-title">Freetext</p>
</div>
''',
        # Invalid structure
        '''
<div class="admonition freetext">
    <p>question: No title element</p>
</div>
''',
    ]
    
    for i, malformed_html in enumerate(malformed_cases):
        try:
            result = plugin.on_page_content(malformed_html, mock_page, {}, None)
            
            # Should not crash and should return something
            assert isinstance(result, str), f"Case {i+1}: Should return string even with malformed input"
            
            # If it's too malformed, might return original HTML
            # If it's partially valid, might return modified HTML
            assert len(result) > 0, f"Case {i+1}: Should not return empty string"
            
        except Exception as e:
            # If it does throw an exception, it should be a reasonable one
            assert "question" in str(e).lower() or "html" in str(e).lower() or "parse" in str(e).lower(), \
                f"Case {i+1}: Exception should be related to parsing or question format: {e}"


def test_missing_required_question_field():
    """Test handling when question field is missing."""
    plugin = FreetextPlugin()
    plugin.load_config({})
    
    # Create mock page
    mock_file = type('MockFile', (), {'src_path': 'test.md'})()
    mock_page = type('MockPage', (), {'file': mock_file})()
    
    html_no_question = '''
<div class="admonition freetext">
    <p class="admonition-title">Freetext</p>
    <p>marks: 5</p>
    <p>type: short</p>
    <p>placeholder: Custom placeholder</p>
</div>
'''
    
    result = plugin.on_page_content(html_no_question, mock_page, {}, None)
    
    # Should handle gracefully - either return original or create with default
    assert isinstance(result, str), "Should return string when question is missing"
    
    # Should either be original HTML or contain some error indication
    if 'textarea' in result:
        # If it processed, should have some indication of missing question
        assert 'question' in result.lower() or 'missing' in result.lower() or len(result) > len(html_no_question)
    else:
        # If it didn't process, should return something close to original
        assert 'admonition freetext' in result, "Should preserve original structure when can't process"


def test_invalid_numeric_values():
    """Test handling of invalid numeric values in configuration."""
    plugin = FreetextPlugin()
    plugin.load_config({})
    
    # Create mock page
    mock_file = type('MockFile', (), {'src_path': 'test.md'})()
    mock_page = type('MockPage', (), {'file': mock_file})()
    
    invalid_numeric_cases = [
        # Invalid marks
        '''
<div class="admonition freetext">
    <p class="admonition-title">Freetext</p>
    <p>question: Test question</p>
    <p>marks: not_a_number</p>
</div>
''',
        # Negative marks
        '''
<div class="admonition freetext">
    <p class="admonition-title">Freetext</p>
    <p>question: Test question</p>
    <p>marks: -5</p>
</div>
''',
        # Invalid max_chars
        '''
<div class="admonition freetext">
    <p class="admonition-title">Freetext</p>
    <p>question: Test question</p>
    <p>max_chars: invalid</p>
</div>
''',
        # Zero or negative max_chars
        '''
<div class="admonition freetext">
    <p class="admonition-title">Freetext</p>
    <p>question: Test question</p>
    <p>max_chars: 0</p>
</div>
''',
        # Invalid rows
        '''
<div class="admonition freetext">
    <p class="admonition-title">Freetext</p>
    <p>question: Test question</p>
    <p>rows: not_valid</p>
</div>
''',
    ]
    
    for i, invalid_html in enumerate(invalid_numeric_cases):
        try:
            result = plugin.on_page_content(invalid_html, mock_page, {}, None)
            
            # Should not crash
            assert isinstance(result, str), f"Case {i+1}: Should handle invalid numeric values gracefully"
            
            # Should contain textarea (processed) or original HTML (fallback)
            assert 'textarea' in result or 'admonition freetext' in result, \
                f"Case {i+1}: Should either process or preserve original"
            
        except Exception as e:
            # If exception, should be about parsing/validation
            assert any(word in str(e).lower() for word in ['parse', 'invalid', 'number', 'value']), \
                f"Case {i+1}: Exception should be about invalid values: {e}"


def test_invalid_question_types():
    """Test handling of invalid question type values."""
    plugin = FreetextPlugin()
    plugin.load_config({})
    
    # Create mock page
    mock_file = type('MockFile', (), {'src_path': 'test.md'})()
    mock_page = type('MockPage', (), {'file': mock_file})()
    
    invalid_type_cases = [
        'invalid_type',
        'LONG',  # Wrong case
        'Short',  # Wrong case
        '123',   # Numeric
        '',      # Empty
        'long short',  # Multiple values
    ]
    
    for invalid_type in invalid_type_cases:
        html_invalid_type = f'''
<div class="admonition freetext">
    <p class="admonition-title">Freetext</p>
    <p>question: Test question</p>
    <p>type: {invalid_type}</p>
</div>
'''
        
        try:
            result = plugin.on_page_content(html_invalid_type, mock_page, {}, None)
            
            # Should handle gracefully
            assert isinstance(result, str), f"Should handle invalid type '{invalid_type}' gracefully"
            
            if 'textarea' in result:
                # If processed, should fall back to default type
                assert 'rows=' in result, "Should use default rows when type is invalid"
            
        except Exception as e:
            # Acceptable to throw exception for invalid type
            assert 'type' in str(e).lower() or 'invalid' in str(e).lower(), \
                f"Exception for invalid type '{invalid_type}' should be about type validation: {e}"


def test_extremely_long_content():
    """Test handling of extremely long question content."""
    plugin = FreetextPlugin()
    plugin.load_config({})
    
    # Create mock page
    mock_file = type('MockFile', (), {'src_path': 'test.md'})()
    mock_page = type('MockPage', (), {'file': mock_file})()
    
    # Create very long question text
    long_question = "A" * 10000  # 10KB question
    long_placeholder = "B" * 5000  # 5KB placeholder
    
    html_long_content = f'''
<div class="admonition freetext">
    <p class="admonition-title">Freetext</p>
    <p>question: {long_question}</p>
    <p>placeholder: {long_placeholder}</p>
</div>
'''
    
    try:
        result = plugin.on_page_content(html_long_content, mock_page, {}, None)
        
        # Should handle long content
        assert isinstance(result, str), "Should handle extremely long content"
        assert len(result) > 0, "Should return non-empty result"
        
        # Content should be preserved or truncated gracefully
        if 'textarea' in result:
            assert long_question[:1000] in result or 'question' in result, "Should preserve or handle long question text"
        
    except Exception as e:
        # Should not fail due to content length alone
        assert 'memory' not in str(e).lower(), f"Should not fail due to memory issues: {e}"


def test_special_characters_and_encoding():
    """Test handling of special characters and encoding issues."""
    plugin = FreetextPlugin()
    plugin.load_config({})
    
    # Create mock page
    mock_file = type('MockFile', (), {'src_path': 'test.md'})()
    mock_page = type('MockPage', (), {'file': mock_file})()
    
    special_chars_cases = [
        # HTML entities
        '''
<div class="admonition freetext">
    <p class="admonition-title">Freetext</p>
    <p>question: What is 2 &lt; 3 &amp; 3 &gt; 2?</p>
    <p>placeholder: Type &quot;answer&quot; here...</p>
</div>
''',
        # Unicode characters
        '''
<div class="admonition freetext">
    <p class="admonition-title">Freetext</p>
    <p>question: 数学问题: 2 + 2 = ?</p>
    <p>placeholder: 请输入答案...</p>
</div>
''',
        # Emoji and symbols
        '''
<div class="admonition freetext">
    <p class="admonition-title">Freetext</p>
    <p>question: What does 🎯 mean? ★☆☆</p>
    <p>placeholder: 📝 Write here...</p>
</div>
''',
        # Quotes and escaping
        '''
<div class="admonition freetext">
    <p class="admonition-title">Freetext</p>
    <p>question: He said "Hello 'world'" - explain this.</p>
    <p>placeholder: Use "quotes" carefully...</p>
</div>
''',
    ]
    
    for i, special_html in enumerate(special_chars_cases):
        try:
            result = plugin.on_page_content(special_html, mock_page, {}, None)
            
            # Should handle special characters
            assert isinstance(result, str), f"Case {i+1}: Should handle special characters"
            assert len(result) > 0, f"Case {i+1}: Should return non-empty result"
            
            # Check that HTML is properly escaped in attributes
            if 'textarea' in result:
                # Verify no unescaped quotes in attributes
                assert 'placeholder=""' not in result, f"Case {i+1}: Should not have empty attributes due to quote issues"
                
        except Exception as e:
            # Should not fail on encoding issues
            assert 'encoding' not in str(e).lower() and 'unicode' not in str(e).lower(), \
                f"Case {i+1}: Should not fail on encoding: {e}"


def test_nested_html_in_questions():
    """Test handling of nested HTML within question content."""
    plugin = FreetextPlugin()
    plugin.load_config({})
    
    # Create mock page
    mock_file = type('MockFile', (), {'src_path': 'test.md'})()
    mock_page = type('MockPage', (), {'file': mock_file})()
    
    html_nested = '''
<div class="admonition freetext">
    <p class="admonition-title">Freetext</p>
    <p>question: Explain this code: <code>print("Hello")</code> and this <strong>bold text</strong></p>
    <p>placeholder: Use <em>formatting</em> if needed</p>
</div>
'''
    
    try:
        result = plugin.on_page_content(html_nested, mock_page, {}, None)
        
        # Should handle nested HTML
        assert isinstance(result, str), "Should handle nested HTML in questions"
        
        if 'textarea' in result:
            # Should preserve or safely handle nested HTML
            # Either escaped in attributes or preserved in question display
            nested_elements = ['<code>', '<strong>', '<em>']
            found_nested = any(elem in result for elem in nested_elements)
            
            if found_nested:
                # If preserved, should be in safe context (not in attributes)
                assert 'placeholder="' in result, "Should have placeholder attribute"
                # Placeholder should not contain unescaped HTML
                import re
                placeholder_match = re.search(r'placeholder="([^"]*)"', result)
                if placeholder_match:
                    placeholder_content = placeholder_match.group(1)
                    assert '<' not in placeholder_content or '&lt;' in placeholder_content, \
                        "HTML in placeholder should be escaped"
        
    except Exception as e:
        # Should not fail due to nested HTML
        assert 'html' not in str(e).lower() or 'parse' in str(e).lower(), \
            f"Should handle nested HTML or provide parsing error: {e}"


def test_empty_configuration_values():
    """Test handling of empty configuration values."""
    plugin = FreetextPlugin()
    plugin.load_config({})
    
    # Create mock page
    mock_file = type('MockFile', (), {'src_path': 'test.md'})()
    mock_page = type('MockPage', (), {'file': mock_file})()
    
    html_empty_values = '''
<div class="admonition freetext">
    <p class="admonition-title">Freetext</p>
    <p>question: Valid question</p>
    <p>marks:</p>
    <p>type:</p>
    <p>placeholder:</p>
    <p>max_chars:</p>
</div>
'''
    
    try:
        result = plugin.on_page_content(html_empty_values, mock_page, {}, None)
        
        # Should handle empty values gracefully
        assert isinstance(result, str), "Should handle empty configuration values"
        
        if 'textarea' in result:
            # Should fall back to defaults for empty values
            assert 'rows=' in result, "Should use default rows when not specified"
            assert 'placeholder=' in result, "Should have some placeholder even if empty"
            
    except Exception as e:
        # Should not crash on empty values
        assert 'empty' in str(e).lower() or 'missing' in str(e).lower(), \
            f"Should handle empty values gracefully: {e}"
