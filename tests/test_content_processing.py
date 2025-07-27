"""
Test content processing and preservation of the MkDocs Free-Text Plugin.

This test suite verifies:
1. Rich markdown preservation in questions
2. Complex HTML structure handling
3. Link and image preservation
4. Code block and syntax highlighting preservation
5. Mixed content scenarios
"""

from mkdocs_freetext.plugin import FreetextPlugin


def test_markdown_formatting_preservation():
    """Test that rich markdown formatting is preserved in question text."""
    plugin = FreetextPlugin()
    plugin.load_config({})
    
    # Create mock page
    mock_file = type('MockFile', (), {'src_path': 'test.md'})()
    mock_page = type('MockPage', (), {'file': mock_file})()
    
    html_rich_markdown = '''
<div class="admonition freetext">
    <p class="admonition-title">Freetext</p>
    <p>question: Explain the difference between <strong>bold</strong> and <em>italic</em> text formatting.</p>
    <p>marks: 5</p>
</div>
'''
    
    result = plugin.on_page_content(html_rich_markdown, mock_page, {}, None)
    
    # Should preserve HTML formatting in question display
    assert '<strong>bold</strong>' in result, "Should preserve bold formatting"
    assert '<em>italic</em>' in result, "Should preserve italic formatting"
    assert 'textarea' in result, "Should still generate textarea"
    
    # Formatting should be in question display, not in form attributes
    import re
    textarea_match = re.search(r'<textarea[^>]*>', result)
    if textarea_match:
        textarea_tag = textarea_match.group(0)
        assert '<strong>' not in textarea_tag, "Formatting should not be in textarea attributes"
        assert '<em>' not in textarea_tag, "Formatting should not be in textarea attributes"


def test_placeholder_config_separation():
    """Test that configuration doesn't leak into placeholder text - CRITICAL BUG FIX."""
    plugin = FreetextPlugin()
    plugin.load_config({})
    
    # Create mock page
    mock_file = type('MockFile', (), {'src_path': 'test.md'})()
    mock_page = type('MockPage', (), {'file': mock_file})()
    
    # Test new --- separator syntax
    html_with_separator = '''
<div class="admonition freetext">
    <p class="admonition-title">Freetext</p>
    <p>What is the capital of France?</p>
    
    <hr />
    
    <p>placeholder: Enter your answer here...</p>
    <p>marks: 2</p>
    <p>show_answer: true</p>
    <p>answer: Paris is the capital of France.</p>
</div>
'''
    
    result = plugin.on_page_content(html_with_separator, mock_page, {}, None)
    
    # Extract the textarea placeholder attribute
    import re
    textarea_match = re.search(r'<textarea[^>]*placeholder="([^"]*)"[^>]*>', result)
    assert textarea_match, "Should find textarea with placeholder attribute"
    
    placeholder_text = textarea_match.group(1)
    
    # CRITICAL: Placeholder should ONLY contain the intended placeholder text
    assert placeholder_text == "Enter your answer here...", f"Placeholder should be clean, but got: {placeholder_text}"
    
    # Configuration should NOT leak into placeholder
    assert "marks:" not in placeholder_text, "Configuration should not appear in placeholder"
    assert "show_answer:" not in placeholder_text, "Configuration should not appear in placeholder"
    assert "answer:" not in placeholder_text, "Configuration should not appear in placeholder"
    assert "true" not in placeholder_text, "Configuration values should not appear in placeholder"
    assert "Paris" not in placeholder_text, "Answer text should not appear in placeholder"


def test_legacy_placeholder_config_separation():
    """Test that legacy syntax also doesn't leak config into placeholder."""
    plugin = FreetextPlugin()
    plugin.load_config({})
    
    # Create mock page
    mock_file = type('MockFile', (), {'src_path': 'test.md'})()
    mock_page = type('MockPage', (), {'file': mock_file})()
    
    # Test legacy syntax without --- separator
    html_legacy = '''
<div class="admonition freetext">
    <p class="admonition-title">Freetext</p>
    <p>question: What is the capital of France?</p>
    <p>placeholder: Type your answer...</p>
    <p>marks: 3</p>
</div>
'''
    
    result = plugin.on_page_content(html_legacy, mock_page, {}, None)
    
    # Extract the textarea placeholder attribute
    import re
    textarea_match = re.search(r'<textarea[^>]*placeholder="([^"]*)"[^>]*>', result)
    assert textarea_match, "Should find textarea with placeholder attribute"
    
    placeholder_text = textarea_match.group(1)
    
    # CRITICAL: Placeholder should ONLY contain the intended placeholder text
    assert placeholder_text == "Type your answer...", f"Legacy placeholder should be clean, but got: {placeholder_text}"
    
    # Configuration should NOT leak into placeholder
    assert "question:" not in placeholder_text, "Configuration should not appear in placeholder"
    assert "marks:" not in placeholder_text, "Configuration should not appear in placeholder"
    assert "What is the capital" not in placeholder_text, "Question text should not appear in placeholder"


