"""
Test configuration processing and content stripping issues.

These tests specifically address the issues identified in the demo site:
1. Freetext admonition header embedded in question blocks
2. Missing marks blocks
3. Configuration leakage in rich formatted content (code blocks, images, diagrams)
"""

import pytest
from mkdocs_freetext.plugin import FreetextPlugin


class TestConfigurationProcessing:
    """Tests for configuration processing and stripping."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.plugin = FreetextPlugin()
        self.plugin.load_config({})
        
        # Create mock page object
        self.mock_file = type('MockFile', (), {'src_path': 'test.md'})()
        self.mock_page = type('MockPage', (), {'file': self.mock_file})()
    
    def test_admonition_title_removal(self):
        """Test that admonition titles are properly removed from all question types."""
        html_with_title = '''
<div class="admonition freetext">
    <p class="admonition-title">Freetext</p>
    <p>question: Simple question</p>
    <p>marks: 5</p>
</div>
'''
        
        result = self.plugin.on_page_content(html_with_title, self.mock_page, {}, None)
        
        assert 'admonition-title' not in result, "Admonition title class should be removed"
        assert '>Freetext<' not in result, "Freetext title text should be removed"
        assert 'Simple question' in result, "Question text should be preserved"
        assert '(5 marks)' in result, "Marks should be displayed"

    def test_config_stripping_with_rich_content(self):
        """Test that configuration is properly stripped when rich content is present."""
        html_with_rich_and_config = '''
<div class="admonition freetext">
    <p class="admonition-title">Freetext</p>
    <p>question: Analyze this code and diagram:</p>
    <p><img src="test.png" alt="Test Image" /></p>
    <pre class="mermaid"><code>graph TD; A-->B;</code></pre>
    <div class="language-python highlight"><pre><code>def test(): pass</code></pre></div>
    <p>marks: 10</p>
    <p>placeholder: Your analysis...</p>
    <p>show_answer: true</p>
    <p>answer: Sample answer</p>
</div>
'''
        
        result = self.plugin.on_page_content(html_with_rich_and_config, self.mock_page, {}, None)
        
        # Get the question content section (before textarea)
        if '<textarea' in result:
            question_section = result.split('<textarea')[0]
        else:
            question_section = result
        
        # Verify config is stripped from question text
        assert 'marks: 10' not in question_section, "Config should not appear in question text"
        assert 'placeholder: Your analysis...' not in question_section, "Config should not appear in question text"
        assert 'show_answer: true' not in question_section, "Config should not appear in question text"
        assert 'answer: Sample answer' not in question_section, "Config should not appear in question text"
        
        # Verify admonition title is removed
        assert 'admonition-title' not in result, "Admonition title should be stripped"
        assert 'Freetext</p>' not in result, "Freetext title should be stripped"
        
        # Verify rich content is preserved in question
        assert '<img src="test.png" alt="Test Image" />' in question_section, "Images should be preserved"
        assert 'mermaid' in question_section, "Mermaid should be preserved"
        assert 'language-python highlight' in question_section, "Code blocks should be preserved"
        
        # Verify marks badge is displayed
        assert '(10 marks)' in result, "Marks badge should be displayed"
        
        # Verify placeholder is applied to textarea
        if '<textarea' in result:
            assert 'placeholder="Your analysis..."' in result, "Placeholder should be in textarea"

    def test_marks_display_with_various_content_types(self):
        """Test that marks are properly displayed across different content types."""
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
''', '(7 marks)'),
            # Question with Mermaid
            ('''
<div class="admonition freetext">
    <p class="admonition-title">Freetext</p>
    <p>question: Question with diagram</p>
    <pre class="mermaid"><code>graph LR; X-->Y;</code></pre>
    <p>marks: 12</p>
</div>
''', '(12 marks)')
        ]
        
        for i, (html, expected_marks) in enumerate(test_cases):
            result = self.plugin.on_page_content(html, self.mock_page, {}, None)
            assert expected_marks in result, f"Should display {expected_marks} for test case {i+1}"

    def test_config_extraction_precedence(self):
        """Test that configuration is extracted correctly regardless of order."""
        # Config interspersed with rich content
        html_mixed_order = '''
<div class="admonition freetext">
    <p class="admonition-title">Freetext</p>
    <p>question: Mixed order test</p>
    <p>marks: 8</p>
    <p><img src="diagram.png" /></p>
    <p>placeholder: Enter response...</p>
    <pre class="mermaid"><code>graph LR; A-->B;</code></pre>
    <p>show_answer: true</p>
    <p>answer: Test answer</p>
</div>
'''
        
        result = self.plugin.on_page_content(html_mixed_order, self.mock_page, {}, None)
        
        # Config should be extracted and applied
        assert '(8 marks)' in result, "Marks should be displayed"
        if '<textarea' in result:
            assert 'placeholder="Enter response..."' in result, "Placeholder should be applied"
        
        # Rich content should remain in question
        question_section = result.split('<textarea')[0] if '<textarea' in result else result
        assert '<img src="diagram.png" />' in question_section, "Image should be preserved"
        assert 'mermaid' in question_section, "Mermaid should be preserved"
        
        # Config should not leak into question text
        assert 'marks: 8' not in question_section, "Config should not leak"
        assert 'placeholder: Enter response...' not in question_section, "Config should not leak"

    def test_assessment_config_stripping(self):
        """Test that assessment-level configuration is properly stripped."""
        html_assessment = '''
<div class="admonition freetext-assessment">
    <p class="admonition-title">Freetext-assessment</p>
    <p>title: Test Assessment</p>
    <p>shuffle: true</p>
    <p>question: First question with image</p>
    <p><img src="q1.png" /></p>
    <p>marks: 5</p>
    <hr />
    <p>question: Second question</p>
    <p>marks: 3</p>
</div>
'''
        
        result = self.plugin.on_page_content(html_assessment, self.mock_page, {}, None)
        
        # Assessment config should not leak into question content
        if 'class="assessment-question"' in result:
            first_question = result.split('class="assessment-question"')[1]
            assert 'title: Test Assessment' not in first_question, "Assessment config should not leak"
            assert 'shuffle: true' not in first_question, "Assessment config should not leak"
        
        # But should be applied (title displayed, shuffle attribute set)
        assert 'Test Assessment' in result, "Assessment title should be displayed"
        # Note: shuffle implementation may vary, but config should be processed

    def test_complex_markdown_preservation(self):
        """Test preservation of complex markdown content with config stripping."""
        html_complex = '''
<div class="admonition freetext">
    <p class="admonition-title">Freetext</p>
    <p>Analyze the following architecture:</p>
    <h3>System Overview</h3>
    <p><img src="architecture.png" alt="System Architecture" /></p>
    <pre class="mermaid"><code>
graph TB
    A[Frontend] --> B[API Gateway]
    B --> C[Service 1]
    B --> D[Service 2]
    </code></pre>
    <h4>Code Implementation</h4>
    <div class="language-python highlight">
        <pre><code>
def process_request(data):
    """Process incoming request"""
    return {"status": "processed", "data": data}
        </code></pre>
    </div>
    <p>Consider the <strong>scalability</strong> and <em>performance</em> implications.</p>
    <ul>
        <li>Load balancing</li>
        <li>Database optimization</li>
        <li>Caching strategies</li>
    </ul>
    ---
    <p>marks: 15, placeholder: Provide detailed analysis..., show_answer: true, answer: Consider horizontal scaling and implement Redis caching</p>
</div>
'''
        
        result = self.plugin.on_page_content(html_complex, self.mock_page, {}, None)
        
        # Get question content
        question_section = result.split('<textarea')[0] if '<textarea' in result else result
        
        # Verify all rich content is preserved
        assert '<h3>System Overview</h3>' in question_section, "Headers should be preserved"
        assert '<img src="architecture.png" alt="System Architecture" />' in question_section, "Images should be preserved"
        assert 'mermaid' in question_section and 'graph TB' in question_section, "Mermaid diagrams should be preserved"
        assert 'language-python highlight' in question_section, "Code blocks should be preserved"
        assert 'def process_request' in question_section, "Code content should be preserved"
        assert '<strong>scalability</strong>' in question_section, "Bold text should be preserved"
        assert '<em>performance</em>' in question_section, "Italic text should be preserved"
        assert '<ul>' in question_section and '<li>Load balancing</li>' in question_section, "Lists should be preserved"
        
        # Verify config is stripped from question content
        assert 'marks: 15' not in question_section, "Config should not appear in question"
        assert 'placeholder: Provide detailed analysis...' not in question_section, "Config should not appear in question"
        assert 'show_answer: true' not in question_section, "Config should not appear in question"
        assert 'answer: Consider horizontal scaling' not in question_section, "Config should not appear in question"
        
        # Verify config is applied
        assert '(15 marks)' in result, "Marks should be displayed"
        if '<textarea' in result:
            assert 'placeholder="Provide detailed analysis..."' in result, "Placeholder should be applied"

    def test_edge_case_empty_content(self):
        """Test handling of edge cases with minimal or empty content."""
        html_minimal = '''
<div class="admonition freetext">
    <p class="admonition-title">Freetext</p>
    <p>question: </p>
    <p>marks: 1</p>
</div>
'''
        
        result = self.plugin.on_page_content(html_minimal, self.mock_page, {}, None)
        
        # Should still process correctly even with empty question
        assert '(1 marks)' in result or '(1 mark)' in result, "Should handle minimal content"
        assert 'admonition-title' not in result, "Should remove admonition title even with minimal content"

    def test_config_line_variations(self):
        """Test different ways config can be specified in HTML."""
        # Test with extra whitespace, different formatting
        html_variations = '''
<div class="admonition freetext">
    <p class="admonition-title">Freetext</p>
    <p>question: Test question</p>
    <p>  marks:  10  </p>
    <p>placeholder:   Enter your answer here   </p>
    <p> show_answer : true </p>
</div>
'''
        
        result = self.plugin.on_page_content(html_variations, self.mock_page, {}, None)
        
        # Should handle whitespace variations correctly
        assert '(10 marks)' in result, "Should parse marks with extra whitespace"
        if '<textarea' in result:
            assert 'placeholder="Enter your answer here"' in result, "Should handle placeholder with whitespace"
        
        # Config should not leak
        question_section = result.split('<textarea')[0] if '<textarea' in result else result
        assert 'marks:  10' not in question_section, "Config with whitespace should not leak"


class TestContentLeakagePrevention:
    """Specific tests for preventing configuration leakage into content."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.plugin = FreetextPlugin()
        self.plugin.load_config({})
        
        # Create mock page object
        self.mock_file = type('MockFile', (), {'src_path': 'test.md'})()
        self.mock_page = type('MockPage', (), {'file': self.mock_file})()
    
    def test_no_config_leakage_in_code_blocks(self):
        """Ensure config doesn't leak when code blocks contain similar text."""
        html_with_code = '''
<div class="admonition freetext">
    <p class="admonition-title">Freetext</p>
    <p>question: What does this code do?</p>
    <div class="language-python highlight">
        <pre><code>
# Configuration example
marks = 100  # This is not a config line
placeholder = "Enter value"  # This is not a config line
question = "What is this?"  # This is not a config line
        </code></pre>
    </div>
    <p>marks: 5</p>
    <p>placeholder: Your answer...</p>
</div>
'''
        
        result = self.plugin.on_page_content(html_with_code, self.mock_page, {}, None)
        
        # Code content should be preserved
        question_section = result.split('<textarea')[0] if '<textarea' in result else result
        assert 'marks = 100' in question_section, "Code content should be preserved"
        assert 'placeholder = "Enter value"' in question_section, "Code content should be preserved"
        assert 'question = "What is this?"' in question_section, "Code content should be preserved"
        
        # But actual config should be stripped
        assert 'marks: 5' not in question_section, "Real config should be stripped"
        assert 'placeholder: Your answer...' not in question_section, "Real config should be stripped"
        
        # Config should be applied
        assert '(5 marks)' in result, "Marks should be applied"

    def test_no_config_leakage_in_images_alt_text(self):
        """Ensure config doesn't leak when images have config-like alt text."""
        html_with_images = '''
<div class="admonition freetext">
    <p class="admonition-title">Freetext</p>
    <p>question: Analyze this image:</p>
    <p><img src="test.png" alt="marks: 100, placeholder: test" /></p>
    <p>marks: 8</p>
    <p>placeholder: Real placeholder</p>
</div>
'''
        
        result = self.plugin.on_page_content(html_with_images, self.mock_page, {}, None)
        
        # Image should be preserved with its alt text
        question_section = result.split('<textarea')[0] if '<textarea' in result else result
        assert 'alt="marks: 100, placeholder: test"' in question_section, "Image alt text should be preserved"
        
        # Real config should be applied
        assert '(8 marks)' in result, "Real marks should be applied"
        if '<textarea' in result:
            assert 'placeholder="Real placeholder"' in result, "Real placeholder should be applied"
