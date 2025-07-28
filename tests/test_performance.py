"""
Test performance and scalability of the MkDocs Free-Text Plugin.

This test suite verifies:
1. Performance with large numbers of questions
2. Memory usage optimization
3. Processing time benchmarks
"""

import time
from mkdocs_freetext.plugin import FreetextPlugin


def test_multiple_questions_performance():
    """Test performance when processing many questions on a single page."""
    plugin = FreetextPlugin()
    plugin.load_config({})
    
    # Create mock page
    mock_file = type('MockFile', (), {'src_path': 'test.md'})()
    mock_page = type('MockPage', (), {'file': mock_file})()
    
    # Generate HTML with many questions
    num_questions = 50
    questions_html = []
    
    for i in range(num_questions):
        question_html = f'''
<div class="admonition freetext">
    <p class="admonition-title">Freetext</p>
    <p>question: Question {i+1}: What is your understanding of topic {i+1}?</p>
    <p>marks: {(i % 5) + 1}</p>
    <p>type: {"long" if i % 2 == 0 else "short"}</p>
    <p>max_chars: {200 + (i * 10)}</p>
</div>
'''
        questions_html.append(question_html)
    
    large_html = '\n'.join(questions_html)
    
    # Measure processing time
    start_time = time.time()
    result = plugin.on_page_content(large_html, mock_page, {}, None)
    end_time = time.time()
    
    processing_time = end_time - start_time
    
    # Performance assertions
    assert processing_time < 5.0, f"Processing {num_questions} questions should take less than 5 seconds, took {processing_time:.2f}s"
    
    # Verify all questions were processed
    textarea_count = result.count('<textarea')
    assert textarea_count == num_questions, f"Should process all {num_questions} questions, found {textarea_count}"
    
    # Verify unique IDs were generated
    import re
    answer_ids = re.findall(r'id="answer_([^"]+)"', result)
    assert len(set(answer_ids)) == num_questions, f"All textareas should have unique IDs, found {len(set(answer_ids))} unique out of {len(answer_ids)} total"
    
    # Memory efficiency check - result shouldn't be excessively large
    result_size_mb = len(result.encode('utf-8')) / (1024 * 1024)
    assert result_size_mb < 10, f"Result size should be reasonable, got {result_size_mb:.2f}MB"


def test_large_assessment_performance():
    """Test performance with large assessment containing many questions."""
    plugin = FreetextPlugin()
    plugin.load_config({'shuffle_questions': True})
    
    # Create mock page
    mock_file = type('MockFile', (), {'src_path': 'test.md'})()
    mock_page = type('MockPage', (), {'file': mock_file})()
    
    # Generate large assessment
    num_questions = 100
    assessment_parts = ['<div class="admonition freetext-assessment">']
    assessment_parts.append('<p class="admonition-title">Freetext Assessment</p>')
    
    for i in range(num_questions):
        if i > 0:
            assessment_parts.append('<hr>')
        
        assessment_parts.extend([
            f'<p>question: Assessment Question {i+1}: Describe the importance of concept {i+1} in detail.</p>',
            f'<p>marks: {(i % 10) + 1}</p>',
            f'<p>type: {"long" if i % 3 == 0 else "short"}</p>'
        ])
    
    assessment_parts.append('</div>')
    large_assessment_html = '\n'.join(assessment_parts)
    
    # Measure processing time
    start_time = time.time()
    result = plugin.on_page_content(large_assessment_html, mock_page, {}, None)
    end_time = time.time()
    
    processing_time = end_time - start_time
    
    # Performance assertions
    assert processing_time < 10.0, f"Processing large assessment should take less than 10 seconds, took {processing_time:.2f}s"
    
    # Verify assessment was processed
    assert 'freetext-assessment' in result, "Should process assessment"
    assert 'data-shuffle="true"' in result, "Should include shuffle configuration"
    
    # Verify all questions in assessment
    textarea_count = result.count('<textarea')
    assert textarea_count == num_questions, f"Should process all {num_questions} assessment questions"
    
    # Check for total marks calculation
    if 'total-marks' in result or 'Total:' in result:
        # If total marks are calculated, verify it's reasonable
        expected_total = sum((i % 10) + 1 for i in range(num_questions))
        assert str(expected_total) in result, "Should calculate correct total marks"