def test_complex_config_placeholder_isolation():
    """Test placeholder isolation with complex configuration scenarios."""
    plugin = FreetextPlugin()
    plugin.load_config({})
    
    # Create mock page
    mock_file = type('MockFile', (), {'src_path': 'test.md'})()
    mock_page = type('MockPage', (), {'file': mock_file})()
    
    # Test complex configuration that might cause leakage
    html_complex = '''
<div class="admonition freetext">
    <p class="admonition-title">Freetext</p>
    <p>Analyze this complex algorithm and explain its time complexity:</p>
    
    <hr />
    
    <p>placeholder: Describe the algorithm analysis...</p>
    <p>marks: 10</p>
    <p>type: long</p>
    <p>show_answer: true</p>
    <p>answer: This algorithm has O(n log n) time complexity due to the sorting step.</p>
    <p>rows: 8</p>
</div>
'''
    
    result = plugin.on_page_content(html_complex, mock_page, {}, None)
    
    # Extract the textarea placeholder attribute
    import re
    textarea_match = re.search(r'<textarea[^>]*placeholder="([^"]*)"[^>]*>', result)
    assert textarea_match, "Should find textarea with placeholder attribute"
    
    placeholder_text = textarea_match.group(1)
    
    # CRITICAL: Placeholder should ONLY contain the intended placeholder text
    assert placeholder_text == "Describe the algorithm analysis...", f"Complex placeholder should be clean, but got: {placeholder_text}"
    
    # Ensure no configuration PATTERNS leak into placeholder (not just words that might naturally appear)
    config_patterns = ["marks:", "type:", "show_answer:", "answer:", "rows:", "O(n log n)", "sorting step", "true", "long", "10"]
    for pattern in config_patterns:
        assert pattern not in placeholder_text, f"Config pattern '{pattern}' should not appear in placeholder: {placeholder_text}"


def test_demo_page_exact_reproduction():
    """Test the exact scenario from the demo page that showed config leakage."""
    plugin = FreetextPlugin()
    plugin.load_config({})
    
    # Create mock page
    mock_file = type('MockFile', (), {'src_path': 'demo.md'})()
    mock_page = type('MockPage', (), {'file': mock_file})()
    
    # This is the EXACT HTML structure from the demo page
    html_demo_exact = '''
<div class="admonition freetext">
    <p class="admonition-title">Freetext</p>
    <p>What is the capital of France?</p>
    
    <hr />
    
    <p>placeholder: Enter your answer here...</p>
    <p>marks: 2</p>
    <p>show_answer: true</p>
    <p>answer: Paris is the capital of France.</p>
</div>
'''
    
    result = plugin.on_page_content(html_demo_exact, mock_page, {}, None)
    
    # This should work correctly with the <hr /> separator
    import re
    textarea_match = re.search(r'<textarea[^>]*placeholder="([^"]*)"[^>]*>', result)
    assert textarea_match, "Should find textarea with placeholder attribute"
    
    placeholder_text = textarea_match.group(1)
    
    # CRITICAL: This is the exact bug - placeholder should be clean
    assert placeholder_text == "Enter your answer here...", f"Demo page placeholder broken! Got: {placeholder_text}"
    
    # Verify question text appears correctly in display
    assert "What is the capital of France?" in result, "Question should be displayed"
    
    # Verify marks are shown
    assert "(2 marks)" in result, "Marks should be displayed"
    
    # Verify NO configuration text leaks into the textarea placeholder
    assert "marks:" not in placeholder_text, "Config should not leak into placeholder"
    assert "show_answer:" not in placeholder_text, "Config should not leak into placeholder"
    assert "Paris is the capital" not in placeholder_text, "Answer should not leak into placeholder"


