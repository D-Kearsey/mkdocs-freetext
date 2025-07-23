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
from mkdocs.config import config_options
from mkdocs.plugins import BasePlugin
from mkdocs.structure.pages import Page


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
    )

    def __init__(self):
        super().__init__()
        self.page_questions = {}  # Track questions per page

    def on_config(self, config):
        """Called once after config is loaded"""
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
        This hook runs after markdown processing, so rich content will already be rendered.
        """
        # Initialize questions found for this page
        self.current_page_has_questions = False
        
        # Process freetext admonition blocks
        html = self._process_freetext_blocks_html(html)
        
        # Process freetext assessment blocks
        html = self._process_assessment_blocks_html(html)
        
        # Store result for this page
        self.page_questions[page.file.src_path] = self.current_page_has_questions
        
        return html
        
    def _process_freetext_blocks_html(self, html):
        """Process individual freetext question blocks in HTML."""
        import re
        
        def find_and_replace_admonitions(html_content):
            result = html_content
            
            # Find start positions of all freetext admonitions
            pattern = r'<div class="admonition freetext"[^>]*>'
            matches = list(re.finditer(pattern, html_content))
            
            # Process matches in reverse order to avoid index shifting
            for match in reversed(matches):
                start_pos = match.start()
                
                # Find the matching closing </div> by counting div tags
                pos = match.end()
                div_count = 1
                
                while pos < len(html_content) and div_count > 0:
                    if html_content[pos:pos+5] == '<div ':
                        div_count += 1
                        pos += 5
                    elif html_content[pos:pos+6] == '</div>':
                        div_count -= 1
                        if div_count == 0:
                            pos += 6
                            break
                        pos += 6
                    else:
                        pos += 1
                
                if div_count == 0:
                    # Found complete admonition
                    self.current_page_has_questions = True
                    
                    # Extract content between the opening div and closing div
                    content_start = match.end()
                    content = html_content[content_start:pos-6]  # -6 for </div>
                    
                    # Extract the content inside the admonition, skipping the title if present
                    title_match = re.search(r'<p class="admonition-title"[^>]*>.*?</p>(.*)', content, re.DOTALL)
                    if title_match:
                        clean_content = title_match.group(1).strip()
                    else:
                        clean_content = content.strip()
                    
                    # Parse the configuration from the content
                    config = self._parse_question_config_from_html(clean_content)
                    question_id = str(uuid.uuid4())[:8]
                    
                    # Replace the entire admonition with the question HTML
                    question_html = self._generate_question_html(config, question_id)
                    result = result[:start_pos] + question_html + result[pos:]
            
            return result
        
        return find_and_replace_admonitions(html)

    def _parse_freetext_config(self, content):
        """Parse configuration from freetext code block content."""
        config = {
            'question': '',
            'type': 'short',
            'show_answer': True,
            'marks': 0,
            'placeholder': 'Enter your answer...',
            'answer': ''
        }
        
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
                    if key == 'show_answer':
                        config[key] = value.lower() in ['true', 'yes', '1']
                    elif key == 'marks':
                        try:
                            config[key] = int(value)
                        except ValueError:
                            config[key] = 0
                    else:
                        config[key] = value
        
        return config

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
                'type': 'short',
                'show_answer': True,
                'marks': 0,
                'placeholder': 'Enter your answer...',
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
                                question_config[key] = 0
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
        
        # Pattern to match admonition divs with freetext-assessment class
        pattern = r'<div class="admonition freetext-assessment"[^>]*>(.*?)</div>'
        
        def replace_assessment(match):
            self.current_page_has_questions = True
            admonition_content = match.group(1)
            
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
        
        return re.sub(pattern, replace_assessment, html, flags=re.DOTALL)

    def _parse_question_config_from_html(self, html_content):
        """Parse question configuration from HTML content while preserving rich content."""
        import re
        
        config = {
            'question': '',
            'type': 'short',
            'show_answer': True,
            'marks': 0,
            'placeholder': 'Enter your answer...',
            'answer': ''
        }
        
        # Simple approach: extract pieces we recognize and build the question content
        question_content_parts = []
        remaining_html = html_content
        
        # 1. Find and extract the question text (first paragraph starting with "question:")
        question_match = re.search(r'<p[^>]*>question:\s*(.*?)</p>', remaining_html, re.DOTALL)
        if question_match:
            question_text = question_match.group(1).strip()
            if question_text:
                question_content_parts.append(f'<p>{question_text}</p>')
            # Remove this paragraph from remaining HTML
            remaining_html = remaining_html.replace(question_match.group(0), '', 1)
        
        # 2. Find and extract Mermaid diagrams
        mermaid_matches = re.findall(r'<pre class="mermaid"><code>.*?</code></pre>', remaining_html, re.DOTALL)
        for mermaid_html in mermaid_matches:
            question_content_parts.append(mermaid_html)
            # Remove from remaining HTML
            remaining_html = remaining_html.replace(mermaid_html, '', 1)
        
        # 3. Find and extract code blocks
        code_matches = re.findall(r'<div class="language-[^"]*"[^>]*>.*?</div>', remaining_html, re.DOTALL)
        for code_html in code_matches:
            question_content_parts.append(code_html)
            # Remove from remaining HTML
            remaining_html = remaining_html.replace(code_html, '', 1)
        
        # 4. Find and extract image paragraphs
        img_matches = re.findall(r'<p[^>]*>\s*<img[^>]*>\s*</p>', remaining_html, re.DOTALL)
        for img_html in img_matches:
            question_content_parts.append(img_html)
            # Remove from remaining HTML
            remaining_html = remaining_html.replace(img_html, '', 1)
        
        # 5. Parse configuration from remaining paragraphs
        config_paragraphs = re.findall(r'<p[^>]*>(.*?)</p>', remaining_html, re.DOTALL)
        for p_content in config_paragraphs:
            # Extract clean text from paragraph
            clean_text = re.sub(r'<[^>]+>', '', p_content).strip()
            
            # Parse configuration lines
            lines = clean_text.split('\n')
            content_lines = []
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                    
                # Check if this line is configuration
                if ':' in line:
                    parts = line.split(':', 1)
                    if len(parts) == 2:
                        key = parts[0].strip()
                        value = parts[1].strip()
                        
                        if key in config:
                            # This is a configuration line
                            if key == 'show_answer':
                                config[key] = value.lower() in ['true', 'yes', '1']
                            elif key == 'marks':
                                try:
                                    config[key] = int(value)
                                except ValueError:
                                    config[key] = 0
                            else:
                                config[key] = value
                            continue
                
                # Not a config line, add to content
                content_lines.append(line)
            
            # Add any non-config content to question
            if content_lines:
                content_text = '\n'.join(content_lines).strip()
                if content_text:
                    question_content_parts.append(f'<p>{content_text}</p>')
        
        # Combine all question content parts
        config['question'] = ''.join(question_content_parts)
        
        return config

    def _parse_assessment_with_config_from_html(self, html_content):
        """Parse assessment configuration and questions from HTML content."""
        import re
        
        # Default assessment configuration
        assessment_config = {
            'shuffle': None,  # None means use global setting
            'title': 'Assessment'
        }
        
        # Split content by horizontal rules (---) which separate questions
        # Look for <hr> tags or other separators
        question_blocks = re.split(r'<hr[^>]*>|---', html_content)
        
        questions = []
        first_block = True
        
        for block in question_blocks:
            block = block.strip()
            if not block:
                continue
                
            if first_block:
                # First block might contain assessment-level configuration
                first_block = False
                
                # Look for assessment config in the first block
                config_lines = []
                question_content = []
                
                # Split by paragraphs to find config vs content
                html_blocks = re.split(r'</p>|</div>', block)
                
                for html_block in html_blocks:
                    html_block = html_block.strip()
                    if not html_block:
                        continue
                        
                    # Remove opening tags
                    clean_block = re.sub(r'^<[^>]+>', '', html_block)
                    
                    # Check if this looks like configuration
                    if re.match(r'^\s*(title|shuffle)\s*:', clean_block):
                        config_line = re.sub(r'<[^>]+>', '', clean_block).strip()
                        if ':' in config_line:
                            key, value = config_line.split(':', 1)
                            key = key.strip()
                            value = value.strip()
                            
                            if key == 'shuffle':
                                assessment_config['shuffle'] = value.lower() in ['true', 'yes', '1']
                            elif key == 'title':
                                assessment_config['title'] = value
                    else:
                        # This is question content
                        if clean_block.strip():
                            question_content.append(html_block)
                
                # If there's question content in the first block, parse it as a question
                if question_content:
                    question_html = ''.join(question_content)
                    config = self._parse_question_config_from_html(question_html)
                    if config['question']:
                        questions.append(config)
            else:
                # Parse as regular question
                config = self._parse_question_config_from_html(block)
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

    def _parse_question_config(self, content):
        """Parse question configuration from content."""
        config = {
            'question': '',
            'type': 'short',
            'show_answer': True,
            'marks': 0,
            'placeholder': 'Enter your answer...',
            'answer': ''
        }
        
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
                    if key in ['show_answer']:
                        config[key] = value.lower() in ['true', 'yes', '1']
                    elif key in ['marks']:
                        try:
                            config[key] = int(value)
                        except ValueError:
                            config[key] = 0
                    else:
                        config[key] = value
        
        return config

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

    def _parse_assessment_questions(self, content):
        """Parse multiple questions from assessment content (legacy method)."""
        _, questions = self._parse_assessment_with_config(content)
        return questions

    def _generate_question_html(self, config, question_id):
        """Generate HTML for a single question."""
        rows = self.config.get('default_answer_rows', 3) if config['type'] == 'short' else 6
        char_counter = self._get_character_counter_html(question_id) if self.config.get('show_character_count', True) else ''
        
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
            rows="{rows}" 
            placeholder="{config['placeholder']}"
            oninput="updateCharCount_{question_id}(); autoSave_{question_id}();"
        ></textarea>
        {char_counter}
    </div>
    
    <div class="button-group">
        <button onclick="submitAnswer_{question_id}()" class="submit-btn">Submit Answer</button>
    </div>
    
    <div id="feedback_{question_id}" class="feedback" style="display: none;"></div>
</div>

<script>
{self._generate_question_javascript(question_id, config)}
</script>
'''
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
            rows = self.config.get('default_answer_rows', 3) if config['type'] == 'short' else 6
            char_counter = self._get_character_counter_html(question_id) if self.config.get('show_character_count', True) else ''
            
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
            rows="{rows}" 
            placeholder="{config['placeholder']}"
            oninput="updateCharCount_{question_id}(); autoSaveAssessment_{assessment_id}();"
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

<script>
{self._generate_assessment_javascript(assessment_id, questions)}
</script>
'''
        return html

    def _get_character_counter_html(self, question_id):
        """Generate character counter HTML."""
        return f'<div id="charCount_{question_id}" class="char-count">0 characters</div>'

    def _generate_question_javascript(self, question_id, config):
        """Generate JavaScript for individual questions."""
        enable_auto_save = str(self.config.get('enable_auto_save', True)).lower()
        
        return f'''
function updateCharCount_{question_id}() {{
    const textarea = document.getElementById('answer_{question_id}');
    const counter = document.getElementById('charCount_{question_id}');
    if (counter) {{
        counter.textContent = textarea.value.length + ' characters';
    }}
}}

function autoSave_{question_id}() {{
    if ({enable_auto_save}) {{
        const answer = document.getElementById('answer_{question_id}').value;
        localStorage.setItem('freetext_answer_{question_id}', answer);
    }}
}}

function submitAnswer_{question_id}() {{
    const answer = document.getElementById('answer_{question_id}').value;
    const feedback = document.getElementById('feedback_{question_id}');
    
    if (answer.trim() === '') {{
        feedback.innerHTML = '<div class="warning">Please enter an answer before submitting.</div>';
        feedback.style.display = 'block';
        return;
    }}
    
    let successMessage = '<div class="success">Answer submitted successfully!</div>';
    
    // Automatically show answer if show_answer is enabled
    if ({str(config.get('show_answer', False)).lower()}) {{
        successMessage += '<div class="answer-display"><strong>Sample Answer:</strong><br>{config.get("answer", "No sample answer provided.")}</div>';
    }}
    
    feedback.innerHTML = successMessage;
    feedback.style.display = 'block';
    
    // Save submission
    localStorage.setItem('freetext_submitted_{question_id}', 'true');
    localStorage.setItem('freetext_answer_{question_id}', answer);
}}

// Auto-load saved answers
document.addEventListener('DOMContentLoaded', function() {{
    const savedAnswer = localStorage.getItem('freetext_answer_{question_id}');
    if (savedAnswer) {{
        document.getElementById('answer_{question_id}').value = savedAnswer;
        updateCharCount_{question_id}();
    }}
}});
'''

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
    
    if (!allAnswered) {{
        assessmentFeedback.innerHTML = '<div class="warning">Please answer all questions before submitting.</div>';
        assessmentFeedback.style.display = 'block';
        return;
    }}
    
    assessmentFeedback.innerHTML = '<div class="success">Assessment submitted successfully!</div>';
    assessmentFeedback.style.display = 'block';
    
    // Automatically show answers for questions with show_answer enabled
    {chr(10).join(f'''
    if ({str(questions[i].get('show_answer', False)).lower()}) {{
        const feedback_{qid} = document.getElementById('feedback_{qid}');
        feedback_{qid}.innerHTML = '<div class="answer-display"><strong>Sample Answer:</strong><br>{questions[i].get("answer", "No sample answer provided.")}</div>';
        feedback_{qid}.style.display = 'block';
    }}''' for i, qid in enumerate(question_ids))}
    
    // Save submission
    localStorage.setItem('freetext_assessment_submitted_{assessment_id}', 'true');
    localStorage.setItem('freetext_assessment_{assessment_id}', JSON.stringify(answers));
}}

'''

        # Add character counters
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
        const questions = Array.from(questionsContainer.querySelectorAll('.assessment-question'));
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

// Auto-load saved assessment answers
document.addEventListener('DOMContentLoaded', function() {{
    // Shuffle questions first if enabled
    shuffleQuestions_{assessment_id}();
    
    const savedAssessment = localStorage.getItem('freetext_assessment_{assessment_id}');
    if (savedAssessment) {{
        const answers = JSON.parse(savedAssessment);
        {chr(10).join(f'''
        if (answers['{qid}']) {{
            document.getElementById('answer_{qid}').value = answers['{qid}'];
            updateCharCount_{qid}();
        }}''' for qid in question_ids)}
    }}
}});
'''
        
        return js

    def on_post_page(self, output, page, config, **kwargs):
        """Add CSS styling if enabled and questions were found."""
        # Check if this page has questions
        page_has_questions = self.page_questions.get(page.file.src_path, False)
        
        # Insert CSS if enabled and this page has questions
        if not self.config.get('enable_css', True) or not page_has_questions:
            return output
            
        css = self._generate_css()
        
        # Insert CSS before closing </head> tag
        if '</head>' in output:
            output = output.replace('</head>', css + '\n</head>')
        else:
            # Fallback: add at the beginning of the body
            output = css + '\n' + output
            
        return output

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
