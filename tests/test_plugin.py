"""
Test suite for MkDocs Free-Text Plugin

Tests the core functionality of the plugin including:
- Question parsing and HTML generation
- Assessment creation and management
- Material theme integration
- Configuration handling
"""

import unittest
from unittest.mock import Mock, patch
import re

from mkdocs_freetext.plugin import FreetextPlugin


class TestFreetextPlugin(unittest.TestCase):
    """Test cases for the FreetextPlugin class."""
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.plugin = FreetextPlugin()
        self.plugin.config = {
            'question_class': 'freetext-question',
            'assessment_class': 'freetext-assessment',
            'enable_css': True,
            'shuffle_questions': False,
            'show_character_count': True
        }
        
    def test_plugin_initialization(self):
        """Test plugin initializes correctly."""
        self.assertIsInstance(self.plugin.page_questions, dict)
        
    def test_simple_question_parsing(self):
        """Test parsing a simple freetext question."""
        html_content = '''
        <p>question: What is the capital of France?</p>
        <p>marks: 2</p>
        <p>placeholder: Enter your answer...</p>
        '''
        
        config = self.plugin._parse_question_config_from_html(html_content)
        
        self.assertIn('What is the capital of France?', config['question'])
        self.assertEqual(config['marks'], 2)
        self.assertEqual(config['placeholder'], 'Enter your answer...')
        
    def test_question_with_mermaid_diagram(self):
        """Test parsing a question with embedded Mermaid diagram."""
        html_content = '''
        <p>question: Analyze this flowchart:</p>
        <pre class="mermaid"><code>graph TD
            A[Start] --> B[Process]
            B --> C[End]
        </code></pre>
        <p>marks: 5</p>
        '''
        
        config = self.plugin._parse_question_config_from_html(html_content)
        
        self.assertIn('Analyze this flowchart:', config['question'])
        self.assertIn('<pre class="mermaid">', config['question'])
        self.assertIn('graph TD', config['question'])
        self.assertEqual(config['marks'], 5)
        
    def test_question_with_code_block(self):
        """Test parsing a question with code block."""
        html_content = '''
        <p>question: Explain this Python code:</p>
        <div class="language-python"><pre><code>def hello():
    print("Hello, World!")
</code></pre></div>
        <p>marks: 3</p>
        '''
        
        config = self.plugin._parse_question_config_from_html(html_content)
        
        self.assertIn('Explain this Python code:', config['question'])
        self.assertIn('def hello():', config['question'])
        self.assertEqual(config['marks'], 3)
        
    def test_question_with_image(self):
        """Test parsing a question with image."""
        html_content = '''
        <p>question: Describe this image:</p>
        <p><img src="test.png" alt="Test image"></p>
        <p>marks: 2</p>
        '''
        
        config = self.plugin._parse_question_config_from_html(html_content)
        
        self.assertIn('Describe this image:', config['question'])
        self.assertIn('<img src="test.png"', config['question'])
        self.assertEqual(config['marks'], 2)
        
    def test_boolean_config_parsing(self):
        """Test parsing boolean configuration values."""
        html_content = '''
        <p>question: Test question</p>
        <p>show_answer: true</p>
        <p>marks: 1</p>
        '''
        
        config = self.plugin._parse_question_config_from_html(html_content)
        
        self.assertTrue(config['show_answer'])
        
        # Test false value
        html_content_false = '''
        <p>question: Test question</p>
        <p>show_answer: false</p>
        '''
        
        config_false = self.plugin._parse_question_config_from_html(html_content_false)
        self.assertFalse(config_false['show_answer'])
        
    def test_question_html_generation(self):
        """Test HTML generation for questions."""
        config = {
            'question': '<p>What is 2 + 2?</p>',
            'marks': 1,
            'placeholder': 'Enter answer...',
            'type': 'short',
            'show_answer': True,
            'answer': 'The answer is 4.'
        }
        
        html = self.plugin._generate_question_html(config, 'test123')
        
        # Check for essential elements
        self.assertIn('freetext-question', html)
        self.assertIn('What is 2 + 2?', html)
        self.assertIn('(1 marks)', html)
        self.assertIn('Enter answer...', html)
        self.assertIn('id="answer_test123"', html)
        self.assertIn('submitAnswer_test123', html)
        
    def test_assessment_html_generation(self):
        """Test HTML generation for assessments."""
        questions = [
            {
                'question': '<p>Question 1?</p>',
                'marks': 2,
                'placeholder': 'Answer 1...',
                'type': 'short',
                'show_answer': False,
                'answer': ''
            },
            {
                'question': '<p>Question 2?</p>',
                'marks': 3,
                'placeholder': 'Answer 2...',
                'type': 'long',
                'show_answer': True,
                'answer': 'Sample answer 2'
            }
        ]
        
        assessment_config = {
            'title': 'Test Assessment',
            'shuffle': False
        }
        
        html = self.plugin._generate_assessment_html(questions, 'assess123', assessment_config)
        
        # Check for essential elements
        self.assertIn('freetext-assessment', html)
        self.assertIn('Test Assessment', html)
        self.assertIn('Total: 5 marks', html)
        self.assertIn('Question 1?', html)
        self.assertIn('Question 2?', html)
        self.assertIn('submitAssessment_assess123', html)
        
    def test_css_generation(self):
        """Test CSS generation includes Material theme variables."""
        css = self.plugin._generate_css()
        
        # Check for Material theme CSS variables
        self.assertIn('var(--md-default-fg-color', css)
        self.assertIn('var(--md-code-bg-color', css)
        self.assertIn('var(--md-primary-fg-color', css)
        
        # Check for responsive design
        self.assertIn('@media (max-width: 768px)', css)
        
        # Check for proper CSS classes
        self.assertIn('.freetext-question', css)
        self.assertIn('.freetext-assessment', css)
        
    def test_admonition_processing(self):
        """Test processing of freetext admonitions."""
        html_input = '''
        <div class="admonition freetext">
            <p class="admonition-title">Question</p>
            <p>question: What is Python?</p>
            <p>marks: 5</p>
        </div>
        '''
        
        result = self.plugin._process_freetext_blocks_html(html_input)
        
        # Should replace admonition with question HTML
        self.assertNotIn('admonition freetext', result)
        self.assertIn('freetext-question', result)
        self.assertIn('What is Python?', result)
        
    def test_page_content_hook(self):
        """Test the on_page_content hook."""
        mock_page = Mock()
        mock_page.file.src_path = 'test.md'
        
        html_input = '''
        <div class="admonition freetext">
            <p>question: Test question</p>
        </div>
        '''
        
        result = self.plugin.on_page_content(html_input, mock_page, {}, [])
        
        # Should process the content and track the page
        self.assertTrue(self.plugin.page_questions['test.md'])
        self.assertIn('freetext-question', result)
        
    def test_configuration_defaults(self):
        """Test that default configuration values are correct."""
        plugin = FreetextPlugin()
        
        # Check config_scheme has expected defaults
        config_dict = {item[0]: item[1].default for item in plugin.config_scheme}
        
        self.assertEqual(config_dict['question_class'], 'freetext-question')
        self.assertEqual(config_dict['assessment_class'], 'freetext-assessment')
        self.assertTrue(config_dict['enable_css'])
        self.assertFalse(config_dict['shuffle_questions'])
        self.assertTrue(config_dict['show_character_count'])


