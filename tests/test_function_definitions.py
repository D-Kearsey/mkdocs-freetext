"""
Test for JavaScript function definition and injection issues.

This test suite specifically targets the issue where JavaScript functions
are generated but not properly injected into the final HTML, causing
"function is not defined" errors in the browser.
"""

import pytest
import re
from mkdocs_freetext.plugin import FreetextPlugin


def test_complete_javascript_injection_workflow():
    """Test the complete workflow from content processing to final HTML injection."""
    plugin = FreetextPlugin()
    plugin.load_config({})
    
    # Create mock page
    mock_file = type('MockFile', (), {'src_path': 'test.md'})()
    mock_page = type('MockPage', (), {'file': mock_file})()
    
    # HTML with a simple question
    html_content = '''
<div class="admonition freetext">
    <p class="admonition-title">Freetext</p>
    <p>What is Python?</p>
    <hr>
    <p>type: short, show_answer: true, answer: Programming language</p>
</div>
'''
    
    # Step 1: Process content (should populate JavaScript arrays)
    processed_content = plugin.on_page_content(html_content, mock_page, {}, None)
    
    print(f"Step 1 - JavaScript functions collected: {len(plugin.current_page_javascript)}")
    print(f"Step 1 - DOM ready blocks collected: {len(plugin.current_page_dom_ready)}")
    
    # Extract question ID from processed content
    id_match = re.search(r'id="([^"]+)"', processed_content)
    assert id_match, "Should find question ID in processed content"
    question_id = id_match.group(1)
    print(f"Question ID: {question_id}")
    
    # Step 2: Create full HTML page
    full_html_page = f'''<!DOCTYPE html>
<html>
<head>
    <title>Test Page</title>
</head>
<body>
    {processed_content}
</body>
</html>'''
    
    # Step 3: Call on_post_page to inject JavaScript
    final_html = plugin.on_post_page(full_html_page, mock_page, {})
    
    # Step 4: Verify JavaScript injection
    print(f"Final HTML length: {len(final_html)}")
    
    # Check for script tags
    script_tags = re.findall(r'<script[^>]*>.*?</script>', final_html, re.DOTALL)
    print(f"Script tags found: {len(script_tags)}")
    
    # Check for specific functions
    submit_function = f"function submitAnswer_{question_id}()"
    char_count_function = f"function updateCharCount_{question_id}()"
    
    assert submit_function in final_html, f"Should find submit function: {submit_function}"
    print(f"✅ Found submit function: {submit_function}")
    
    # Check for DOM ready event
    assert 'DOMContentLoaded' in final_html, "Should find DOMContentLoaded event"
    print("✅ Found DOMContentLoaded event")
    
    # Check for onclick attributes in HTML elements
    onclick_pattern = rf'onclick="submitAnswer_{question_id}\(\)"'
    assert re.search(onclick_pattern, final_html), f"Should find onclick attribute: {onclick_pattern}"
    print(f"✅ Found onclick attribute: {onclick_pattern}")
    
    print("✅ Complete JavaScript injection workflow verified")


