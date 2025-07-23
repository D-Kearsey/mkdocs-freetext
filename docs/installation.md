# Installation Guide

## Requirements

- Python 3.7+
- MkDocs 1.0+
- (Recommended) Material for MkDocs theme

## Installation Methods

### Via PyPI (Recommended)

```bash
pip install mkdocs-freetext
```

### From Source

```bash
git clone https://github.com/your-username/mkdocs-freetext.git
cd mkdocs-freetext
pip install -e .
```

## Basic Setup

1. Add the plugin to your `mkdocs.yml`:

```yaml
plugins:
  - freetext
```

2. (Optional) Configure with custom options:

```yaml
plugins:
  - freetext:
      question_class: "my-questions"
      assessment_class: "my-assessments"
      shuffle_questions: true
      show_character_count: false
```

## Verification

Create a test page with a simple question:

```markdown
# Test Page

!!! freetext
    question: What is 2 + 2?
    marks: 1
```

Build and serve your site:

```bash
mkdocs serve
```

You should see an interactive question with a text input area.

## Material Theme Integration

For the best experience, use with Material for MkDocs:

```yaml
theme:
  name: material
  features:
    - content.code.copy
  palette:
    - scheme: default
      toggle:
        icon: material/brightness-7
        name: Switch to dark mode
    - scheme: slate
      toggle:
        icon: material/brightness-4
        name: Switch to light mode

plugins:
  - freetext
```

The plugin automatically adapts to Material's light/dark theme switching.

## Troubleshooting

### Plugin Not Working

1. Ensure the plugin is installed: `pip list | grep mkdocs-freetext`
2. Check your `mkdocs.yml` syntax
3. Restart the MkDocs server after configuration changes

### Questions Not Appearing

1. Verify the admonition syntax (`!!! freetext`)
2. Check for indentation errors
3. Ensure required fields are present (`question:`)

### Styling Issues

1. Clear browser cache
2. Check if custom CSS conflicts with plugin styles
3. Verify Material theme is properly configured