class TestQuestionParsing(unittest.TestCase):
    """Specific tests for question content parsing."""
    
    def setUp(self):
        self.plugin = FreetextPlugin()
        
    def test_multi_line_question_content(self):
        """Test parsing questions with multiple content lines."""
        html_content = '''
        <p>question: This is a multi-line question.</p>
        <p>It continues here with more details.</p>
        <p>marks: 3</p>
        '''
        
        config = self.plugin._parse_question_config_from_html(html_content)
        
        self.assertIn('This is a multi-line question.', config['question'])
        self.assertIn('It continues here with more details.', config['question'])
        
    def test_mixed_content_question(self):
        """Test parsing questions with mixed content types."""
        html_content = '''
        <p>question: Analyze the following:</p>
        <pre class="mermaid"><code>graph LR
            A --> B
        </code></pre>
        <p>What does this diagram show?</p>
        <div class="language-python"><pre><code>print("test")</code></pre></div>
        <p>marks: 10</p>
        '''
        
        config = self.plugin._parse_question_config_from_html(html_content)
        
        # Should contain all content types
        self.assertIn('Analyze the following:', config['question'])
        self.assertIn('<pre class="mermaid">', config['question'])
        self.assertIn('What does this diagram show?', config['question'])
        self.assertIn('print("test")', config['question'])
        self.assertEqual(config['marks'], 10)


if __name__ == '__main__':
    unittest.main()