def test_function_name_id_matching():
    """Test that function names exactly match the HTML element IDs."""
    plugin = FreetextPlugin()
    plugin.load_config({})
    
    # Create mock page
    mock_file = type('MockFile', (), {'src_path': 'test.md'})()
    mock_page = type('MockPage', (), {'file': mock_file})()
    
    # HTML with long answer to test character count
    html_content = '''
<div class="admonition freetext">
    <p class="admonition-title">Freetext</p>
    <p>Explain object-oriented programming.</p>
    <hr>
    <p>type: long, max_chars: 500, show_answer: true, answer: OOP is a programming paradigm</p>
</div>
'''
    
    # Process content
    processed_content = plugin.on_page_content(html_content, mock_page, {}, None)
    
    # Extract all IDs and function calls from HTML
    element_ids = re.findall(r'id="([^"]+)"', processed_content)
    onclick_calls = re.findall(r'onclick="([^"]+)"', processed_content)
    oninput_calls = re.findall(r'oninput="([^"]+)"', processed_content)
    
    print(f"Element IDs found: {element_ids}")
    print(f"onclick calls found: {onclick_calls}")
    print(f"oninput calls found: {oninput_calls}")
    
    # Create full HTML and inject JavaScript
    full_html = f'<!DOCTYPE html><html><body>{processed_content}</body></html>'
    final_html = plugin.on_post_page(full_html, mock_page, {})
    
    # Extract function definitions from JavaScript
    function_defs = re.findall(r'function\s+(\w+)\s*\(', final_html)
    print(f"Function definitions found: {function_defs}")
    
    # Verify each onclick/oninput call has a corresponding function definition
    for onclick in onclick_calls:
        function_name = onclick.replace('()', '')
        assert function_name in function_defs, f"Missing function definition for: {function_name}"
        print(f"✅ Found matching function for onclick: {function_name}")
    
    for oninput in oninput_calls:
        function_name = oninput.replace('()', '')
        assert function_name in function_defs, f"Missing function definition for: {function_name}"
        print(f"✅ Found matching function for oninput: {function_name}")


def test_debug_javascript_generation():
    """Test and debug the JavaScript generation process step by step."""
    plugin = FreetextPlugin()
    plugin.load_config({})
    
    # Create mock page
    mock_file = type('MockFile', (), {'src_path': 'debug.md'})()
    mock_page = type('MockPage', (), {'file': mock_file})()
    
    # Initialize arrays (this happens in on_page_content)
    plugin.current_page_has_questions = False
    plugin.current_page_javascript = []
    plugin.current_page_dom_ready = []
    
    print("=== DEBUG: Initial state ===")
    print(f"current_page_javascript: {plugin.current_page_javascript}")
    print(f"current_page_dom_ready: {plugin.current_page_dom_ready}")
    
    # Simple question HTML
    html_content = '''
<div class="admonition freetext">
    <p class="admonition-title">Freetext</p>
    <p>Debug test question?</p>
    <hr>
    <p>answer: Debug answer</p>
</div>
'''
    
    # Process content step by step
    print("\n=== DEBUG: Processing content ===")
    processed_content = plugin.on_page_content(html_content, mock_page, {}, None)
    
    print(f"After processing - JavaScript functions: {len(plugin.current_page_javascript)}")
    print(f"After processing - DOM ready blocks: {len(plugin.current_page_dom_ready)}")
    
    if plugin.current_page_javascript:
        print("\nJavaScript functions collected:")
        for i, js in enumerate(plugin.current_page_javascript):
            print(f"Function {i+1}:")
            print(js[:200] + "..." if len(js) > 200 else js)
    
    if plugin.current_page_dom_ready:
        print("\nDOM ready blocks collected:")
        for i, dom_js in enumerate(plugin.current_page_dom_ready):
            print(f"DOM block {i+1}:")
            print(dom_js[:200] + "..." if len(dom_js) > 200 else dom_js)
    
    # Check page JavaScript storage
    print(f"\n=== DEBUG: Page JavaScript storage ===")
    if hasattr(plugin, 'page_javascript') and mock_page.file.src_path in plugin.page_javascript:
        stored_js = plugin.page_javascript[mock_page.file.src_path]
        print(f"Stored functions: {len(stored_js.get('functions', []))}")
        print(f"Stored DOM ready: {len(stored_js.get('dom_ready', []))}")
    else:
        print("No JavaScript stored for this page")
    
    # Test on_post_page
    print(f"\n=== DEBUG: on_post_page processing ===")
    full_html = f'<!DOCTYPE html><html><body>{processed_content}</body></html>'
    final_html = plugin.on_post_page(full_html, mock_page, {})
    
    # Check final injection
    has_script_tags = '<script>' in final_html
    has_functions = 'function submitAnswer_' in final_html
    has_dom_ready = 'DOMContentLoaded' in final_html
    
    print(f"Final HTML has script tags: {has_script_tags}")
    print(f"Final HTML has submit functions: {has_functions}")
    print(f"Final HTML has DOM ready: {has_dom_ready}")
    
    # Extract and show injected JavaScript
    if has_script_tags:
        script_content = re.search(r'<script[^>]*>(.*?)</script>', final_html, re.DOTALL)
        if script_content:
            js_content = script_content.group(1)
            print(f"\nInjected JavaScript (first 500 chars):")
            print(js_content[:500])
    
    assert has_script_tags, "Final HTML should contain script tags"
    assert has_functions, "Final HTML should contain function definitions"
    assert has_dom_ready, "Final HTML should contain DOM ready events"
    
    print("✅ Debug test completed successfully")


