#!/usr/bin/env python3
"""Debug auto-save functionality."""

from mkdocs_freetext.plugin import FreetextPlugin

def test_autosave_patterns():
    """Test what patterns are actually generated for auto-save."""
    
    # Test with auto-save enabled
    plugin_enabled = FreetextPlugin()
    plugin_enabled.load_config({'enable_auto_save': True})
    
    # Test with auto-save disabled
    plugin_disabled = FreetextPlugin()
    plugin_disabled.load_config({'enable_auto_save': False})
    
    # Create mock page
    mock_file = type('MockFile', (), {'src_path': 'test.md'})()
    mock_page = type('MockPage', (), {'file': mock_file})()
    
    html_question = '''
<div class="admonition freetext">
    <p class="admonition-title">Freetext</p>
    <p>question: Auto-save test</p>
</div>
'''
    
    # Process with both configurations
    result_enabled = plugin_enabled.on_page_content(html_question, mock_page, {}, None)
    result_disabled = plugin_disabled.on_page_content(html_question, mock_page, {}, None)
    
    print("=== AUTO-SAVE ENABLED RESULT ===")
    print("Contains 'autoSave_':", 'autoSave_' in result_enabled)
    print("Contains 'localStorage.setItem':", 'localStorage.setItem' in result_enabled)
    print("Contains 'if (true)':", 'if (true)' in result_enabled)
    print("Contains 'if (false)':", 'if (false)' in result_enabled)
    
    print("\n=== AUTO-SAVE DISABLED RESULT ===")
    print("Contains 'autoSave_':", 'autoSave_' in result_disabled)
    print("Contains 'localStorage.setItem':", 'localStorage.setItem' in result_disabled)
    print("Contains 'if (true)':", 'if (true)' in result_disabled)
    print("Contains 'if (false)':", 'if (false)' in result_disabled)
    
    # Find the relevant JavaScript sections
    print("\n=== JAVASCRIPT ANALYSIS ===")
    
    # Look for auto-save functions in enabled result
    if 'autoSave_' in result_enabled:
        import re
        autosave_matches = re.findall(r'function autoSave_[^}]+}', result_enabled, re.DOTALL)
        if autosave_matches:
            print("Auto-save function (enabled):")
            print(autosave_matches[0])
    
    if 'autoSave_' in result_disabled:
        import re
        autosave_matches = re.findall(r'function autoSave_[^}]+}', result_disabled, re.DOTALL)
        if autosave_matches:
            print("Auto-save function (disabled):")
            print(autosave_matches[0])

if __name__ == "__main__":
    test_autosave_patterns()
