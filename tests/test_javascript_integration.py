#!/usr/bin/env python3
"""
Comprehensive JavaScript Integration Test Suite

This test suite validates all JavaScript functionality in the MkDocs Free-Text Plugin:
- Function timing and ordering
- HTML-JavaScript consistency 
- Syntax error handling (triple quotes, escaping)
- Submit button functionality
- Character counting and auto-save features

Replaces and consolidates multiple scattered test files.
"""

import pytest
import re
import os
import pathlib
from unittest.mock import Mock
from mkdocs.structure.pages import Page
from mkdocs.structure.files import File
from mkdocs_freetext.plugin import FreetextPlugin


class TestJavaScriptIntegration:
    """Comprehensive test suite for JavaScript integration in Free-Text Plugin."""
    
    def setup_method(self):
        """Set up test fixtures before each test method."""
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
        
        # Initialize page tracking attributes
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

    def test_html_javascript_consistency(self):
        """Test that all HTML function calls have corresponding JavaScript definitions."""
        input_html = '''
        <div class="admonition freetext">
            <p class="admonition-title">Question</p>
            <p>What is your name?</p>
            ---
            <p>type: short, marks: 5</p>
        </div>
        '''
        
        # Process HTML content
        result_html = self.plugin.on_page_content(input_html, self.mock_page, {}, {})
        final_html = self.plugin.on_post_page(result_html, self.mock_page, {})
        
        # Extract function calls from HTML
        html_function_calls = set()
        
        # Find onclick attributes
        onclick_matches = re.findall(r'onclick="([^"]+)"', result_html)
        for match in onclick_matches:
            func_match = re.search(r'(\w+)\s*\(', match)
            if func_match:
                html_function_calls.add(func_match.group(1))
        
        # Find oninput attributes  
        oninput_matches = re.findall(r'oninput="([^"]+)"', result_html)
        for match in oninput_matches:
            func_matches = re.findall(r'(\w+)\s*\(', match)
            for func in func_matches:
                html_function_calls.add(func)
        
        # Extract JavaScript function definitions
        script_matches = re.findall(r'<script[^>]*>(.*?)</script>', final_html, re.DOTALL)
        javascript = '\n'.join(script_matches)
        
        js_function_definitions = set()
        func_matches = re.findall(r'function\s+(\w+)\s*\(', javascript)
        for func in func_matches:
            js_function_definitions.add(func)
        
        # Check consistency
        missing_functions = html_function_calls - js_function_definitions
        assert not missing_functions, f"Missing JavaScript functions: {missing_functions}"
        
        # Ensure we actually found some functions
        assert len(html_function_calls) > 0, "No function calls found in HTML"
        assert len(js_function_definitions) > 0, "No function definitions found in JavaScript"

    def test_javascript_function_timing(self):
        """Test that JavaScript functions are defined before they are called in HTML."""
        input_html = '''
        <div class="admonition freetext">
            <p class="admonition-title">Question</p>
            <p>Test question with character count</p>
            ---
            <p>show_character_count: true, enable_auto_save: true</p>
        </div>
        '''
        
        result_html = self.plugin.on_page_content(input_html, self.mock_page, {}, {})
        final_html = self.plugin.on_post_page(result_html, self.mock_page, {})
        
        # Check that JavaScript functions are defined before they are called
        # The plugin puts JavaScript in the body, but ensures functions are defined before calls
        
        # Find function definitions and calls
        first_oninput_pos = final_html.find('oninput=')
        first_function_pos = final_html.find('function ')
        
        if first_oninput_pos != -1 and first_function_pos != -1:
            assert first_function_pos < first_oninput_pos, "Functions should be defined before they're called"

    def test_javascript_syntax_validation(self):
        """Test that JavaScript syntax is valid and free of triple quote errors."""
        input_html = '''
        <div class="admonition freetext">
            <p class="admonition-title">Question</p>
            <p>Test with triple quotes</p>
            ---
            <p>answer: This is a """sample answer""" with quotes</p>
        </div>
        '''
        
        result_html = self.plugin.on_page_content(input_html, self.mock_page, {}, {})
        final_html = self.plugin.on_post_page(result_html, self.mock_page, {})
        
        # Extract JavaScript content
        script_matches = re.findall(r'<script[^>]*>(.*?)</script>', final_html, re.DOTALL)
        javascript = '\n'.join(script_matches)
        
        # Check for problematic triple quotes in JavaScript
        assert '"""' not in javascript, "JavaScript should not contain unescaped triple quotes"
        
        # Check that sample answer content is properly escaped
        if 'sample answer' in javascript:
            # Should be properly escaped without breaking JavaScript syntax
            assert 'This is a ' in javascript, "Sample answer content should be present"

    def test_submit_button_functionality(self):
        """Test that submit button generates correct JavaScript functionality."""
        input_html = '''
        <div class="admonition freetext">
            <p class="admonition-title">Question</p>
            <p>Submit test question</p>
            ---
            <p>show_answer: true, sample_answer: Test answer</p>
        </div>
        '''
        
        result_html = self.plugin.on_page_content(input_html, self.mock_page, {}, {})
        final_html = self.plugin.on_post_page(result_html, self.mock_page, {})
        
        # Check for submit button improvements
        assert "submitBtn.textContent = 'Submitted';" in final_html, "Button text should change to 'Submitted'"
        assert "submitBtn.title = 'Click to resubmit';" in final_html, "Button should get tooltip"
        
        # Check that generic success message is removed
        assert "Answer submitted successfully!" not in final_html, "Generic success message should be removed"
        
        # Check for sample answer display
        assert '<div class="answer-display"><strong>Sample Answer:</strong><br>' in final_html, "Sample answer display should be present"

    def test_character_count_functionality(self):
        """Test character counting JavaScript generation."""
        input_html = '''
        <div class="admonition freetext">
            <p class="admonition-title">Question</p>
            <p>Character count test</p>
            ---
            <p>show_character_count: true</p>
        </div>
        '''
        
        result_html = self.plugin.on_page_content(input_html, self.mock_page, {}, {})
        final_html = self.plugin.on_post_page(result_html, self.mock_page, {})
        
        # Check for character count elements and functions
        assert 'updateCharCount_' in final_html, "Character count function should be generated"
        assert 'oninput=' in final_html, "Character count should be triggered on input"
        assert 'characters' in final_html, "Character count display should be present"

    def test_multiple_questions_unique_ids(self):
        """Test that multiple questions generate unique function names."""
        input_html = '''
        <div class="admonition freetext">
            <p class="admonition-title">Question</p>
            <p>First question</p>
        </div>
        <div class="admonition freetext">
            <p class="admonition-title">Question</p>
            <p>Second question</p>
        </div>
        '''
        
        result_html = self.plugin.on_page_content(input_html, self.mock_page, {}, {})
        final_html = self.plugin.on_post_page(result_html, self.mock_page, {})
        
        # Find all function names
        submit_functions = re.findall(r'function submitAnswer_(\w+)', final_html)
        
        # Check that we have multiple unique functions
        assert len(submit_functions) >= 2, "Should generate multiple submit functions"
        assert len(set(submit_functions)) == len(submit_functions), "All function names should be unique"

    def test_dom_ready_javascript_ordering(self):
        """Test that DOM ready code is properly structured."""
        input_html = '''
        <div class="admonition freetext">
            <p class="admonition-title">Question</p>
            <p>DOM ready test</p>
            ---
            <p>enable_auto_save: true</p>
        </div>
        '''
        
        result_html = self.plugin.on_page_content(input_html, self.mock_page, {}, {})
        final_html = self.plugin.on_post_page(result_html, self.mock_page, {})
        
        # Check for DOM ready structure
        assert 'DOMContentLoaded' in final_html, "Should use DOM ready event"
        
        # Extract JavaScript content
        script_matches = re.findall(r'<script[^>]*>(.*?)</script>', final_html, re.DOTALL)
        javascript = '\n'.join(script_matches)
        
        # Check that auto-save restoration is in DOM ready
        if 'savedAnswer_' in javascript:
            assert 'DOMContentLoaded' in javascript, "Auto-save restoration should be in DOM ready"


