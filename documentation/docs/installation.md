# Installation Guide

## Requirements

- Python 3.7+
- MkDocs 1.0+
- MkDocs Material theme (recommended)

## Installation

### Via PyPI (Recommended)

```bash
pip install mkdocs-freetext
```

### From Source

```bash
git clone https://github.com/D-Kearsey/mkdocs-freetext.git
cd mkdocs-freetext
pip install -e .
```

## Configuration

### Basic Setup

Add the plugin to your `mkdocs.yml`:

```yaml
plugins:
  - freetext
```

### Quick Start with New Syntax (v1.1.0+)

Create your first question using the modern syntax:

```markdown
!!! freetext
    What is your favorite programming language and why?
    ---
    marks: 5, type: long, placeholder: Share your thoughts..., show_answer: true, answer: This is a sample answer explaining why Python is great for beginners.
```

### With Material Theme

For the best experience, use with Material theme:

```yaml
theme:
  name: material
  features:
    - content.code.copy
    - navigation.sections

plugins:
  - search
  - freetext:
      show_character_count: true

markdown_extensions:
  - admonition
  - pymdownx.superfences:
      custom_fences:
        - name: mermaid
          class: mermaid
          format: !!python/name:pymdownx.superfences.fence_code_format
```

### Plugin Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `question_class` | string | `freetext-question` | CSS class for question containers |
| `assessment_class` | string | `freetext-assessment` | CSS class for assessment containers |
| `enable_css` | boolean | `true` | Enable built-in CSS styling |
| `shuffle_questions` | boolean | `false` | Shuffle question order in assessments |
| `show_character_count` | boolean | `true` | Show character counter on text inputs |

### Example Configuration

```yaml
plugins:
  - freetext:
      question_class: "my-question"
      assessment_class: "my-assessment" 
      enable_css: true
      shuffle_questions: false
      show_character_count: true
```

## Verification

After installation, create a test page to verify everything works:

```markdown
# Test Page

!!! freetext
    question: What is 2 + 2?
    placeholder: Enter your answer...
    marks: 1
```

Then run:

```bash
mkdocs serve
```

Visit `http://localhost:8000` and you should see your interactive question!

## Troubleshooting

### Plugin Not Loading

1. Ensure the plugin is installed: `pip list | grep mkdocs-freetext`
2. Check your `mkdocs.yml` syntax
3. Verify MkDocs version: `mkdocs --version`

### Styling Issues

1. Ensure Material theme is installed: `pip install mkdocs-material`
2. Check that `enable_css: true` in plugin configuration
3. Verify admonition extension is enabled

### Need Help?

- [GitHub Issues](https://github.com/D-Kearsey/mkdocs-freetext/issues)
- [Documentation](https://d-kearsey.github.io/mkdocs-freetext/)

---

Next: [Try the Live Demo →](demo.md)