def test_complex_content_processing_performance():
    """Test performance with questions containing complex rich content."""
    plugin = FreetextPlugin()
    plugin.load_config({'enable_css': True, 'show_character_count': True, 'enable_auto_save': True})
    
    # Create mock page
    mock_file = type('MockFile', (), {'src_path': 'test.md'})()
    mock_page = type('MockPage', (), {'file': mock_file})()
    
    # Generate questions with complex content
    num_questions = 20
    complex_questions = []
    
    for i in range(num_questions):
        complex_question = f'''
<div class="admonition freetext">
    <p class="admonition-title">Freetext</p>
    <p>question: <strong>Complex Question {i+1}</strong> - Analyze this scenario:</p>
    
    <h4>Background Information</h4>
    <p>Consider the following <a href="https://example{i}.com">reference materials</a>.</p>
    
    <table>
        <thead>
            <tr><th>Item</th><th>Value</th><th>Priority</th></tr>
        </thead>
        <tbody>
            <tr><td>Feature A</td><td>{i*10}</td><td>High</td></tr>
            <tr><td>Feature B</td><td>{i*20}</td><td>Medium</td></tr>
            <tr><td>Feature C</td><td>{i*30}</td><td>Low</td></tr>
        </tbody>
    </table>
    
    <div class="highlight">
        <pre><code class="language-python">
def process_data_{i}():
    items = []
    for j in range(10):
        items.append({{"name": f"item{{j}}", "value": j*{i}}})
    return sorted(items, key=lambda x: x["value"])
        </code></pre>
    </div>
    
    <ul>
        <li>Analyze the <em>efficiency</em> of this approach</li>
        <li>Identify potential <strong>performance bottlenecks</strong></li>
        <li>Suggest <code>optimization strategies</code></li>
    </ul>
    
    <p><img src="/charts/chart{i}.png" alt="Data visualization {i}" width="400"></p>
    
    <p>marks: {(i % 8) + 3}</p>
    <p>type: long</p>
    <p>max_chars: {1000 + (i * 100)}</p>
</div>
'''
        complex_questions.append(complex_question)
    
    complex_html = '\n'.join(complex_questions)
    
    # Measure processing time
    start_time = time.time()
    result = plugin.on_page_content(complex_html, mock_page, {}, None)
    end_time = time.time()
    
    processing_time = end_time - start_time
    
    # Performance assertions
    assert processing_time < 8.0, f"Processing complex content should take less than 8 seconds, took {processing_time:.2f}s"
    
    # Verify all complex elements were preserved
    assert result.count('<table>') == num_questions, "Should preserve all tables"
    assert result.count('<pre><code') == num_questions, "Should preserve all code blocks"
    assert result.count('<img') == num_questions, "Should preserve all images"
    assert result.count('<a href=') == num_questions, "Should preserve all links"
    
    # Verify all questions were processed into forms
    assert result.count('<textarea') == num_questions, "Should generate forms for all questions"
    
    # CSS should be included only once despite multiple questions
    css_count = result.count('<style')
    assert css_count <= 1, f"Should include CSS only once, found {css_count} style blocks"
    
    # JavaScript functions should be unique
    import re
    char_count_functions = re.findall(r'updateCharCount_\w+', result)
    
    # Auto-save functionality has been removed from the plugin
    assert len(set(char_count_functions)) == num_questions, "Character count functions should be unique"


