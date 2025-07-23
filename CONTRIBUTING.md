# Contributing to MkDocs Free-Text Plugin

Thank you for your interest in contributing to the MkDocs Free-Text Plugin! This guide will help you get started.

## 🚀 Quick Start for Contributors

1. **Fork the repository** on GitHub
2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/your-username/mkdocs-freetext.git
   cd mkdocs-freetext
   ```
3. **Create a virtual environment**:
   ```bash
   python -m venv env
   source env/bin/activate  # On Windows: env\Scripts\activate
   ```
4. **Install development dependencies**:
   ```bash
   pip install -e .[dev]
   ```

## 🧪 Running Tests

Run the test suite to ensure everything works:

```bash
python -m pytest tests/ -v
```

Run tests with coverage:

```bash
python -m pytest tests/ --cov=mkdocs_freetext --cov-report=html
```

## 🔧 Development Setup

### Code Quality Tools

We use several tools to maintain code quality:

```bash
# Install development tools
pip install black flake8 mypy pytest pytest-cov

# Format code
black mkdocs_freetext/ tests/

# Check code style
flake8 mkdocs_freetext/ tests/

# Type checking
mypy mkdocs_freetext/
```

### Testing Your Changes

1. **Create a test site**:
   ```bash
   mkdir test-site
   cd test-site
   mkdocs new .
   ```

2. **Configure test site** (`mkdocs.yml`):
   ```yaml
   site_name: Test Site
   theme:
     name: material
   plugins:
     - freetext
   ```

3. **Add test content** to `docs/index.md`:
   ```markdown
   # Test Page
   
   !!! freetext
       question: What is your name?
       marks: 1
   ```

4. **Serve and test**:
   ```bash
   mkdocs serve
   ```

## 📝 Contribution Guidelines

### Code Style

- Follow PEP 8 conventions
- Use Black for code formatting
- Add type hints where appropriate
- Write docstrings for all public methods
- Keep line length under 88 characters

### Commit Messages

Follow conventional commit format:

```
feat: add support for custom CSS classes
fix: resolve Material theme dark mode issue
docs: update installation instructions
test: add tests for assessment parsing
refactor: simplify HTML generation logic
```

### Pull Request Process

1. **Create a feature branch**:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes** following the guidelines above

3. **Write or update tests** for your changes

4. **Update documentation** if needed

5. **Ensure all tests pass**:
   ```bash
   python -m pytest tests/
   ```

6. **Submit a pull request** with:
   - Clear description of changes
   - Reference to any related issues
   - Screenshots for UI changes

## 🐛 Reporting Issues

When reporting bugs, please include:

- MkDocs version
- Python version
- Plugin version
- Minimal reproduction case
- Expected vs actual behavior
- Error messages or logs

Use this template:

```markdown
**Environment:**
- MkDocs: v1.4.2
- Python: 3.9.1
- Plugin: v1.0.0
- Theme: Material v8.5.8

**Description:**
Brief description of the issue...

**Steps to Reproduce:**
1. Create a question with...
2. Build the site...
3. See error...

**Expected Behavior:**
What should happen...

**Actual Behavior:**
What actually happens...
```

## 💡 Feature Requests

For new features:

1. **Check existing issues** to avoid duplicates
2. **Describe the use case** and why it's needed
3. **Provide examples** of how it would work
4. **Consider backwards compatibility**

## 🏗️ Architecture Overview

### Key Components

- **`plugin.py`**: Main plugin class and hooks
- **HTML Processing**: Parses admonitions and generates interactive elements
- **CSS Generation**: Creates Material theme-compatible styles
- **JavaScript**: Handles user interactions and state management

### Plugin Hooks Used

- `on_page_content`: Processes HTML after markdown conversion
- `on_post_page`: Injects CSS when questions are present

### Content Processing Flow

1. MkDocs processes markdown (including Mermaid, code blocks)
2. Plugin detects freetext admonitions in HTML
3. Plugin extracts and preserves rich content
4. Plugin generates interactive question HTML
5. Plugin injects CSS for styling

## 🧪 Testing Guidelines

### Test Categories

1. **Unit Tests**: Test individual functions
2. **Integration Tests**: Test plugin hooks and workflows
3. **UI Tests**: Test generated HTML structure
4. **Theme Tests**: Test Material theme integration

### Writing Tests

```python
def test_question_parsing(self):
    """Test that questions are parsed correctly."""
    html_input = '''
    <p>question: Test question</p>
    <p>marks: 5</p>
    '''
    
    config = self.plugin._parse_question_config_from_html(html_input)
    
    self.assertIn('Test question', config['question'])
    self.assertEqual(config['marks'], 5)
```

### Test Coverage

Aim for:
- 90%+ line coverage
- Test all public methods
- Test error conditions
- Test edge cases

## 📚 Documentation

### Writing Documentation

- Use clear, concise language
- Include code examples
- Add screenshots for complex features
- Keep examples up-to-date

### Documentation Structure

```
docs/
├── installation.md     # Setup instructions
├── configuration.md    # All configuration options
├── question-syntax.md  # How to write questions
├── examples.md         # Real-world examples
├── theming.md          # Customization guide
└── api.md              # Plugin API reference
```

## 🎉 Recognition

Contributors will be recognized in:

- `CONTRIBUTORS.md` file
- Release notes
- Documentation credits

## 📬 Getting Help

- **GitHub Issues**: For bugs and feature requests
- **GitHub Discussions**: For questions and ideas
- **Email**: For private inquiries

## 📄 License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

Thank you for contributing to make MkDocs Free-Text Plugin better! 🚀
