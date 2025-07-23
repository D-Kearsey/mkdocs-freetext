# Installation and Testing Guide

## Development Installation

For local development and testing:

```bash
# Clone or create your plugin directory
mkdir mkdocs-freetext
cd mkdocs-freetext

# Create the package structure (already done)
# Install in development mode
pip install -e .
```

## Testing the Plugin

Create a test MkDocs site to verify the plugin works:

```bash
# Create test site
mkdir test-site
cd test-site
mkdocs new .
```

Edit `mkdocs.yml`:
```yaml
site_name: Test Site
plugins:
  - freetext:
      show_character_count: true
      default_answer_rows: 4
```

Add test content to `docs/index.md`:
````markdown
# Test Free-Text Plugin

## Single Question
```freetext
question: What is your favorite color?
type: short
show_answer: true
marks: 0
placeholder: Enter your favorite color...
answer: Any color preference is valid
```

## Assessment
```freetext-assessment
question: Explain photosynthesis.
type: long
show_answer: true
marks: 10
answer: Photosynthesis is the process by which plants use sunlight, water, and carbon dioxide to produce oxygen and energy in the form of sugar.

---

question: Name the primary colors.
type: short
show_answer: true
marks: 5
answer: Red, blue, and yellow
```
````

Test the site:
```bash
mkdocs serve
```

Open your browser to `http://localhost:8000` to see the plugin in action!

## Publishing to PyPI

### First Time Setup

```bash
# Install build tools
pip install build twine

# Create accounts on PyPI and TestPyPI
# Configure ~/.pypirc with your credentials
```

### Build and Upload

```bash
# Build the package
python -m build

# Upload to TestPyPI first
twine upload --repository testpypi dist/*

# Test installation from TestPyPI
pip install --index-url https://test.pypi.org/simple/ mkdocs-freetext

# If everything works, upload to PyPI
twine upload dist/*
```

### User Installation

Once published, users can install with:

```bash
pip install mkdocs-freetext
```

## Running Tests

```bash
python -m pytest tests/
```

Your comprehensive MkDocs Free-Text Plugin is now complete and ready for use!