class TestJavaScriptFileGeneration:
    """Test JavaScript generation from actual site files (if available)."""
    
    def setup_method(self):
        """Set up for file-based testing."""
        # Look for generated HTML files
        self.possible_html_files = [
            "mkdocs-freetext/documentation/site/demo/index.html",
            "../mkdocs-freetext/documentation/site/demo/index.html",
        ]
        
        self.html_file = None
        for file_path in self.possible_html_files:
            if os.path.exists(file_path):
                self.html_file = file_path
                break

    def test_generated_html_consistency(self):
        """Test consistency of actually generated HTML files."""
        if not self.html_file:
            pytest.skip("No generated HTML file found for testing")
        
        with open(self.html_file, 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        # Extract function calls from HTML attributes
        html_function_calls = set()
        
        # Find all function calls in event handlers
        for attr in ['onclick', 'oninput', 'onchange']:
            pattern = f'{attr}="([^"]*)"'
            matches = re.findall(pattern, html_content)
            for match in matches:
                func_matches = re.findall(r'(\w+)\s*\(', match)
                html_function_calls.update(func_matches)
        
        # Extract JavaScript function definitions
        script_matches = re.findall(r'<script[^>]*>(.*?)</script>', html_content, re.DOTALL)
        javascript = '\n'.join(script_matches)
        
        js_function_definitions = set(re.findall(r'function\s+(\w+)\s*\(', javascript))
        
        # Verify consistency
        missing_functions = html_function_calls - js_function_definitions
        assert not missing_functions, f"Missing JavaScript functions in generated file: {missing_functions}"
        
        # Verify no syntax errors
        assert '"""' not in javascript, "Generated JavaScript contains unescaped triple quotes"


if __name__ == "__main__":
    # Run tests directly
    pytest.main([__file__, "-v"])