def test_question_text_vs_placeholder_separation():
    """Test that question text and placeholder text remain properly separated."""
    plugin = FreetextPlugin()
    plugin.load_config({})
    
    # Create mock page
    mock_file = type('MockFile', (), {'src_path': 'test.md'})()
    mock_page = type('MockPage', (), {'file': mock_file})()
    
    html_separation_test = '''
<div class="admonition freetext">
    <p class="admonition-title">Freetext</p>
    <p>What is machine learning and how does it differ from traditional programming?</p>
    
    <hr />
    
    <p>placeholder: Explain machine learning concepts...</p>
    <p>marks: 5</p>
</div>
'''
    
    result = plugin.on_page_content(html_separation_test, mock_page, {}, None)
    
    # Question text should appear in the question display area
    assert "What is machine learning" in result, "Question text should be displayed"
    assert "traditional programming" in result, "Full question text should be displayed"
    
    # Extract placeholder from textarea
    import re
    textarea_match = re.search(r'<textarea[^>]*placeholder="([^"]*)"[^>]*>', result)
    assert textarea_match, "Should find textarea with placeholder"
    
    placeholder_text = textarea_match.group(1)
    
    # Placeholder should be clean and separate from question
    assert placeholder_text == "Explain machine learning concepts...", f"Expected clean placeholder, got: {placeholder_text}"
    assert "What is machine learning" not in placeholder_text, "Question text should not leak into placeholder"
    assert "traditional programming" not in placeholder_text, "Question text should not leak into placeholder"


def test_code_block_preservation():
    """Test that code blocks and syntax highlighting are preserved."""
    plugin = FreetextPlugin()
    plugin.load_config({})
    
    # Create mock page
    mock_file = type('MockFile', (), {'src_path': 'test.md'})()
    mock_page = type('MockPage', (), {'file': mock_file})()
    
    html_with_code = '''
<div class="admonition freetext">
    <p class="admonition-title">Freetext</p>
    <p>question: Explain this Python code:</p>
    <div class="highlight">
        <pre><code class="language-python">
def hello_world():
    print("Hello, World!")
    return True
        </code></pre>
    </div>
    <p>What does this function do?</p>
    <p>marks: 10</p>
</div>
'''
    
    result = plugin.on_page_content(html_with_code, mock_page, {}, None)
    
    # Should preserve code block structure
    assert 'class="highlight"' in result, "Should preserve syntax highlighting container"
    assert '<pre><code' in result, "Should preserve code block structure"
    assert 'language-python' in result, "Should preserve language specification"
    assert 'def hello_world()' in result, "Should preserve code content"
    assert 'print("Hello, World!")' in result, "Should preserve code content"
    
    # Should still generate form elements
    assert 'textarea' in result, "Should still generate textarea for answer"


def test_link_preservation():
    """Test that links in questions are preserved and functional."""
    plugin = FreetextPlugin()
    plugin.load_config({})
    
    # Create mock page
    mock_file = type('MockFile', (), {'src_path': 'test.md'})()
    mock_page = type('MockPage', (), {'file': mock_file})()
    
    html_with_links = '''
<div class="admonition freetext">
    <p class="admonition-title">Freetext</p>
    <p>question: Read <a href="https://example.com">this article</a> and 
       also check the <a href="/local/page.html">local documentation</a>.</p>
    <p>Summarize the key points from both sources.</p>
    <p>marks: 8</p>
</div>
'''
    
    result = plugin.on_page_content(html_with_links, mock_page, {}, None)
    
    # Should preserve links
    assert 'href="https://example.com"' in result, "Should preserve external links"
    assert 'href="/local/page.html"' in result, "Should preserve local links"
    assert '>this article<' in result, "Should preserve link text"
    assert '>local documentation<' in result, "Should preserve link text"
    
    # Links should be clickable (not in form attributes)
    assert '<a href=' in result, "Should have functioning anchor tags"


