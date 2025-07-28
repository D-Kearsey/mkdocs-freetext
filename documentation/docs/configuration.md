# Configuration Reference

Complete reference for all configuration options available in the MkDocs Free-Text Questions Plugin.

## 🆕 New Syntax (v1.1.0+)

The plugin now supports a modern, clean syntax using the `---` separator:

### Single Question Format
```markdown
!!! freetext
    Your question content here (supports rich markdown)
    ---
    marks: 5, type: long, placeholder: Your answer here..., show_answer: true
```

### Assessment Format
```markdown
!!! freetext-assessment
    title: My Assessment, shuffle: true
    
    First question content here
    ---
    marks: 5, type: short
    
    <hr>
    
    Second question content here
    ---
    marks: 10, type: long, rows: 8
```

**Key Benefits:**
- ✅ Clean separation between content and configuration
- ✅ Comma-separated configuration for better readability
- ✅ Supports complex rich content without conflicts
- ✅ Backward compatible with legacy format

## Plugin Configuration

Configure the plugin in your `mkdocs.yml` file:

```yaml
plugins:
  - freetext:
      # CSS Classes
      question_class: "freetext-question"
      assessment_class: "freetext-assessment"
      answer_class: "freetext-answer"
      container_class: "freetext-container"
      
      # Styling & Appearance
      enable_css: true
      dark_mode_support: true
      
      # Functionality
      shuffle_questions: false
      show_character_count: true
      # Note: Auto-save functionality has been removed in v1.1.0+
      
      # Default Values
      default_answer_rows: 3
      default_long_answer_rows: 6
      default_placeholder: "Enter your answer..."
      default_marks: 0
      default_show_answer: true
      default_question_type: "short"
```

## Options Reference

### CSS Classes

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `question_class` | string | "freetext-question" | CSS class for individual question containers |
| `assessment_class` | string | "freetext-assessment" | CSS class for assessment containers |
| `answer_class` | string | "freetext-answer" | CSS class for answer input areas |
| `container_class` | string | "freetext-container" | CSS class for main containers |

### Styling & Appearance

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `enable_css` | Boolean | true | Enable or disable built-in CSS styling |
| `dark_mode_support` | Boolean | true | Enable dark mode CSS support |

### Functionality

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `shuffle_questions` | Boolean | false | Randomly shuffle question order in assessments |
| `show_character_count` | Boolean | true | Show character counter on text areas |

**Note:** Auto-save functionality has been removed in v1.1.0+ for improved security and reduced complexity.

### Default Values

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `default_answer_rows` | number | 3 | Default rows for short answer text areas |
| `default_long_answer_rows` | number | 6 | Default rows for long answer text areas |
| `default_placeholder` | string | "Enter your answer..." | Default placeholder text |
| `default_marks` | number | 0 | Default marks value |
| `default_show_answer` | Boolean | true | Default show_answer setting |
| `default_question_type` | string | "short" | Default question type ("short" or "long") |

### 🔍 Debug & Development (v1.2.0+)

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `debug` | Boolean | false | Enable detailed debug logging for troubleshooting |
| `debug_output_dir` | string | null | Optional directory for debug file output |

#### Debug Mode Configuration

Enable comprehensive logging for development and troubleshooting:

```yaml
plugins:
  - freetext:
      debug: true
      debug_output_dir: "./debug"  # Optional: specify custom debug directory
```

**Debug Mode Features:**
- **Professional Logging System**: Uses Python's standard `logging` module with proper categorization
- **Multiple Log Levels**: DEBUG (verbose), INFO (important events), WARNING (issues), ERROR (failures)
- **Clean Output**: Quiet operation by default, detailed logging only when enabled
- **Configurable Debug Files**: Optional HTML comparison files for content processing analysis
- **Configuration Validation**: Early detection of configuration issues with helpful error messages
- **Better Error Messages**: Actionable warnings with suggested solutions

**Example Debug Output:**
```
2025-01-28 10:30:15 - mkdocs_freetext.plugin - INFO - FreetextPlugin initialized successfully
2025-01-28 10:30:16 - mkdocs_freetext.plugin - INFO - Processed freetext questions on page demo.md
2025-01-28 10:30:16 - mkdocs_freetext.plugin - DEBUG - Generated JavaScript for question abc123
```

## Question Syntax

The plugin supports two syntax formats: **Modern Separator Syntax** (recommended) and **Legacy Format** (for backwards compatibility).

### Modern Separator Syntax (Recommended)

Use the `---` separator to cleanly separate question content from configuration:

```markdown
!!! freetext
    What is the capital of France?
    
    This question can include **rich content** like:
    - Markdown formatting
    - Code blocks
    - Images
    - Mermaid diagrams
    
    ---
    
    marks: 2
    placeholder: Enter your answer here...
    show_answer: true
    answer: Paris is the capital of France.
```

### Legacy Format (Backwards Compatibility)

```markdown
!!! freetext
    question: Your question text here
    placeholder: Placeholder text for the input
    marks: 5
    show_answer: true
    answer: The sample answer
```

### Question Parameters

| Parameter | Required | Type | Default | Description |
|-----------|----------|------|---------|-------------|
| `marks` | ❌ No | number | 0 | Point value for the question |
| `placeholder` | ❌ No | string | "Enter your answer..." | Placeholder text for the input field |
| `show_answer` | ❌ No | boolean | true | Show/hide sample answer button |
| `answer` | ❌ No | string | "" | Sample answer text |
| `type` | ❌ No | string | "short" | Question type: "short" or "long" |
| `rows` | ❌ No | number | 3 (short), 6 (long) | Number of textarea rows |

## Assessment Syntax

### Modern Assessment Syntax (Recommended)

Use `---` separators to define multiple questions within an assessment:

```markdown
!!! freetext-assessment
    title: Python Fundamentals Assessment
    shuffle: true
    
    What is a variable in Python?
    
    ---
    
    marks: 3
    placeholder: Describe variables...
    show_answer: true
    answer: A variable in Python is a name that refers to a value stored in memory.
    
    ---
    
    Explain the difference between a list and a tuple.
    
    Include examples in your answer.
    
    ---
    
    marks: 5
    placeholder: Compare lists and tuples...
    show_answer: true
    answer: Lists are mutable and use square brackets [1,2,3]. Tuples are immutable and use parentheses (1,2,3).
```

### Legacy Assessment Format

```markdown
!!! freetext-assessment
    title: Assessment Title
    shuffle: true
    
    question: First question
    marks: 5
    placeholder: Answer here...
    
    ---
    
    question: Second question  
    marks: 3
    placeholder: Another answer...
```

### Assessment Parameters

| Parameter | Required | Type | Default | Description |
|-----------|----------|------|---------|-------------|
| `title` | ❌ No | string | "Assessment" | Title displayed above the assessment |
| `shuffle` | ❌ No | Boolean | false | Shuffle question order (overrides global setting) |

## Integration with Other Plugins

Works well with other MkDocs plugins:

```yaml
plugins:
  - search
  - freetext
  - mermaid2  # For diagram support
```

---

**Next**: [See Examples →](examples.md) | [Advanced Usage →](advanced.md)
