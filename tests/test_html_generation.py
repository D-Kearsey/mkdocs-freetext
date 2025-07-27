#!/usr/bin/env python3
"""
HTML Validation and Structure Test Suite

This test suite validates the HTML generation and structural integrity:
- HTML structure and validity
- CSS class assignments
- Element relationships
- Configuration processing
- Content transformation

Consolidates HTML-related testing functionality.
"""

import pytest
import re
import os
from unittest.mock import Mock
from mkdocs.structure.pages import Page
from mkdocs.structure.files import File
from mkdocs_freetext.plugin import FreetextPlugin


class TestHTMLGeneration:
    """Test suite for HTML generation and structure validation."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.plugin = FreetextPlugin()
        self.plugin.config = {
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
            'debug': False
        }
        self.plugin._debug_enabled = False
        
        # Initialize tracking attributes
        self.plugin.current_page_has_questions = False
        self.plugin.current_page_javascript = []
        self.plugin.current_page_dom_ready = []
        self.plugin.page_questions = {}
        self.plugin.page_javascript = {}
        
        # Create mock page
        mock_file = Mock(spec=File)
        mock_file.src_path = 'test.md'
        self.mock_page = Mock(spec=Page)
        self.mock_page.file = mock_file

    def test_basic_question_html_structure(self):
        """Test that basic question generates correct HTML structure."""
        input_html = '''
        <div class="admonition freetext">
            <p class="admonition-title">Question</p>
            <p>question: What is your name?</p>
        </div>
        '''
        
        result = self.plugin.on_page_content(input_html, self.mock_page, {}, {})
        
        # Check basic structure
        assert 'class="freetext-question"' in result, "Question container should have correct class"
        assert '<textarea' in result, "Should generate textarea element"
        assert 'name="answer_' in result, "Textarea should have answer name attribute"
        assert 'Submit Answer' in result, "Should have submit button"

    def test_question_configuration_processing(self):
        """Test that question configuration is properly processed."""
        input_html = '''
        <div class="admonition freetext">
            <p class="admonition-title">Question</p>
            <p>question: Test question
            type: long
            marks: 10
            placeholder: Custom placeholder
            rows: 5</p>
        </div>
        '''
        
        result = self.plugin.on_page_content(input_html, self.mock_page, {}, {})
        
        # Check configuration processing
        assert 'rows="5"' in result, "Custom rows should be applied"
        assert 'placeholder="Custom placeholder"' in result, "Custom placeholder should be applied"
        assert '10 marks' in result or 'marks: 10' in result, "Marks should be displayed"

    def test_character_count_html_generation(self):
        """Test character count HTML elements."""
        input_html = '''
        <div class="admonition freetext">
            <p class="admonition-title">Question</p>
            <p>question: Character count test
            show_character_count: true</p>
        </div>
        '''
        
        result = self.plugin.on_page_content(input_html, self.mock_page, {}, {})
        
        # Check character count elements
        assert 'character-count' in result, "Should have character count container"
        assert 'characters' in result, "Should have character count display"

    def test_sample_answer_display(self):
        """Test sample answer HTML generation."""
        input_html = '''
        <div class="admonition freetext">
            <p class="admonition-title">Question</p>
            <p>question: Sample answer test
            sample_answer: This is a sample answer
            show_answer: true</p>
        </div>
        '''
        
        result = self.plugin.on_page_content(input_html, self.mock_page, {}, {})
        
        # Check sample answer elements
        assert 'feedback_' in result, "Should have feedback container"
        # Sample answer is shown via JavaScript, so check for the trigger

    def test_css_classes_assignment(self):
        """Test that CSS classes are correctly assigned."""
        input_html = '''
        <div class="admonition freetext">
            <p class="admonition-title">Question</p>
            <p>question: CSS test</p>
        </div>
        '''
        
        result = self.plugin.on_page_content(input_html, self.mock_page, {}, {})
        
        # Check CSS classes
        assert 'freetext-question' in result, "Should have question class"
        assert 'freetext-answer' in result, "Should have answer class"

    def test_multiple_questions_structure(self):
        """Test HTML structure with multiple questions."""
        input_html = '''
        <div class="admonition freetext">
            <p class="admonition-title">Question</p>
            <p>question: First question</p>
        </div>
        <div class="admonition freetext">
            <p class="admonition-title">Question</p>
            <p>question: Second question</p>
        </div>
        '''
        
        result = self.plugin.on_page_content(input_html, self.mock_page, {}, {})
        
        # Check multiple question structure
        question_containers = result.count('class="freetext-question"')
        assert question_containers >= 2, "Should generate multiple question containers"
        
        # Check unique IDs
        answer_names = re.findall(r'name="answer_(\w+)"', result)
        assert len(set(answer_names)) == len(answer_names), "Each question should have unique ID"

    def test_assessment_block_processing(self):
        """Test assessment block HTML generation."""
        input_html = '''
        <div class="admonition assessment">
            <p class="admonition-title">Assessment</p>
            <p>This is an assessment block</p>
        </div>
        '''
        
        result = self.plugin.on_page_content(input_html, self.mock_page, {}, {})
        
        # Check assessment processing
        assert 'freetext-assessment' in result, "Should have assessment class"

    def test_html_escaping_and_sanitization(self):
        """Test that HTML content is properly escaped and sanitized."""
        input_html = '''
        <div class="admonition freetext">
            <p class="admonition-title">Question</p>
            <p>question: Test with <script>alert('xss')</script> content
            sample_answer: Answer with "quotes" and 'apostrophes'</p>
        </div>
        '''
        
        result = self.plugin.on_page_content(input_html, self.mock_page, {}, {})
        
        # Check that dangerous content is handled
        # Script tags in questions should be escaped/removed
        assert '<script>' not in result or '&lt;script&gt;' in result, "Script tags should be escaped"

    def test_content_preservation(self):
        """Test that non-freetext content is preserved."""
        input_html = '''
        <h1>Regular Header</h1>
        <p>Regular paragraph</p>
        <div class="admonition freetext">
            <p class="admonition-title">Question</p>
            <p>question: Test question</p>
        </div>
        <p>Another regular paragraph</p>
        '''
        
        result = self.plugin.on_page_content(input_html, self.mock_page, {}, {})
        
        # Check content preservation
        assert '<h1>Regular Header</h1>' in result, "Regular content should be preserved"
        assert 'Another regular paragraph' in result, "Content after questions should be preserved"

    def test_empty_and_malformed_input(self):
        """Test handling of empty and malformed input."""
        # Test empty input
        result_empty = self.plugin.on_page_content('', self.mock_page, {}, {})
        assert result_empty == '', "Empty input should return empty output"
        
        # Test malformed admonition
        malformed_html = '''
        <div class="admonition freetext">
            <p class="admonition-title">Question</p>
            <!-- Missing question content -->
        </div>
        '''
        
        result_malformed = self.plugin.on_page_content(malformed_html, self.mock_page, {}, {})
        # Should handle gracefully without crashing
        assert isinstance(result_malformed, str), "Should return string even for malformed input"


class TestConfigurationProcessing:
    """Test configuration parsing and processing."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.plugin = FreetextPlugin()
        self.plugin.config = {
            'question_class': 'custom-question',
            'default_answer_rows': 5,
            'default_placeholder': 'Default placeholder',
            'debug': False
        }

    def test_comma_separated_config_parsing(self):
        """Test parsing of comma-separated configuration values."""
        # This tests the _parse_comma_separated_config method
        test_cases = [
            ('value1, value2, value3', ['value1', 'value2', 'value3']),
            ('single_value', ['single_value']),
            ('value1,value2,value3', ['value1', 'value2', 'value3']),  # No spaces
            ('value1 , value2 , value3 ', ['value1', 'value2', 'value3']),  # Extra spaces
            ('', []),  # Empty string
        ]
        
        for input_value, expected in test_cases:
            result = self.plugin._parse_comma_separated_config(input_value)
            assert result == expected, f"Failed for input: {input_value}"

    def test_config_defaults_application(self):
        """Test that configuration defaults are properly applied."""
        mock_file = Mock()
        mock_file.src_path = 'test.md'
        mock_page = Mock()
        mock_page.file = mock_file
        
        input_html = '''
        <div class="admonition freetext">
            <p class="admonition-title">Question</p>
            <p>question: Test question</p>
        </div>
        '''
        
        result = self.plugin.on_page_content(input_html, mock_page, {}, {})
        
        # Check that defaults are applied
        assert 'custom-question' in result, "Custom question class should be applied"
        assert 'rows="5"' in result, "Default rows should be applied"


if __name__ == "__main__":
    # Run tests directly
    pytest.main([__file__, "-v"])