def test_image_preservation():
    """Test that images in questions are preserved with proper attributes."""
    plugin = FreetextPlugin()
    plugin.load_config({})
    
    # Create mock page
    mock_file = type('MockFile', (), {'src_path': 'test.md'})()
    mock_page = type('MockPage', (), {'file': mock_file})()
    
    html_with_images = '''
<div class="admonition freetext">
    <p class="admonition-title">Freetext</p>
    <p>question: Analyze the chart below:</p>
    <img src="/images/chart.png" alt="Sales Chart" width="400" height="300">
    <p>What trends do you observe in the data?</p>
    <p>marks: 6</p>
</div>
'''
    
    result = plugin.on_page_content(html_with_images, mock_page, {}, None)
    
    # Should preserve image element
    assert '<img' in result, "Should preserve image element"
    assert 'src="/images/chart.png"' in result, "Should preserve image source"
    assert 'alt="Sales Chart"' in result, "Should preserve alt text"
    assert 'width="400"' in result, "Should preserve width attribute"
    assert 'height="300"' in result, "Should preserve height attribute"


def test_list_preservation():
    """Test that ordered and unordered lists are preserved in questions."""
    plugin = FreetextPlugin()
    plugin.load_config({})
    
    # Create mock page
    mock_file = type('MockFile', (), {'src_path': 'test.md'})()
    mock_page = type('MockPage', (), {'file': mock_file})()
    
    html_with_lists = '''
<div class="admonition freetext">
    <p class="admonition-title">Freetext</p>
    <p>question: Consider these requirements:</p>
    <ul>
        <li>Must be scalable</li>
        <li>Should handle <strong>1000+ users</strong></li>
        <li>Must be secure</li>
    </ul>
    <p>And these steps:</p>
    <ol>
        <li>Design the architecture</li>
        <li>Implement core features</li>
        <li>Test thoroughly</li>
    </ol>
    <p>How would you approach this project?</p>
    <p>marks: 12</p>
</div>
'''
    
    result = plugin.on_page_content(html_with_lists, mock_page, {}, None)
    
    # Should preserve list structures
    assert '<ul>' in result, "Should preserve unordered list"
    assert '<ol>' in result, "Should preserve ordered list"
    assert '<li>' in result, "Should preserve list items"
    
    # Should preserve nested formatting in lists
    assert '<strong>1000+ users</strong>' in result, "Should preserve formatting within list items"
    
    # Should preserve list content
    assert 'Must be scalable' in result, "Should preserve list item content"
    assert 'Design the architecture' in result, "Should preserve ordered list content"


def test_table_preservation():
    """Test that tables in questions are preserved with proper structure."""
    plugin = FreetextPlugin()
    plugin.load_config({})
    
    # Create mock page
    mock_file = type('MockFile', (), {'src_path': 'test.md'})()
    mock_page = type('MockPage', (), {'file': mock_file})()
    
    html_with_table = '''
<div class="admonition freetext">
    <p class="admonition-title">Freetext</p>
    <p>question: Analyze the data in this table:</p>
    <table>
        <thead>
            <tr>
                <th>Product</th>
                <th>Sales Q1</th>
                <th>Sales Q2</th>
            </tr>
        </thead>
        <tbody>
            <tr>
                <td>Widget A</td>
                <td>1000</td>
                <td>1200</td>
            </tr>
            <tr>
                <td>Widget B</td>
                <td>800</td>
                <td>950</td>
            </tr>
        </tbody>
    </table>
    <p>What insights can you draw from this data?</p>
    <p>marks: 8</p>
</div>
'''
    
    result = plugin.on_page_content(html_with_table, mock_page, {}, None)
    
    # Should preserve table structure
    assert '<table>' in result, "Should preserve table element"
    assert '<thead>' in result, "Should preserve table header"
    assert '<tbody>' in result, "Should preserve table body"
    assert '<th>' in result, "Should preserve header cells"
    assert '<td>' in result, "Should preserve data cells"
    
    # Should preserve table content
    assert 'Product' in result, "Should preserve header content"
    assert 'Widget A' in result, "Should preserve cell content"
    assert '1000' in result, "Should preserve numeric data"


