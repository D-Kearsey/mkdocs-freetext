# MkDocs Free-Text Questions Plugin

A comprehensive MkDocs plugin for adding interactive free-text input questions and assessments to your documentation. Perfect for educational content, tutorials, and training materials.

## ✨ Features

- **Interactive Questions**: Add free-text input questions directly to your documentation
- **Multi-Question Assessments**: Create comprehensive assessments with multiple questions
- **Rich Content Support**: Questions support Mermaid diagrams, code blocks, images, and markdown
- **Material Theme Integration**: Seamlessly integrates with MkDocs Material theme, including automatic dark/light mode support
- **Persistent Storage**: Auto-saves user answers in browser localStorage
- **Flexible Configuration**: Customize appearance, behavior, and validation
- **Question Shuffling**: Optional randomization of assessment question order
- **Character Counting**: Optional character counter for text inputs
- **Sample Answers**: Show/hide sample answers for learning reinforcement

## 🚀 Quick Start

### Installation

```bash
pip install mkdocs-freetext
```

### Basic Configuration

Add the plugin to your `mkdocs.yml`:

```yaml
plugins:
  - freetext
```

### Simple Question Example

```markdown
!!! freetext
    question: What is the capital of France?
    placeholder: Enter your answer here...
    marks: 2
    show_answer: true
    answer: Paris is the capital of France.
```

### Assessment Example

```markdown
!!! freetext-assessment
    title: Python Basics Assessment
    shuffle: true
    
    question: What is a variable in Python?
    marks: 3
    placeholder: Describe what a variable is...
    
    ---
    
    question: Explain the difference between a list and a tuple.
    marks: 5
    placeholder: Compare lists and tuples...
```

## 📖 Documentation

- **[Configuration Reference](docs/configuration.md)** - All available options
- **[Question Syntax](docs/question-syntax.md)** - How to create questions
- **[Assessment Syntax](docs/assessment-syntax.md)** - How to create assessments
- **[Rich Content](docs/rich-content.md)** - Using diagrams, code, and images
- **[Theming](docs/theming.md)** - Customizing appearance
- **[Examples](docs/examples.md)** - Real-world usage examples

## 🎨 Material Theme Integration

This plugin is designed to work seamlessly with the Material for MkDocs theme:

- Automatic light/dark mode support using Material CSS variables
- Consistent styling with Material design principles
- Responsive design that works on all devices
- Admonition-based syntax that integrates naturally with Material

## 🔧 Configuration Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `question_class` | string | `freetext-question` | CSS class for question containers |
| `assessment_class` | string | `freetext-assessment` | CSS class for assessment containers |
| `enable_css` | boolean | `true` | Enable built-in CSS styling |
| `shuffle_questions` | boolean | `false` | Shuffle question order in assessments |
| `show_character_count` | boolean | `true` | Show character counter on text inputs |

## 🌟 Examples

### Basic Question with Rich Content

```markdown
!!! freetext
    question: Analyze the following Python code and explain what it does:
    
    ```python
    def fibonacci(n):
        if n <= 1:
            return n
        return fibonacci(n-1) + fibonacci(n-2)
    ```
    
    What is the time complexity of this implementation?
    
    marks: 5
    placeholder: Explain the code and analyze its complexity...
```

### Assessment with Mermaid Diagram

```markdown
!!! freetext-assessment
    title: System Design Assessment
    
    question: Based on this system architecture, identify potential bottlenecks:
    
    ```mermaid
    graph TD
        A[User] --> B[Load Balancer]
        B --> C[Web Server 1]
        B --> D[Web Server 2]
        C --> E[Database]
        D --> E
    ```
    
    marks: 10
    placeholder: Identify and explain potential bottlenecks...
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🔗 Links

- [PyPI Package](https://pypi.org/project/mkdocs-freetext/)
- [GitHub Repository](https://github.com/D-Kearsey/mkdocs-freetext)
- [Documentation](https://d-kearsey.github.io/mkdocs-freetext/)
- [Issue Tracker](https://github.com/D-Kearsey/mkdocs-freetext/issues)

## 🏆 Why Choose MkDocs Free-Text?

- **Educational Focus**: Built specifically for learning and assessment
- **Modern Design**: Beautiful, responsive interface that works everywhere
- **Rich Content**: Support for diagrams, code, images, and complex markdown
- **Developer Friendly**: Clean API, extensive documentation, and active maintenance
- **Production Ready**: Used in educational institutions and corporate training