def test_memory_efficiency():
    """Test memory efficiency by processing content and checking resource usage."""
    plugin = FreetextPlugin()
    plugin.load_config({})
    
    # Create mock page
    mock_file = type('MockFile', (), {'src_path': 'test.md'})()
    mock_page = type('MockPage', (), {'file': mock_file})()
    
    # Test with varying content sizes
    test_cases = [
        (10, "small"),    # 10 questions
        (50, "medium"),   # 50 questions  
        (100, "large"),   # 100 questions
    ]
    
    results = {}
    
    for num_questions, size_label in test_cases:
        # Generate questions
        questions = []
        for i in range(num_questions):
            question = f'''
<div class="admonition freetext">
    <p class="admonition-title">Freetext</p>
    <p>question: Question {i+1} for {size_label} test case</p>
    <p>marks: {(i % 5) + 1}</p>
</div>
'''
            questions.append(question)
        
        html_content = '\n'.join(questions)
        
        # Measure processing
        start_time = time.time()
        result = plugin.on_page_content(html_content, mock_page, {}, None)
        end_time = time.time()
        
        # Store results
        results[size_label] = {
            'input_size': len(html_content),
            'output_size': len(result),
            'processing_time': end_time - start_time,
            'questions_processed': result.count('<textarea')
        }
    
    # Verify linear scaling characteristics
    small = results['small']
    medium = results['medium']
    large = results['large']
    
    # Processing time should scale reasonably
    medium_time_ratio = medium['processing_time'] / small['processing_time']
    large_time_ratio = large['processing_time'] / small['processing_time']
    
    # Should not be exponential growth
    assert medium_time_ratio < 10, f"Medium processing time ratio should be reasonable: {medium_time_ratio:.2f}"
    assert large_time_ratio < 20, f"Large processing time ratio should be reasonable: {large_time_ratio:.2f}"
    
    # Output size should scale proportionally
    medium_size_ratio = medium['output_size'] / small['output_size']
    large_size_ratio = large['output_size'] / small['output_size']
    
    # Expect roughly linear scaling for output size
    assert 3 < medium_size_ratio < 8, f"Medium output size ratio should be proportional: {medium_size_ratio:.2f}"
    assert 7 < large_size_ratio < 15, f"Large output size ratio should be proportional: {large_size_ratio:.2f}"
    
    # All questions should be processed correctly
    assert small['questions_processed'] == 10, "Should process all small test questions"
    assert medium['questions_processed'] == 50, "Should process all medium test questions"
    assert large['questions_processed'] == 100, "Should process all large test questions"


def test_concurrent_processing_simulation():
    """Test behavior when simulating concurrent processing scenarios."""
    plugin1 = FreetextPlugin()
    plugin2 = FreetextPlugin()
    
    plugin1.load_config({'enable_css': True, 'show_character_count': True})
    plugin2.load_config({'enable_css': False, 'show_character_count': False})
    
    # Create mock pages
    mock_file1 = type('MockFile', (), {'src_path': 'page1.md'})()
    mock_page1 = type('MockPage', (), {'file': mock_file1})()
    
    mock_file2 = type('MockFile', (), {'src_path': 'page2.md'})()
    mock_page2 = type('MockPage', (), {'file': mock_file2})()
    
    # Different content for each "concurrent" processing
    html1 = '''
<div class="admonition freetext">
    <p class="admonition-title">Freetext</p>
    <p>question: First page question</p>
    <p>marks: 5</p>
</div>
'''
    
    html2 = '''
<div class="admonition freetext">
    <p class="admonition-title">Freetext</p>
    <p>question: Second page question</p>
    <p>marks: 8</p>
</div>
'''
    
    # Process "concurrently" (sequentially for testing)
    start_time = time.time()
    result1 = plugin1.on_page_content(html1, mock_page1, {}, None)
    result2 = plugin2.on_page_content(html2, mock_page2, {}, None)
    end_time = time.time()
    
    processing_time = end_time - start_time
    
    # Should complete quickly
    assert processing_time < 1.0, f"Concurrent processing simulation should be fast: {processing_time:.2f}s"
    
    # Results should be independent
    assert 'First page question' in result1, "Plugin 1 should process its content"
    assert 'Second page question' in result2, "Plugin 2 should process its content"
    assert 'First page question' not in result2, "Results should be independent"
    assert 'Second page question' not in result1, "Results should be independent"
    
    # Different configurations should produce different results
    css_in_result1 = '<style' in result1
    css_in_result2 = '<style' in result2
    
    if css_in_result1 or css_in_result2:
        # At least verify they're different if CSS is generated
        assert css_in_result1 != css_in_result2, "Different CSS configurations should produce different results"