def test_mixed_complex_content():
    """Test handling of complex mixed content with multiple elements."""
    plugin = FreetextPlugin()
    plugin.load_config({})
    
    # Create mock page
    mock_file = type('MockFile', (), {'src_path': 'test.md'})()
    mock_page = type('MockPage', (), {'file': mock_file})()
    
    html_complex = '''
<div class="admonition freetext">
    <p class="admonition-title">Freetext</p>
    <p>question: <strong>Complex Question</strong> with multiple elements:</p>
    
    <h4>Background</h4>
    <p>Read this <a href="https://example.com">reference article</a> first.</p>
    
    <h4>Code Example</h4>
    <pre><code class="language-javascript">
function calculate(a, b) {
    return a + b;
}
    </code></pre>
    
    <h4>Requirements</h4>
    <ul>
        <li>Explain the <em>purpose</em> of this function</li>
        <li>Identify any <strong>potential issues</strong></li>
        <li>Suggest improvements</li>
    </ul>
    
    <p><img src="/diagram.png" alt="Flow diagram" width="300"></p>
    
    <p>marks: 15</p>
    <p>type: long</p>
    <p>max_chars: 1000</p>
</div>
'''
    
    result = plugin.on_page_content(html_complex, mock_page, {}, None)
    
    # Should preserve all structural elements
    assert '<h4>' in result, "Should preserve headings"
    assert '<strong>Complex Question</strong>' in result, "Should preserve inline formatting"
    assert 'href="https://example.com"' in result, "Should preserve links"
    assert '<pre><code' in result, "Should preserve code blocks"
    assert 'language-javascript' in result, "Should preserve syntax highlighting"
    assert '<ul>' in result and '<li>' in result, "Should preserve lists"
    assert '<img' in result and 'src="/diagram.png"' in result, "Should preserve images"
    
    # Should parse configuration correctly
    assert 'rows=' in result, "Should process row configuration"
    if 'max_chars' in result:
        assert '1000' in result, "Should apply character limit"
    
    # Should still generate form
    assert 'textarea' in result, "Should generate textarea despite complex content"


def test_nested_admonitions_handling():
    """Test handling when freetext contains other admonition-like structures."""
    plugin = FreetextPlugin()
    plugin.load_config({})
    
    # Create mock page
    mock_file = type('MockFile', (), {'src_path': 'test.md'})()
    mock_page = type('MockPage', (), {'file': mock_file})()
    
    html_nested_admonitions = '''
<div class="admonition freetext">
    <p class="admonition-title">Freetext</p>
    <p>question: Consider this note:</p>
    
    <div class="admonition note">
        <p class="admonition-title">Note</p>
        <p>This is important information to consider.</p>
    </div>
    
    <p>How does this note affect your analysis?</p>
    <p>marks: 5</p>
</div>
'''
    
    result = plugin.on_page_content(html_nested_admonitions, mock_page, {}, None)
    
    # Should preserve nested admonition
    assert 'class="admonition note"' in result, "Should preserve nested admonition class"
    assert 'This is important information' in result, "Should preserve nested content"
    
    # Should not try to process nested admonition as freetext
    nested_admonition_count = result.count('class="admonition note"')
    assert nested_admonition_count == 1, "Should preserve exactly one nested admonition"
    
    # Should still process the outer freetext
    assert 'textarea' in result, "Should process outer freetext admonition"


def test_mathematical_content_preservation():
    """Test preservation of mathematical notation and special symbols."""
    plugin = FreetextPlugin()
    plugin.load_config({})
    
    # Create mock page
    mock_file = type('MockFile', (), {'src_path': 'test.md'})()
    mock_page = type('MockPage', (), {'file': mock_file})()
    
    html_math = '''
<div class="admonition freetext">
    <p class="admonition-title">Freetext</p>
    <p>question: Solve for x: ax² + bx + c = 0</p>
    <p>Given: a ≠ 0, Δ = b² - 4ac ≥ 0</p>
    <p>Formula: x = (-b ± √Δ) / 2a</p>
    <p>Show your work step by step.</p>
    <p>marks: 10</p>
</div>
'''
    
    result = plugin.on_page_content(html_math, mock_page, {}, None)
    
    # Should preserve mathematical symbols
    mathematical_symbols = ['²', '≠', '≥', '±', '√', 'Δ']
    for symbol in mathematical_symbols:
        assert symbol in result, f"Should preserve mathematical symbol: {symbol}"
    
    # Should preserve mathematical expressions
    assert 'ax² + bx + c = 0' in result, "Should preserve quadratic equation"
    assert 'b² - 4ac' in result, "Should preserve discriminant formula"
    assert '(-b ± √Δ) / 2a' in result, "Should preserve quadratic formula"


