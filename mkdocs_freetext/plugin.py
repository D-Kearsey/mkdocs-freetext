"""
MkDocs Free-Text Plugin

A comprehensive plugin for adding free-text input questions
and assessments to MkDocs documentation.
"""

import os
import re
import uuid
import random
import json
import markdown
import logging
from mkdocs.config import config_options
from mkdocs.plugins import BasePlugin
from mkdocs.structure.pages import Page

logger = logging.getLogger(__name__)


class FreetextPlugin(BasePlugin):
    """
    MkDocs plugin to add interactive free-text questions and assessments.
    """

    config_scheme = (
        ('question_class', config_options.Type(str, default='freetext-question')),
        ('assessment_class', config_options.Type(str, default='freetext-assessment')),
        ('answer_class', config_options.Type(str, default='freetext-answer')),
        ('container_class', config_options.Type(str, default='freetext-container')),
        ('enable_css', config_options.Type(bool, default=True)),
        ('dark_mode_support', config_options.Type(bool, default=True)),
        ('shuffle_questions', config_options.Type(bool, default=False)),
        ('show_character_count', config_options.Type(bool, default=True)),
        ('enable_auto_save', config_options.Type(bool, default=True)),
        ('default_answer_rows', config_options.Type(int, default=3)),
        ('default_long_answer_rows', config_options.Type(int, default=6)),
        ('default_placeholder', config_options.Type(str, default='Enter your answer...')),
        ('default_marks', config_options.Type(int, default=0)),
        ('default_show_answer', config_options.Type(bool, default=True)),
        ('default_question_type', config_options.Type(str, default='short')),
        ('debug', config_options.Type(bool, default=False)),
        ('debug_output_dir', config_options.Type(str, default=None)),
    )

    def __init__(self):
        super().__init__()
        self.page_questions = {}  # Track questions per page
        self.page_javascript = {}  # Track JavaScript per page for consolidation

    def _get_expected_type_hint(self, key):
        """Return expected type for configuration keys."""
        type_hints = {
            'marks': 'integer (e.g., 5)',
            'rows': 'integer (e.g., 3)',
            'show_answer': 'boolean (true/false)',
            'type': 'string (short/long)'
        }
        return type_hints.get(key, 'string')

    def _validate_config(self):
        """Validate plugin configuration and log issues."""
        issues = []
        
        if self.config.get('default_answer_rows', 0) < 1:
            issues.append("default_answer_rows must be at least 1")
        
        if self.config.get('default_long_answer_rows', 0) < 1:
            issues.append("default_long_answer_rows must be at least 1")
        
        valid_types = ['short', 'long']
        if self.config.get('default_question_type') not in valid_types:
            issues.append(f"default_question_type must be one of: {valid_types}")
        
        for issue in issues:
            logger.error(f"Configuration error: {issue}")
        
        return len(issues) == 0

    def on_config(self, config):
        """Called once after config is loaded"""
        if self.config.get('debug', False):
            logger.setLevel(logging.DEBUG)
            logger.info("FreetextPlugin debug mode enabled")
        else:
            logger.setLevel(logging.INFO)
        
        # Validate configuration
        if not self._validate_config():
            logger.error("Plugin configuration contains errors. Please fix them before proceeding.")
        
        logger.info("FreetextPlugin initialized successfully")
        return config

    def _process_markdown_content(self, content):
        """Process content that is already in HTML format from MkDocs processing."""
        # Since we're now working with on_page_content hook, the content is already HTML
        # Just return it as-is since it's already been processed by MkDocs including
        # Mermaid diagrams, images, code blocks, etc.
        return content

    def on_page_content(self, html, page, config, files, **kwargs):
        """
        Process HTML content to convert freetext question and assessment syntax.
        This hook runs after markdown processing, so Mermaid diagrams will already be rendered.
        """
        # Initialize questions found for this page
        self.current_page_has_questions = False
        self.current_page_javascript = []  # Collect all JavaScript for this page
        self.current_page_dom_ready = []   # Collect all DOM ready code for this page
        
        logger.debug(f"Processing page: {page.file.src_path}")
        logger.debug(f"Input HTML length: {len(html)}")
        
        # Save original HTML for comparison
        original_html = html
        
        # Look for freetext admonitions in the HTML
        import re
        freetext_matches = re.findall(r'<div class="admonition freetext[^"]*"[^>]*>', html)
        logger.debug(f"Found {len(freetext_matches)} freetext admonition(s) on page {page.file.src_path}")
        
        # Process freetext assessment blocks FIRST (before individual questions)
        html_before = html
        html = self._process_assessment_blocks_html(html)
        
        # Process individual freetext question blocks AFTER assessments
        html = self._process_freetext_blocks_html(html)
        
        # Check if anything changed and write debug files
        if html != html_before:
            logger.info(f"Processed freetext questions on page {page.file.src_path}")
            
            # Write debug files only if debug_output_dir is configured
            debug_dir = self.config.get('debug_output_dir')
            if debug_dir:
                try:
                    os.makedirs(debug_dir, exist_ok=True)
                    
                    page_name = page.file.src_path.replace('.md', '').replace('/', '_')
                    
                    with open(f"{debug_dir}/{page_name}_before.html", "w", encoding="utf-8") as f:
                        f.write(html_before)
                    
                    with open(f"{debug_dir}/{page_name}_after.html", "w", encoding="utf-8") as f:
                        f.write(html)
                        
                    logger.debug(f"Debug files written to {debug_dir}")
                except OSError as e:
                    logger.error(f"Could not write debug files to {debug_dir}: {e}")
        else:
            logger.debug(f"No freetext questions found on page {page.file.src_path}")
        
        # Store result for this page
        self.page_questions[page.file.src_path] = self.current_page_has_questions
        
        # Store JavaScript data for use in on_post_page
        if hasattr(self, 'current_page_javascript') and hasattr(self, 'current_page_dom_ready'):
            # Create a nested dictionary structure to store page-specific JS data
            if not hasattr(self, 'page_javascript'):
                self.page_javascript = {}
            self.page_javascript[page.file.src_path] = {
                'functions': self.current_page_javascript[:],  # Make a copy
                'dom_ready': self.current_page_dom_ready[:]   # Make a copy
            }
            logger.debug(f"Stored JavaScript data for {page.file.src_path}: {len(self.current_page_javascript)} functions, {len(self.current_page_dom_ready)} DOM ready blocks")
        
        return html
        
    def _consolidate_dom_ready_events(self, javascript_code):
        """Consolidate multiple DOMContentLoaded events into a single one."""
        import re
        
        # Extract all function definitions (not wrapped in DOMContentLoaded)
        functions = []
        dom_ready_content = []
        
        # Split by DOMContentLoaded events and extract the content
        parts = javascript_code.split("document.addEventListener('DOMContentLoaded', function() {")
        
        # First part contains function definitions
        if parts[0].strip():
            functions.append(parts[0].strip())
        
        # Extract content from each DOMContentLoaded block
        for i in range(1, len(parts)):
            part = parts[i]
            # Find the closing of the DOMContentLoaded function
            # Count braces to find the end
            brace_count = 1
            pos = 0
            while pos < len(part) and brace_count > 0:
                if part[pos] == '{':
                    brace_count += 1
                elif part[pos] == '}':
                    brace_count -= 1
                pos += 1
            
            if pos < len(part):
                # Extract the content inside the DOMContentLoaded
                dom_content = part[:pos-1].strip()
                # Remove the closing });
                dom_content = re.sub(r'\}\);?\s*$', '', dom_content).strip()
                if dom_content:
                    dom_ready_content.append(dom_content)
                
                # Add any remaining functions after this DOMContentLoaded
                remaining = part[pos:].strip()
                if remaining and not remaining.startswith('});'):
                    functions.append(remaining)
        
        # Combine everything
        result_parts = []
        
        # Add all function definitions first
        if functions:
            result_parts.extend(functions)
        
        # Add single consolidated DOMContentLoaded event
        if dom_ready_content:
            consolidated_dom_ready = f"""
document.addEventListener('DOMContentLoaded', function() {{
{chr(10).join('    ' + line for content in dom_ready_content for line in content.split(chr(10)) if line.strip())}
}});"""
            result_parts.append(consolidated_dom_ready)
        
        return '\n\n'.join(result_parts)
        
    def _process_freetext_blocks_html(self, html):
        """Process individual freetext question blocks in HTML."""
        import re
        import uuid

        logger.debug("Processing freetext blocks in HTML")
        logger.debug(f"HTML snippet (first 500 chars): {html[:500]}")

        # Extract all admonitions first
        def extract_admonition_content(html):
            """Extract content from freetext admonition divs, handling nested divs correctly."""
            results = []
            
            # Find all starting positions of individual freetext admonitions (NOT assessments)
            start_pattern = r'<div class="admonition freetext"[^>]*>'
            for start_match in re.finditer(start_pattern, html):
                start_pos = start_match.end()
                
                # Count div tags to find the matching closing div
                div_count = 1
                pos = start_pos
                
                while pos < len(html) and div_count > 0:
                    # Look for the next div tag (opening or closing)
                    next_div = re.search(r'<(/?)div[^>]*>', html[pos:])
                    if not next_div:
                        break
                    
                    if next_div.group(1):  # Closing div
                        div_count -= 1
                    else:  # Opening div
                        div_count += 1
                    
                    pos += next_div.end()
                
                if div_count == 0:
                    # Found the matching closing div
                    content = html[start_pos:pos - len('</div>')]
                    results.append((start_match.group(0) + content + '</div>', content))
            
            return results
        
        admonition_matches = extract_admonition_content(html)
        logger.debug(f"Found {len(admonition_matches)} freetext admonition(s) to process")
        
        # PRE-GENERATE question IDs to ensure consistency
        question_ids = {}
        for i, (full_match, content) in enumerate(admonition_matches):
            question_ids[i] = str(uuid.uuid4())[:8]
            logger.debug(f"Pre-generated question ID {i}: {question_ids[i]}")
        
        def replace_question(match_info, match_index):
            full_match, admonition_content = match_info
            self.current_page_has_questions = True
            
            # Use pre-generated question ID for consistency
            question_id = question_ids[match_index]
            logger.debug(f"Processing question with ID: {question_id}")
            
            # Remove the admonition title if present
            title_match = re.search(r'<p class="admonition-title"[^>]*>.*?</p>(.*)', admonition_content, re.DOTALL)
            if title_match:
                content = title_match.group(1).strip()
            else:
                content = admonition_content.strip()
            
            # Check if this is an assessment (contains freetext-assessment class)
            is_assessment = 'freetext-assessment' in full_match
            
            if is_assessment:
                # Parse as assessment with multiple questions
                return self._parse_and_generate_assessment_html_from_admonition(content, question_id)
            else:
                # Parse configuration from HTML content
                config = self._parse_question_config(content)
                
                # Clean up question content: remove --- separator if present
                if '---' in config['question']:
                    question_part = config['question'].split('---')[0].strip()
                    config['question'] = question_part
                
                logger.debug(f"Parsed config: {config}")
                
                # Generate HTML and JavaScript with the SAME question_id
                html = self._generate_question_html(config, question_id)
                return html
        
        # Process each admonition with its pre-assigned ID
        for i, (full_match, admonition_content) in enumerate(admonition_matches):
            replacement = replace_question((full_match, admonition_content), i)
            html = html.replace(full_match, replacement, 1)
        
        return html
        

    def _parse_question_config(self, content):
        """Parse question configuration from content (supports --- separator)."""
        import re
        
        config = {
            'question': '',
            'type': self.config.get('default_question_type', 'short'),
            'show_answer': True,
            'marks': self.config.get('default_marks', 0),
            'placeholder': self.config.get('default_placeholder', 'Enter your answer...'),
            'rows': None,  # Will be set based on type if not explicitly configured
            'answer': ''
        }
        
        logger.debug(f"Parsing content: {content[:200]}...")
        
        # Check for --- separator first (NEW FEATURE)
        # In HTML, --- becomes <hr> or <hr />
        hr_pattern = r'<hr[^>]*/?>'
        has_separator = bool(re.search(hr_pattern, content)) or '---' in content
        
        if has_separator:
            logger.debug("Found --- separator (or <hr>), splitting content")
            
            # Split by <hr> tags if present, otherwise by ---
            if re.search(hr_pattern, content):
                parts = re.split(hr_pattern, content, 1)
            else:
                parts = content.split('---', 1)
            
            if len(parts) >= 2:
                question_content = parts[0].strip()
                config_content = parts[1].strip()
                
                # Set the question content directly (preserves all rich content)
                config['question'] = question_content
                logger.debug(f"Question part length: {len(question_content)}")
                logger.debug(f"Config part length: {len(config_content)}")
                
                # Parse configuration from config section only
                self._parse_config_section(config_content, config)
            else:
                logger.debug("Separator found but couldn't split content, falling back to legacy")
                # Fallback to legacy parsing
                is_html = bool(re.search(r'<[^>]+>', content))
                if is_html:
                    self._parse_html_content_legacy(content, config)
                else:
                    self._parse_plain_text_content(content, config)
            
        else:
            logger.debug("No --- separator found, using legacy parsing")
            # Legacy parsing: detect HTML vs plain text and parse accordingly
            is_html = bool(re.search(r'<[^>]+>', content))
            logger.debug(f"Content type: {'HTML' if is_html else 'Plain text'}")
            
            if is_html:
                self._parse_html_content_legacy(content, config)
            else:
                self._parse_plain_text_content(content, config)
        
        logger.debug(f"Final config: {config}")
        return config

    def _parse_config_section(self, config_content, config):
        """Parse configuration from a dedicated config section using comma-separated format."""
        import re
        
        # Clean up the content - remove HTML tags
        clean_content = re.sub(r'<[^>]+>', '', config_content).strip()
        
        logger.debug(f"Parsing config content: {clean_content}")
        
        # Skip parsing if content is too long (likely not configuration)
        if len(clean_content) > 200:
            logger.debug("Content too long to be configuration, skipping")
            return
        
        # Check if it looks like incorrect line-based config
        if '\n' in clean_content and ',' not in clean_content:
            # Only warn if it contains config-like keywords
            config_keywords = ['marks:', 'type:', 'rows:', 'placeholder:', 'answer:', 'question:', 'show_answer:']
            if any(keyword in clean_content.lower() for keyword in config_keywords):
                logger.warning(
                    f"Invalid configuration format. "
                    f"Expected comma-separated format: 'marks: 10, type: long, rows: 5'. "
                    f"Found line-based format. Using default values."
                )
            return
        
        # Parse using comma-separated format only
        config_dict = self._parse_comma_separated_config(clean_content)
        
        logger.debug(f"Parsed config dictionary: {config_dict}")
        
        # Validate that we got a proper config dictionary
        if not isinstance(config_dict, dict):
            logger.warning(
                f"Configuration parsing failed for: '{clean_content}'. "
                f"Please use comma-separated format: 'key1: value1, key2: value2'. "
                f"Using default configuration values."
            )
            return
        
        # Only warn if we expected to find config but couldn't parse it
        if not config_dict and clean_content.strip():
            # Check if it looks like it was meant to be configuration
            config_indicators = ['marks:', 'type:', 'rows:', ':', 'marks=', 'type=']
            looks_like_config = any(indicator in clean_content.lower() for indicator in config_indicators)
            
            if looks_like_config:
                logger.warning(
                    f"Failed to parse configuration: '{clean_content}'. "
                    f"Please use comma-separated format: 'key1: value1, key2: value2'. "
                    f"Using default configuration values."
                )
            else:
                logger.debug(f"Content doesn't appear to be configuration: {clean_content[:50]}...")
            return
        
        # Apply config values with type conversion and validation
        if config_dict:
            self._apply_config_dictionary(config_dict, config)

    def _parse_comma_separated_config(self, content):
        """Parse comma-separated config content into key:value dictionary."""
        if not content or not content.strip():
            return {}
        
        config_dict = {}
        
        # First, check if this looks like actual configuration content
        # Configuration should have at least one colon and common config keywords
        config_keywords = ['marks', 'type', 'rows', 'placeholder', 'answer', 'question', 'show_answer', 'title', 'shuffle']
        has_config_keyword = any(keyword in content.lower() for keyword in config_keywords)
        has_colons = ':' in content
        
        # If it doesn't look like configuration, return empty dict
        if not (has_config_keyword and has_colons):
            logger.debug(f"Content doesn't appear to be configuration: {content[:50]}...")
            return {}
        
        # Split by commas and parse each key:value pair
        items = [item.strip() for item in content.split(',')]
        
        for item in items:
            if ':' in item:
                key, value = item.split(':', 1)
                key = key.strip()
                value = value.strip()
                
                # Only process if key looks like a valid config key
                if key.lower() in config_keywords:
                    # Remove quotes if present
                    if (value.startswith('"') and value.endswith('"')) or (value.startswith("'") and value.endswith("'")):
                        value = value[1:-1]
                    
                    config_dict[key] = value
                else:
                    logger.debug(f"Skipping unknown config key '{key}' in item '{item}'")
            elif item.strip() and len(item.strip()) < 50:  # Only warn for short items that might be intended as config
                logger.debug(f"Skipping config item without colon: '{item}'")
        
        return config_dict

    def _apply_config_dictionary(self, config_dict, config):
        """Apply configuration dictionary to config object with proper type conversion."""
        
        # Define type converters for each config key
        type_converters = {
            'marks': lambda x: int(x),
            'rows': lambda x: int(x),
            'show_answer': lambda x: x.lower() in ['true', 'yes', '1'],
            'shuffle': lambda x: x.lower() in ['true', 'yes', '1'],
            'type': lambda x: x,  # string, validated below
            'placeholder': lambda x: x,  # string
            'answer': lambda x: x,  # string
            'title': lambda x: x,  # string (for assessments)
            'question': lambda x: x,  # string
        }
        
        # Valid values for certain config keys
        valid_values = {
            'type': ['short', 'long']
        }
        
        # Apply each config value
        for key, value in config_dict.items():
            if key in type_converters:
                try:
                    # Convert to appropriate type
                    converted_value = type_converters[key](value)
                    
                    # Validate if needed
                    if key in valid_values and converted_value not in valid_values[key]:
                        logger.warning(
                            f"Invalid configuration value '{converted_value}' for '{key}'. "
                            f"Expected {self._get_expected_type_hint(key)}. Using default value."
                        )
                        continue
                    
                    config[key] = converted_value
                    logger.debug(f"Applied config {key} = {converted_value}")
                    
                except (ValueError, TypeError) as e:
                    logger.warning(
                        f"Invalid configuration value '{value}' for '{key}'. "
                        f"Expected {self._get_expected_type_hint(key)}. Using default value."
                    )
                    # Apply defaults for failed conversions
                    if key == 'marks':
                        config[key] = self.config.get('default_marks', 0)
                    elif key == 'rows':
                        config[key] = None  # Will use type-based default
            else:
                # Unknown config key - store as string
                config[key] = value
                logger.debug(f"Applied unknown config {key} = {value}")

    def _parse_html_content_legacy(self, content, config):
        """Legacy HTML parsing for backwards compatibility."""
        import re
        
        # First check for comma-separated config format in HTML
        comma_config_pattern = r'<p[^>]*>\s*([^<]*,\s*[^<]*)\s*</p>'
        comma_match = re.search(comma_config_pattern, content)
        if comma_match:
            config_text = comma_match.group(1).strip()
            logger.debug(f"Found comma-separated config in HTML: {config_text}")
            
            # Use the same dictionary-based parsing as the new method
            self._parse_config_section(config_text, config)
            
            # Remove the config paragraph from content
            remaining_content = content.replace(comma_match.group(0), '', 1)
            remaining_content = re.sub(r'<p[^>]*>\s*</p>', '', remaining_content)
            remaining_content = re.sub(r'\n\s*\n', '\n', remaining_content).strip()
            
            # If we found a question in config, use remaining content as additional question content
            if config['question']:
                if remaining_content:
                    config['question'] = f"<p>{config['question']}</p>\n{remaining_content}"
            else:
                # Use remaining content as question
                config['question'] = remaining_content
            
            return  # Done with comma-separated parsing
        
        # Fall back to legacy key: value parsing
        # Parse HTML format: <p>key: value</p>
        config_patterns = {
            'question': r'<p[^>]*>\s*question:\s*(.*?)\s*</p>',
            'marks': r'<p[^>]*>\s*marks:\s*(\d+)\s*</p>',
            'placeholder': r'<p[^>]*>\s*placeholder:\s*(.*?)\s*</p>',
            'show_answer': r'<p[^>]*>\s*show_answer:\s*(true|false|yes|no)\s*</p>',
            'answer': r'<p[^>]*>\s*answer:\s*(.*?)\s*</p>',
            'rows': r'<p[^>]*>\s*rows:\s*(\d+)\s*</p>',
            'type': r'<p[^>]*>\s*type:\s*(short|long)\s*</p>'
        }
        
        # Extract configuration values and track remaining content for rich content preservation
        remaining_content = content
        
        for config_key, pattern in config_patterns.items():
            logger.debug(f"Testing pattern for {config_key}: {pattern}")
            
            match = re.search(pattern, remaining_content, re.DOTALL | re.IGNORECASE | re.MULTILINE)
            if match:
                value = match.group(1).strip()
                logger.debug(f"Found config: {config_key} = {value}")
                
                # Parse the value based on type
                if config_key == 'marks' or config_key == 'rows':
                    try:
                        config[config_key] = int(value)
                    except ValueError:
                        if config_key == 'marks':
                            config[config_key] = self.config.get('default_marks', 0)
                        else:
                            config[config_key] = None
                elif config_key == 'show_answer':
                    config[config_key] = value.lower() in ['true', 'yes', '1']
                else:
                    config[config_key] = value
                
                # Remove this config paragraph from remaining content
                remaining_content = remaining_content.replace(match.group(0), '', 1)
                logger.debug(f"Removed config paragraph '{match.group(0)}', remaining length: {len(remaining_content)}")
            else:
                logger.debug(f"No match found for {config_key}")
        
        # Clean up any empty paragraphs and normalize whitespace
        remaining_content = re.sub(r'<p[^>]*>\s*</p>', '', remaining_content)
        remaining_content = re.sub(r'\n\s*\n', '\n', remaining_content).strip()
        
        # If we found a question in config, use remaining content as additional question content
        if config['question']:
            if remaining_content:
                # Combine question text with remaining rich content (after removing config paragraphs)
                config['question'] = f"<p>{config['question']}</p>\n{remaining_content}"
            else:
                config['question'] = f"<p>{config['question']}</p>"
        else:
            # No explicit question config, use all remaining content as question (after removing config paragraphs)
            config['question'] = remaining_content if remaining_content else '<p>No question text provided</p>'

    def _parse_plain_text_content(self, content, config):
        """Parse plain text content (original approach)."""
        lines = content.strip().split('\n')
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            if ':' in line:
                key, value = line.split(':', 1)
                key = key.strip()
                value = value.strip()
                
                if key in config:
                    logger.debug(f"Found config: {key} = {value}")
                    if key == 'show_answer':
                        config[key] = value.lower() in ['true', 'yes', '1']
                    elif key in ['marks', 'rows']:
                        try:
                            config[key] = int(value)
                        except ValueError:
                            if key == 'marks':
                                config[key] = self.config.get('default_marks', 0)
                            else:
                                config[key] = None
                    else:
                        config[key] = value

    def _parse_and_generate_assessment_html_from_admonition(self, content, assessment_id=None):
        """Parse assessment content from HTML admonition and generate HTML."""
        import re
        import uuid
        
        # Use provided assessment_id or generate a new one
        if assessment_id is None:
            assessment_id = str(uuid.uuid4())[:8]
        
        # Split content by <hr> tags to separate questions
        question_sections = re.split(r'<hr[^>]*>', content)
        
        # Parse assessment-level configuration from first section
        assessment_config = {
            'title': 'Assessment',
            'shuffle': None  # Will use global setting if not specified
        }
        
        questions = []
        
        for idx, section_content in enumerate(question_sections):
            section_content = section_content.strip()
            if not section_content:
                continue
            
            logger.debug(f"Processing assessment section {idx}: {section_content[:100]}...")
                
            # Parse this section using our existing HTML question parser
            config = self._parse_question_config(section_content)
            
            # For the first section, also look for assessment-level configuration
            if idx == 0:
                # Look for title and shuffle in the first section
                title_match = re.search(r'<p[^>]*>\s*title:\s*(.*?)\s*</p>', section_content, re.IGNORECASE)
                if title_match:
                    assessment_config['title'] = title_match.group(1).strip()
                    logger.debug(f"Found assessment title: {assessment_config['title']}")
                
                shuffle_match = re.search(r'<p[^>]*>\s*shuffle:\s*(true|false|yes|no)\s*</p>', section_content, re.IGNORECASE)
                if shuffle_match:
                    assessment_config['shuffle'] = shuffle_match.group(1).lower() in ['true', 'yes', '1']
                    logger.debug(f"Found assessment shuffle: {assessment_config['shuffle']}")
            
            # Only add questions that have actual question content
            if config['question'] and config['question'].strip():
                questions.append(config)
                logger.debug(f"Added question {len(questions)}: marks={config['marks']}")
        
        logger.debug(f"Assessment total questions: {len(questions)}")
        logger.debug(f"Assessment config: {assessment_config}")
        
        # Generate assessment HTML using the provided/generated assessment_id
        if questions:
            return self._generate_assessment_html(questions, assessment_id, assessment_config)
        else:
            return '<div class="error">No valid questions found in assessment</div>'

    def _parse_and_generate_assessment_html(self, content):
        """Parse assessment content from code block and generate HTML."""
        # Split content by '---' to separate questions
        questions_content = content.split('---')
        
        # Parse assessment-level configuration from first section
        assessment_config = {
            'title': 'Assessment',
            'shuffle': None  # Will use global setting if not specified
        }
        
        questions = []
        
        for idx, q_content in enumerate(questions_content):
            q_content = q_content.strip()
            if not q_content:
                continue
                
            lines = q_content.split('\n')
            question_config = {
                'question': '',
                'type': self.config.get('default_question_type', 'short'),
                'show_answer': True,
                'marks': self.config.get('default_marks', 0),
                'placeholder': self.config.get('default_placeholder', 'Enter your answer...'),
                'answer': ''
            }
            
            # Parse lines for this question
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                    
                if ':' in line:
                    key, value = line.split(':', 1)
                    key = key.strip()
                    value = value.strip()
                    
                    # Check for assessment-level config in first question
                    if idx == 0 and key in ['title', 'shuffle']:
                        if key == 'shuffle':
                            assessment_config[key] = value.lower() in ['true', 'yes', '1']
                        else:
                            assessment_config[key] = value
                    elif key in question_config:
                        if key == 'show_answer':
                            question_config[key] = value.lower() in ['true', 'yes', '1']
                        elif key == 'marks':
                            try:
                                question_config[key] = int(value)
                            except ValueError:
                                question_config[key] = self.config.get('default_marks', 0)
                        else:
                            question_config[key] = value
            
            # Only add questions that have a question text
            if question_config['question']:
                questions.append(question_config)
        
        # Generate assessment HTML
        if questions:
            assessment_id = str(uuid.uuid4())[:8]
            return self._generate_assessment_html(questions, assessment_id, assessment_config)
        
        return ''

    def _process_assessment_blocks_html(self, html):
        """Process freetext assessment blocks in HTML."""
        import re
        
        def extract_assessment_content(html):
            """Extract content from freetext-assessment admonition divs, handling nested divs correctly."""
            results = []
            
            # Find all starting positions of freetext-assessment admonitions
            start_pattern = r'<div class="admonition freetext-assessment"[^>]*>'
            for start_match in re.finditer(start_pattern, html):
                start_pos = start_match.end()
                
                # Count div tags to find the matching closing div
                div_count = 1
                pos = start_pos
                
                while pos < len(html) and div_count > 0:
                    # Look for the next div tag (opening or closing)
                    next_div = re.search(r'<(/?)div[^>]*>', html[pos:])
                    if not next_div:
                        break
                    
                    if next_div.group(1):  # Closing div
                        div_count -= 1
                    else:  # Opening div
                        div_count += 1
                    
                    pos += next_div.end()
                
                if div_count == 0:
                    # Found the matching closing div
                    content = html[start_pos:pos - len('</div>')]
                    results.append((start_match.group(0) + content + '</div>', content))
            
            return results
        
        assessment_matches = extract_assessment_content(html)
        
        def replace_assessment(match_info):
            full_match, admonition_content = match_info
            self.current_page_has_questions = True
            
            # Extract the content inside the admonition, skipping the title if present
            title_match = re.search(r'<p class="admonition-title"[^>]*>.*?</p>(.*)', admonition_content, re.DOTALL)
            if title_match:
                content = title_match.group(1).strip()
            else:
                content = admonition_content.strip()
            
            # Parse assessment-level configuration and questions
            assessment_config, questions = self._parse_assessment_with_config_from_html(content)
            assessment_id = str(uuid.uuid4())[:8]
            
            return self._generate_assessment_html(questions, assessment_id, assessment_config)
        
        # Replace all assessments
        for full_match, content in assessment_matches:
            replacement = replace_assessment((full_match, content))
            html = html.replace(full_match, replacement)
        
        return html

    def _parse_assessment_with_config_from_html(self, html_content):
        """Parse assessment configuration and questions from HTML content."""
        import re
        
        # Default assessment configuration
        assessment_config = {
            'shuffle': None,  # None means use global setting
            'title': 'Assessment'
        }
        
        # First, extract assessment-level configuration (title, shuffle)
        config_patterns = {
            'title': r'<p[^>]*>\s*title:\s*(.*?)\s*</p>',
            'shuffle': r'<p[^>]*>\s*shuffle:\s*(.*?)\s*</p>'
        }
        
        for key, pattern in config_patterns.items():
            match = re.search(pattern, html_content, re.IGNORECASE)
            if match:
                value = match.group(1).strip()
                if key == 'shuffle':
                    assessment_config[key] = value.lower() in ['true', 'yes', '1']
                else:
                    assessment_config[key] = value
                
                # Remove the config line from content
                html_content = re.sub(pattern, '', html_content, flags=re.IGNORECASE)
        
        # Split content by horizontal rules (<hr>) which separate questions
        question_blocks = re.split(r'<hr[^>]*>', html_content)
        
        questions = []
        
        for block in question_blocks:
            block = block.strip()
            if not block:
                continue
                
            # Parse each block as a question
            config = self._parse_question_config(block)
            if config['question']:
                questions.append(config)
        
        return assessment_config, questions
        
        if should_shuffle and len(questions) > 1:
            random.shuffle(questions)
        
        return assessment_config, questions

    def _process_freetext_blocks(self, markdown):
        """Process individual freetext question blocks."""
        pattern = r'!!! freetext\s*\n(.*?)(?=\n!!!|\n\n|$)'
        
        def replace_freetext(match):
            self.current_page_has_questions = True
            content = match.group(1)
            config = self._parse_question_config(content)
            question_id = str(uuid.uuid4())[:8]
            return self._generate_question_html(config, question_id)
        
        return re.sub(pattern, replace_freetext, markdown, flags=re.DOTALL)

    def _process_assessment_blocks(self, markdown):
        """Process freetext assessment blocks with multiple questions."""
        pattern = r'!!! freetext-assessment\s*\n(.*?)(?=\n!!!|\n\n|$)'
        
        def replace_assessment(match):
            self.current_page_has_questions = True
            content = match.group(1)
            
            # Parse assessment-level configuration and questions
            assessment_config, questions = self._parse_assessment_with_config(content)
            assessment_id = str(uuid.uuid4())[:8]
            
            return self._generate_assessment_html(questions, assessment_id, assessment_config)
        
        return re.sub(pattern, replace_assessment, markdown, flags=re.DOTALL)

    def _parse_assessment_questions(self, content):
        """Parse multiple questions from assessment content."""
        questions = []
        question_blocks = content.split('---')
        
        for block in question_blocks:
            block = block.strip()
            if block:
                config = self._parse_question_config(block)
                if config['question']:
                    questions.append(config)
        
        return questions

    def _parse_assessment_with_config(self, content):
        """Parse assessment configuration and questions from content."""
        
        # Default assessment configuration
        assessment_config = {
            'shuffle': None,  # None means use global setting
            'title': 'Assessment'
        }
        
        lines = content.strip().split('\n')
        assessment_lines = []
        questions_content = []
        
        # Separate assessment config from questions
        in_questions = False
        current_block = []
        
        for line in lines:
            if line.strip().startswith('question:'):
                in_questions = True
                if current_block:
                    questions_content.append('\n'.join(current_block))
                current_block = [line]
            elif line.strip() == '---':
                if current_block:
                    questions_content.append('\n'.join(current_block))
                current_block = []
            elif in_questions:
                current_block.append(line)
            else:
                # Assessment-level configuration
                if ':' in line:
                    key, value = line.split(':', 1)
                    key = key.strip()
                    value = value.strip()
                    
                    if key == 'shuffle':
                        assessment_config['shuffle'] = value.lower() in ['true', 'yes', '1']
                    elif key == 'title':
                        assessment_config['title'] = value
        
        # Add the last question block
        if current_block:
            questions_content.append('\n'.join(current_block))
        
        # Parse individual questions
        questions = []
        for block_content in questions_content:
            if block_content.strip():
                config = self._parse_question_config(block_content)
                if config['question']:
                    questions.append(config)
        
        # Apply shuffling if enabled
        should_shuffle = assessment_config['shuffle']
        if should_shuffle is None:  # Use global setting if not specified
            should_shuffle = self.config.get('shuffle_questions', False)
        
        if should_shuffle and len(questions) > 1:
            random.shuffle(questions)
        
        return assessment_config, questions

    def _process_freetext_blocks(self, markdown):
        """Process individual freetext question blocks."""
        pattern = r'!!! freetext\s*\n(.*?)(?=\n!!!|\n\n|$)'
        
        def replace_freetext(match):
            self.current_page_has_questions = True
            content = match.group(1)
            config = self._parse_question_config(content)
            question_id = str(uuid.uuid4())[:8]
            return self._generate_question_html(config, question_id)
        
        return re.sub(pattern, replace_freetext, markdown, flags=re.DOTALL)

    def _process_assessment_blocks(self, markdown):
        """Process freetext assessment blocks with multiple questions."""
        pattern = r'!!! freetext-assessment\s*\n(.*?)(?=\n!!!|\n\n|$)'
        
        def replace_assessment(match):
            self.current_page_has_questions = True
            content = match.group(1)
            
            # Parse assessment-level configuration and questions
            assessment_config, questions = self._parse_assessment_with_config(content)
            assessment_id = str(uuid.uuid4())[:8]
            
            return self._generate_assessment_html(questions, assessment_id, assessment_config)
        
        return re.sub(pattern, replace_assessment, markdown, flags=re.DOTALL)

    def _parse_assessment_questions(self, content):
        """Parse multiple questions from assessment content (legacy method)."""
        _, questions = self._parse_assessment_with_config(content)
        return questions

    def _escape_html(self, text):
        """Escape HTML entities for safe use in HTML attributes."""
        if not text:
            return ""
        return str(text).replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;').replace("'", '&#x27;')

    def _generate_question_html(self, config, question_id):
        """Generate HTML for a single question."""
        # Determine rows: explicit config > type-based defaults
        if 'rows' in config and config['rows'] is not None and config['rows'] > 0:
            rows = config['rows']
        elif config['type'] == 'long':
            rows = self.config.get('default_long_answer_rows', 6)
        else:  # short type
            rows = self.config.get('default_answer_rows', 3)
            
        char_counter = self._get_character_counter_html(question_id) if self.config.get('show_character_count', True) else ''
        
        # Build oninput attribute conditionally
        oninput_parts = []
        if self.config.get('show_character_count', True):
            oninput_parts.append(f"updateCharCount_{question_id}()")
        # Auto-save functionality has been removed from the plugin
        oninput_attr = f'oninput="{"; ".join(oninput_parts)};"' if oninput_parts else ''
        
        # Process question text as markdown
        question_html = self._process_markdown_content(config['question'])
        
        html = f'''
<div class="{self.config.get('question_class', 'freetext-question')}" data-question-id="{question_id}">
    <div class="question-header">
        <div class="question-text">{question_html}</div>
        {f'<span class="marks">({config["marks"]} marks)</span>' if config['marks'] > 0 else ''}
    </div>
    
    <div class="answer-section">
        <textarea 
            id="answer_{question_id}" 
            class="{self.config.get('answer_class', 'freetext-answer')}"
            rows="{rows}" 
            placeholder="{self._escape_html(config['placeholder'])}"
            {oninput_attr}
        ></textarea>
        {char_counter}
    </div>
    
    <div class="button-group">
        <button onclick="submitAnswer_{question_id}()" class="submit-btn">Submit Answer</button>
    </div>
    
    <div id="feedback_{question_id}" class="feedback" style="display: none;"></div>
</div>
'''
        
        # CRITICAL: Generate JavaScript immediately with the SAME question_id
        question_js = self._generate_question_javascript(question_id, config)
        if hasattr(self, 'current_page_javascript'):
            self.current_page_javascript.append(question_js)
            logger.debug(f"Generated JavaScript for question {question_id}")
        
        return html

    def _generate_assessment_html(self, questions, assessment_id, assessment_config=None):
        """Generate HTML for an assessment with multiple questions."""
        if assessment_config is None:
            assessment_config = {'title': 'Assessment', 'shuffle': None}
            
        total_marks = sum(q['marks'] for q in questions)
        
        # Determine if shuffling should be enabled
        should_shuffle = assessment_config.get('shuffle')
        if should_shuffle is None:  # Use global setting if not specified
            should_shuffle = self.config.get('shuffle_questions', False)
        
        questions_html = ""
        for i, config in enumerate(questions):
            question_id = f"{assessment_id}_q{i+1}"
            
            # Determine rows: explicit config > type-based defaults
            if 'rows' in config and config['rows'] is not None and config['rows'] > 0:
                rows = config['rows']
            elif config['type'] == 'long':
                rows = self.config.get('default_long_answer_rows', 6)
            else:  # short type
                rows = self.config.get('default_answer_rows', 3)
                
            char_counter = self._get_character_counter_html(question_id) if self.config.get('show_character_count', True) else ''
            
            # Build oninput attribute conditionally for assessments
            oninput_parts = []
            if self.config.get('show_character_count', True):
                oninput_parts.append(f"updateCharCount_{question_id}()")
            # Always include auto-save call - the function itself controls whether it's active
            oninput_parts.append(f"autoSaveAssessment_{assessment_id}()")
            oninput_attr = f'oninput="{"; ".join(oninput_parts)};"' if oninput_parts else ''
            
            # Process question text as markdown
            question_html = self._process_markdown_content(config['question'])
            
            questions_html += f'''
<div class="assessment-question" data-question-id="{question_id}">
    <div class="question-header">
        <div class="question-number">{i+1}.</div>
        <div class="question-text">{question_html}</div>
        {f'<span class="marks">({config["marks"]} marks)</span>' if config['marks'] > 0 else ''}
    </div>
    
    <div class="answer-section">
        <textarea 
            id="answer_{question_id}" 
            class="{self.config.get('answer_class', 'freetext-answer')}"
            rows="{rows}" 
            placeholder="{self._escape_html(config['placeholder'])}"
            {oninput_attr}
        ></textarea>
        {char_counter}
    </div>
    
    <div id="feedback_{question_id}" class="feedback" style="display: none;"></div>
</div>
'''

        html = f'''
<div class="{self.config['assessment_class']}" data-assessment-id="{assessment_id}" data-shuffle="{str(should_shuffle).lower()}">
    <div class="assessment-header">
        <h3>{assessment_config['title']}</h3>
        {f'<span class="total-marks">Total: {total_marks} marks</span>' if total_marks > 0 else ''}
    </div>
    
    {questions_html}
    
    <div class="assessment-buttons">
        <button onclick="submitAssessment_{assessment_id}()" class="submit-assessment-btn">Submit Assessment</button>
    </div>
    
    <div id="assessment_feedback_{assessment_id}" class="assessment-feedback" style="display: none;"></div>
</div>
'''
        
        # Collect JavaScript instead of outputting it inline
        assessment_js = self._generate_assessment_javascript(assessment_id, questions)
        if hasattr(self, 'current_page_javascript'):
            self.current_page_javascript.append(assessment_js)
            
        return html

    def _get_character_counter_html(self, question_id):
        """Generate character counter HTML."""
        return f'<div id="charCount_{question_id}" class="char-count">0 characters</div>'

    def _generate_question_javascript(self, question_id, config):
        """Generate JavaScript for individual questions."""
        enable_auto_save = str(self.config.get('enable_auto_save', True)).lower()
        show_character_count = self.config.get('show_character_count', True)
        
        js_functions = []
        
        logger.debug(f"Generating JavaScript for question_id: {question_id}")
        
        # Character count function (only if enabled)
        if show_character_count:
            char_count_func = f'''function updateCharCount_{question_id}() {{
    const textarea = document.getElementById('answer_{question_id}');
    const counter = document.getElementById('charCount_{question_id}');
    if (counter) {{
        counter.textContent = textarea.value.length + ' characters';
    }}
}}'''
            js_functions.append(char_count_func)
            logger.debug(f"Added updateCharCount_{question_id}")
        
        # Auto-save functionality has been removed from the plugin
        
        # CRITICAL FIX: Clean the answer text for JavaScript - check both keys
        answer_text = config.get("sample_answer") or config.get("answer", "No sample answer provided.")
        clean_answer = self._clean_answer_for_javascript(answer_text)
        
        # Submit function (always included)
        submit_func = f'''function submitAnswer_{question_id}() {{
    const answer = document.getElementById('answer_{question_id}').value;
    const feedback = document.getElementById('feedback_{question_id}');
    const submitBtn = document.querySelector('[data-question-id="{question_id}"] .submit-btn');
    
    if (answer.trim() === '') {{
        feedback.innerHTML = '<div class="warning">Please enter an answer before submitting.</div>';
        feedback.style.display = 'block';
        return;
    }}
    
    // Update button text and add tooltip
    submitBtn.textContent = 'Submitted';
    submitBtn.title = 'Click to resubmit';
    
    // Only show sample answer if show_answer is enabled, no success message
    if ({str(config.get('show_answer', False)).lower()}) {{
        feedback.innerHTML = '<div class="answer-display"><strong>Sample Answer:</strong><br>{clean_answer}</div>';
        feedback.style.display = 'block';
    }} else {{
        // Hide feedback if no sample answer to show
        feedback.style.display = 'none';
    }}
    
    // Auto-save and answer persistence functionality has been removed from the plugin
}}'''
        js_functions.append(submit_func)
        logger.debug(f"Added submitAnswer_{question_id}")
        
        # Auto-save and answer persistence functionality has been removed from the plugin
        dom_ready_js = f'''// Initialize question {question_id} (persistence removed)
    // Question {question_id} ready for user input
'''
        
        # Store DOM ready code for later consolidation
        if hasattr(self, 'current_page_dom_ready'):
            self.current_page_dom_ready.append(dom_ready_js)
        
        final_js = '\n\n'.join(js_functions)
        logger.debug(f"Generated JavaScript for {question_id} with {len(js_functions)} functions")
        return final_js

    def _generate_assessment_javascript(self, assessment_id, questions):
        """Generate JavaScript for assessments."""
        question_ids = [f"{assessment_id}_q{i+1}" for i in range(len(questions))]
        enable_auto_save = str(self.config.get('enable_auto_save', True)).lower()
        
        js = f'''
function autoSaveAssessment_{assessment_id}() {{
    if ({enable_auto_save}) {{
        const answers = {{}};
        {chr(10).join(f'        answers["{qid}"] = document.getElementById("answer_{qid}").value;' for qid in question_ids)}
        localStorage.setItem('freetext_assessment_{assessment_id}', JSON.stringify(answers));
    }}
}}

function submitAssessment_{assessment_id}() {{
    const answers = {{}};
    let allAnswered = true;
    
    {chr(10).join(f'''
    const answer_{qid} = document.getElementById('answer_{qid}').value;
    if (answer_{qid}.trim() === '') allAnswered = false;
    answers['{qid}'] = answer_{qid};''' for qid in question_ids)}
    
    const assessmentFeedback = document.getElementById('assessment_feedback_{assessment_id}');
    const submitBtn = document.querySelector('[data-assessment-id="{assessment_id}"] .submit-assessment-btn');
    
    if (!allAnswered) {{
        assessmentFeedback.innerHTML = '<div class="warning">Please answer all questions before submitting.</div>';
        assessmentFeedback.style.display = 'block';
        return;
    }}
    
    // Update button text and add tooltip
    submitBtn.textContent = 'Submitted';
    submitBtn.title = 'Click to resubmit';
    
    // Hide the assessment feedback (no success message)
    assessmentFeedback.style.display = 'none';
    
    // Automatically show answers for questions with show_answer enabled
    {chr(10).join(f'''
    if ({str(questions[i].get('show_answer', False)).lower()}) {{
        const feedback_{qid} = document.getElementById('feedback_{qid}');
        feedback_{qid}.innerHTML = '<div class="answer-display"><strong>Sample Answer:</strong><br>{self._clean_answer_for_javascript(questions[i].get("answer", "No sample answer provided."))}</div>';
        feedback_{qid}.style.display = 'block';
    }}''' for i, qid in enumerate(question_ids))}
    
    // Auto-save and answer persistence functionality has been removed from the plugin
}}

'''

        # Add character counters (only if enabled)
        if self.config.get('show_character_count', True):
            for qid in question_ids:
                js += f'''
function updateCharCount_{qid}() {{
    const textarea = document.getElementById('answer_{qid}');
    const counter = document.getElementById('charCount_{qid}');
    if (counter) {{
        counter.textContent = textarea.value.length + ' characters';
    }}
}}
'''

        # Auto-load saved answers
        js += f'''
// Shuffle questions if enabled
function shuffleQuestions_{assessment_id}() {{
    const assessment = document.querySelector('[data-assessment-id="{assessment_id}"]');
    const shouldShuffle = assessment.getAttribute('data-shuffle') === 'true';
    
    if (shouldShuffle) {{
        const questionsContainer = assessment;
        const questions = Array.from(questionsContainer.querySelectorAll('[data-question-id]'));
        const header = questionsContainer.querySelector('.assessment-header');
        const buttons = questionsContainer.querySelector('.assessment-buttons');
        const feedback = questionsContainer.querySelector('.assessment-feedback');
        
        // Fisher-Yates shuffle algorithm
        for (let i = questions.length - 1; i > 0; i--) {{
            const j = Math.floor(Math.random() * (i + 1));
            [questions[i], questions[j]] = [questions[j], questions[i]];
        }}
        
        // Clear container and rebuild with shuffled order
        questionsContainer.innerHTML = '';
        questionsContainer.appendChild(header);
        
        // Re-number questions and append
        questions.forEach((question, index) => {{
            const questionNumber = question.querySelector('.question-number');
            if (questionNumber) {{
                questionNumber.textContent = (index + 1) + '.';
            }} else {{
                // Fallback for old h5 structure
                const questionHeader = question.querySelector('.question-header h5');
                if (questionHeader) {{
                    const originalText = questionHeader.textContent;
                    const newText = originalText.replace(/^\\d+\\./, (index + 1) + '.');
                    questionHeader.textContent = newText;
                }}
            }}
            questionsContainer.appendChild(question);
        }});
        
        questionsContainer.appendChild(buttons);
        questionsContainer.appendChild(feedback);
    }}
}}

// Auto-load functionality has been removed from the plugin
document.addEventListener('DOMContentLoaded', function() {{
    // Shuffle questions first if enabled
    shuffleQuestions_{assessment_id}();
    
    // Assessment ready for user input (persistence removed)
}});
'''
        
        return js

    def _generate_restore_answer_js(self, qid):
        """Generate JavaScript to restore a saved answer."""
        js = f'''
        if (answers['{qid}']) {{
            document.getElementById('answer_{qid}').value = answers['{qid}'];'''
        
        if self.config.get('show_character_count', True):
            js += f'''
            updateCharCount_{qid}();'''
        
        js += '''
        }'''
        
        return js

    def on_post_page(self, output, page, config, **kwargs):
        """Add CSS styling and JavaScript if enabled and questions were found."""
        # Check if this page has questions
        page_has_questions = self.page_questions.get(page.file.src_path, False)
        
        if not page_has_questions:
            return output
            
        # Add consolidated JavaScript if there are questions on this page
        if hasattr(self, 'page_javascript') and page.file.src_path in self.page_javascript:
            js_data = self.page_javascript[page.file.src_path]
            
            # Combine functions and DOM ready code
            all_functions = '\n\n'.join(js_data['functions'])
            
            # Add single consolidated DOMContentLoaded event if we have DOM ready code
            if js_data['dom_ready']:
                dom_ready_content = '\n'.join('    ' + line for content in js_data['dom_ready'] for line in content.split('\n') if line.strip())
                consolidated_dom_ready = f"""
document.addEventListener('DOMContentLoaded', function() {{
{dom_ready_content}
}});"""
                final_js = all_functions + '\n\n' + consolidated_dom_ready
            else:
                final_js = all_functions
            
            # Insert JavaScript at the beginning of head section to ensure functions are defined first
            js_block = f'\n<script>\n{final_js}\n</script>\n'
            if '<head>' in output:
                # Insert right after opening <head> tag
                output = output.replace('<head>', '<head>' + js_block, 1)
            elif '</head>' in output:
                # Insert before closing </head> tag
                output = output.replace('</head>', js_block + '</head>', 1)
            else:
                # Fallback: add at very beginning of document
                output = js_block + output
            logger.debug(f"Added consolidated JavaScript block with {len(js_data['functions'])} function groups and {len(js_data['dom_ready'])} DOM ready blocks")
        
        # Insert CSS if enabled
        if self.config.get('enable_css', True):
            css = self._generate_css()
            
            # Insert CSS before closing </head> tag
            if '</head>' in output:
                output = output.replace('</head>', css + '\n</head>')
            else:
                # Fallback: add at the beginning of the body
                output = css + '\n' + output
            
        return output

    def _clean_answer_for_javascript(self, answer_text):
        """Clean answer text for safe embedding in JavaScript strings."""
        if not answer_text:
            return "No sample answer provided."
        
        clean_answer = str(answer_text)
        
        # Remove triple quotes if present
        if clean_answer.startswith('"""') and clean_answer.endswith('"""'):
            clean_answer = clean_answer[3:-3]
        
        # Escape characters for JavaScript string embedding
        clean_answer = clean_answer.replace('\\', '\\\\')  # Escape backslashes first
        clean_answer = clean_answer.replace("'", "\\'")    # Escape single quotes
        clean_answer = clean_answer.replace('"', '\\"')    # Escape double quotes
        clean_answer = clean_answer.replace('\n', '\\n')   # Escape newlines
        clean_answer = clean_answer.replace('\r', '\\r')   # Escape carriage returns
        
        return clean_answer

    def _generate_css(self):
        """Generate comprehensive CSS for the plugin."""
        question_class = self.config.get('question_class', 'freetext-question')
        assessment_class = self.config.get('assessment_class', 'freetext-assessment')

        return f"""
<style>
/* Freetext Plugin Styles with Material Theme Support */
.{question_class}, .{assessment_class} {{
    margin: 20px 0;
    padding: 20px;
    background-color: var(--md-code-bg-color, #f5f5f5);
    border: 1px solid var(--md-default-fg-color--lighter, #e1e4e8);
    border-radius: 8px;
    color: var(--md-default-fg-color, #333333);
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif;
}}

.question-header, .assessment-header {{
    margin-bottom: 15px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    flex-wrap: wrap;
    gap: 10px;
}}

.question-header h4, .question-header h5, .assessment-header h3, .question-text {{
    margin: 0;
    color: var(--md-default-fg-color, #333333) !important;
    font-weight: 600;
    font-size: 1.1em;
    line-height: 1.4;
    flex: 1;
    text-transform: none !important;
}}

.question-text {{
    font-size: 1em;
    line-height: 1.5;
}}

.question-text p {{
    margin: 0 0 10px 0;
}}

.question-text p:last-child {{
    margin-bottom: 0;
}}

.question-text img {{
    max-width: 100%;
    height: auto;
    border-radius: 4px;
    margin: 10px 0;
}}

.question-text a {{
    color: var(--md-primary-fg-color, #0366d6) !important;
    text-decoration: none;
}}

.question-text a:hover {{
    text-decoration: underline;
}}

.question-text pre {{
    background-color: var(--md-code-bg-color, #ffffff);
    border: 1px solid var(--md-default-fg-color--lighter, #e1e4e8);
    border-radius: 4px;
    padding: 12px;
    margin: 10px 0;
    overflow-x: auto;
    font-size: 0.9em;
}}

.question-text code {{
    background-color: var(--md-code-bg-color, #ffffff);
    padding: 2px 4px;
    border-radius: 3px;
    font-size: 0.9em;
    font-family: 'SFMono-Regular', Consolas, 'Liberation Mono', Menlo, monospace;
    border: 1px solid var(--md-default-fg-color--lighter, #e1e4e8);
}}

.question-text .mermaid {{
    text-align: center;
    margin: 15px 0;
    background-color: var(--md-default-bg-color, #ffffff);
    border: 1px solid var(--md-default-fg-color--lighter, #e1e4e8);
    border-radius: 4px;
    padding: 10px;
}}

.question-number {{
    font-weight: 600;
    margin-right: 8px;
    color: var(--md-default-fg-color, #333333);
}}

.marks, .total-marks {{
    background-color: var(--md-primary-fg-color, #0366d6);
    color: white;
    padding: 4px 8px;
    border-radius: 12px;
    font-size: 12px;
    font-weight: 600;
    white-space: nowrap;
}}

.answer-section {{
    margin: 15px 0;
}}

.{question_class} textarea, .assessment-question textarea {{
    width: 100%;
    padding: 12px;
    border: 1px solid var(--md-default-fg-color--lighter, #d1d5da);
    border-radius: 4px;
    font-size: 14px;
    line-height: 1.5;
    resize: vertical;
    font-family: inherit;
    background-color: var(--md-default-bg-color, #ffffff);
    color: var(--md-default-fg-color, #333333);
    box-sizing: border-box;
    min-height: 80px;
}}

.{question_class} textarea:focus, .assessment-question textarea:focus {{
    outline: none;
    border-color: var(--md-primary-fg-color, #0366d6);
}}

.char-count {{
    text-align: right;
    font-size: 12px;
    color: var(--md-default-fg-color--light, #666666);
    margin-top: 5px;
}}

.button-group, .assessment-buttons {{
    margin-top: 15px;
}}

.submit-btn, .submit-assessment-btn {{
    padding: 8px 16px;
    border: none;
    border-radius: 4px;
    font-size: 14px;
    font-weight: 500;
    cursor: pointer;
    background-color: var(--md-primary-fg-color, #0366d6);
    color: white;
}}

.submit-btn:hover, .submit-assessment-btn:hover {{
    background-color: var(--md-primary-fg-color--dark, #0256cc);
}}

.feedback, .assessment-feedback {{
    margin-top: 15px;
    padding: 12px;
    border-radius: 4px;
}}

.feedback .success, .assessment-feedback .success {{
    background-color: var(--md-typeset-color, #d4edda);
    border: 1px solid var(--md-typeset-color, #c3e6cb);
    color: var(--md-typeset-color, #155724);
}}

.feedback .warning, .assessment-feedback .warning {{
    background-color: var(--md-code-bg-color, #fff3cd);
    border: 1px solid var(--md-default-fg-color--lighter, #ffeaa7);
    color: var(--md-default-fg-color, #856404);
}}

.feedback .answer-display {{
    background-color: var(--md-code-bg-color, #e2f3ff);
    border: 1px solid var(--md-primary-fg-color--light, #b6dbff);
    color: var(--md-primary-fg-color, #0366d6);
    margin-top: 10px;
}}

.assessment-question {{
    margin: 15px 0;
    padding: 15px;
    background-color: var(--md-code-bg-color, #f5f5f5);
    border-radius: 6px;
    color: var(--md-default-fg-color, #333333);
}}

.assessment-header h3 {{
    font-size: 1.2em;
    margin: 0;
    color: var(--md-default-fg-color, #333333) !important;
}}

/* Responsive Design */
@media (max-width: 768px) {{
    .{question_class}, .{assessment_class} {{
        padding: 15px;
        margin: 15px 0;
    }}
    
    .question-header, .assessment-header {{
        flex-direction: column;
        align-items: flex-start;
        gap: 10px;
    }}
}}
</style>
"""