def test_real_world_scenario():
    """Test with HTML that matches the actual demo site structure."""
    plugin = FreetextPlugin()
    plugin.load_config({})
    
    # Create mock page that matches test-site structure
    mock_file = type('MockFile', (), {'src_path': 'index.md'})()
    mock_page = type('MockPage', (), {'file': mock_file})()
    
    # HTML that matches the demo site structure
    demo_html = '''
<h2 id="simple-short-answer">Simple Short Answer</h2>
<div class="admonition freetext">
    <p class="admonition-title">Freetext</p>
    <p>question: What is your favorite programming language?</p>
    <p>type: short</p>
    <p>show_answer: true</p>
    <p>marks: 0</p>
    <p>placeholder: Enter your favorite language...</p>
    <p>answer: Any programming language</p>
</div>

<h2 id="long-answer-with-character-limit">Long Answer with Character Limit</h2>
<div class="admonition freetext">
    <p class="admonition-title">Freetext</p>
    <p>question: Explain the concept of object-oriented programming and its main principles.</p>
    <p>type: long</p>
    <p>max_chars: 500</p>
    <p>show_answer: true</p>
    <p>placeholder: Enter your explanation here...</p>
    <p>answer: Object-oriented programming (OOP) is a programming paradigm based on objects.</p>
</div>
'''
    
    print("=== REAL WORLD TEST ===")
    
    # Process content
    processed_content = plugin.on_page_content(demo_html, mock_page, {}, None)
    
    print(f"JavaScript functions generated: {len(plugin.current_page_javascript)}")
    print(f"DOM ready blocks generated: {len(plugin.current_page_dom_ready)}")
    
    # Create full page structure similar to MkDocs output
    full_page = f'''<!doctype html>
<html lang="en" class="no-js">
<head>
    <meta charset="utf-8">
    <title>Test Page</title>
</head>
<body>
    <div class="md-container">
        <main class="md-main">
            <div class="md-content">
                <article class="md-content__inner md-typeset">
                    {processed_content}
                </article>
            </div>
        </main>
    </div>
</body>
</html>'''
    
    # Inject JavaScript
    final_html = plugin.on_post_page(full_page, mock_page, {})
    
    # Extract question IDs from final HTML
    question_ids = re.findall(r'data-question-id="([^"]+)"', final_html)
    print(f"Question IDs in final HTML: {question_ids}")
    
    # Check each question has its functions
    for question_id in question_ids:
        submit_func = f"function submitAnswer_{question_id}()"
        assert submit_func in final_html, f"Missing submit function for {question_id}"
        print(f"✅ Found submit function for {question_id}")
        
        # Check for onclick in HTML
        onclick_pattern = rf'onclick="submitAnswer_{question_id}\(\)"'
        assert re.search(onclick_pattern, final_html), f"Missing onclick for {question_id}"
        print(f"✅ Found onclick attribute for {question_id}")
    
    # Check for character count functions (for long answers)
    long_answer_functions = re.findall(r'function updateCharCount_([^(]+)\(', final_html)
    print(f"Character count functions found: {len(long_answer_functions)}")
    
    print("✅ Real world scenario test passed")


if __name__ == "__main__":
    print("🧪 Running JavaScript Function Definition Tests...")
    print()
    
    try:
        test_complete_javascript_injection_workflow()
        print()
        test_function_name_id_matching()
        print()
        test_debug_javascript_generation()
        print()
        test_real_world_scenario()
        
        print()
        print("🎉 All JavaScript function definition tests passed!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