def test_multilingual_content_support():
    """Test support for multilingual content in questions."""
    plugin = FreetextPlugin()
    plugin.load_config({})
    
    # Create mock page
    mock_file = type('MockFile', (), {'src_path': 'test.md'})()
    mock_page = type('MockPage', (), {'file': mock_file})()
    
    html_multilingual = '''
<div class="admonition freetext">
    <p class="admonition-title">Freetext</p>
    <p>question: Translate these phrases:</p>
    <ul>
        <li>English: "Hello, how are you?"</li>
        <li>Français: "Bonjour, comment allez-vous?"</li>
        <li>Español: "Hola, ¿cómo estás?"</li>
        <li>中文: "你好，你好吗？"</li>
        <li>العربية: "مرحبا، كيف حالك؟"</li>
        <li>Русский: "Привет, как дела?"</li>
    </ul>
    <p>Provide translations to German.</p>
    <p>marks: 12</p>
</div>
'''
    
    result = plugin.on_page_content(html_multilingual, mock_page, {}, None)
    
    # Should preserve all language content
    languages = [
        '"Hello, how are you?"',
        '"Bonjour, comment allez-vous?"',
        '"Hola, ¿cómo estás?"',
        '"你好，你好吗？"',
        '"مرحبا، كيف حالك؟"',
        '"Привет, как дела?"'
    ]
    
    for phrase in languages:
        assert phrase in result, f"Should preserve multilingual content: {phrase}"
    
    # Should handle right-to-left languages properly
    assert 'العربية' in result, "Should preserve Arabic text"
    assert 'مرحبا' in result, "Should preserve Arabic content"


def test_question_text_parsing():
    """Test that question text is parsed correctly without including configuration keys."""
    plugin = FreetextPlugin()
    plugin.load_config({})

    # Create mock page
    mock_file = type('MockFile', (), {'src_path': 'test.md'})()
    mock_page = type('MockPage', (), {'file': mock_file})()

    html_with_question = '''
<div class="admonition freetext">
    <p class="admonition-title">Freetext</p>
    <p>question: What is the capital of France?</p>
    <p>placeholder: Enter your answer here...</p>
    <p>marks: 2</p>
    <p>show_answer: true</p>
    <p>answer: Paris is the capital of France.</p>
</div>
'''

    result = plugin.on_page_content(html_with_question, mock_page, {}, None)

    # Ensure question text is parsed correctly
    assert 'What is the capital of France?' in result, "Question text should be parsed correctly"
    assert 'placeholder: Enter your answer here...' not in result, "Placeholder should not be part of question text"
    assert 'marks: 2' not in result, "Marks should not be part of question text"
    assert 'show_answer: true' not in result, "Show answer should not be part of question text"
    assert 'answer: Paris is the capital of France.' not in result, "Answer should not be part of question text"


def test_complex_content_preservation_with_config():
    """Test preservation of complex markdown content while stripping configuration."""
    plugin = FreetextPlugin()
    plugin.load_config({})
    
    # Create mock page
    mock_file = type('MockFile', (), {'src_path': 'test.md'})()
    mock_page = type('MockPage', (), {'file': mock_file})()
    
    html_complex = '''
<div class="admonition freetext">
    <p class="admonition-title">Freetext</p>
    <p>question: Analyze the following architecture:</p>
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
    <p>marks: 15</p>
    <p>placeholder: Provide detailed analysis...</p>
    <p>show_answer: true</p>
    <p>answer: Consider horizontal scaling, implement Redis caching...</p>
</div>
'''
    
    result = plugin.on_page_content(html_complex, mock_page, {}, None)
    
    # Get question content section
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


def test_config_leakage_prevention_in_code_blocks():
    """Ensure config doesn't leak when code blocks contain similar text."""
    plugin = FreetextPlugin()
    plugin.load_config({})
    
    # Create mock page
    mock_file = type('MockFile', (), {'src_path': 'test.md'})()
    mock_page = type('MockPage', (), {'file': mock_file})()
    
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
    
    result = plugin.on_page_content(html_with_code, mock_page, {}, None)
    
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


def test_mixed_content_order_independence():
    """Test that config is extracted correctly regardless of content order."""
    plugin = FreetextPlugin()
    plugin.load_config({})
    
    # Create mock page
    mock_file = type('MockFile', (), {'src_path': 'test.md'})()
    mock_page = type('MockPage', (), {'file': mock_file})()
    
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
    
    result = plugin.on_page_content(html_mixed_order, mock_page, {}, None)
    
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
