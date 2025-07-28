# MkDocs Free-Text Questions Plugin

A comprehensive MkDocs plugin for adding interactive free-text input questions and assessments to your documentation. Perfect for educational content, tutorials, and training materials.

## ✨ Features

- **Interactive Questions**: Add free-text input questions directly to your documentation
- **Multi-Question Assessments**: Create comprehensive assessments with multiple questions
- **Rich Content Support**: Questions support Mermaid diagrams, code blocks, images, and markdown
- **Modern Syntax**: Clean `---` separator syntax for organized configuration
- **Material Theme Integration**: Seamlessly integrates with MkDocs Material theme, including automatic dark/light mode support
- **Flexible Configuration**: Customize appearance, behavior, and validation using comma-separated format
- **Question Shuffling**: Optional randomization of assessment question order
- **Character Counting**: Optional character counter for text inputs
- **Sample Answers**: Show/hide sample answers for learning reinforcement
- **Clean Separation**: Use `---` separator to cleanly separate question content from configuration

## 📝 New Syntax (v1.1.0+)

This plugin now uses a modern, clean syntax with the `---` separator:

```markdown
!!! freetext
    Your question content here (supports rich markdown, code, diagrams)
    ---
    marks: 5, type: long, placeholder: Your placeholder..., show_answer: true
```

**Key Benefits:**
- ✅ Cleaner separation between content and configuration
- ✅ Comma-separated configuration for better readability
- ✅ Supports complex rich content without conflicts
- ✅ Backward compatible with legacy format

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
    What is the capital of France?
    ---
    marks: 2, placeholder: Enter your answer here..., show_answer: true, answer: Paris is the capital of France.
```

### Rich Content Question Example

```markdown
!!! freetext
    Analyze this code and explain what it does:
    
    ```python
    def fibonacci(n):
        if n <= 1:
            return n
        return fibonacci(n-1) + fibonacci(n-2)
    ```
    
    What is the time complexity of this algorithm?
    ---
    marks: 10, type: long, rows: 6, placeholder: Explain the algorithm and its complexity...
```

### Question with Images and Diagrams

```markdown
!!! freetext
    Study the system architecture below:
    
    ![System Architecture](images/architecture.png)
    
    ```mermaid
    graph TD
        A[Client] --> B[Load Balancer]
        B --> C[Web Server 1]
        B --> D[Web Server 2]
        C --> E[Database]
        D --> E
    ```
    
    How would you scale this system to handle 10x more traffic?
    ---
    marks: 15, type: long, rows: 8
```

### Assessment Example

```markdown
!!! freetext-assessment
    title: Python Basics Assessment
    shuffle: true
    
    What is a variable in Python?
    ---
    marks: 3, placeholder: Describe what a variable is...
    
    <hr>
    
    Explain the difference between a list and a tuple.
    ---
    marks: 5, placeholder: Compare lists and tuples...
```

## 📖 Documentation

Visit our **[comprehensive documentation](https://d-kearsey.github.io/mkdocs-freetext/)** with live interactive demos, complete installation guide, and examples you can copy-paste.

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
    Analyze the following Python code and explain what it does:
    
    ```python
    def fibonacci(n):
        if n <= 1:
            return n
        return fibonacci(n-1) + fibonacci(n-2)
    ```
    
    What is the time complexity of this implementation?
    ---
    marks: 5, placeholder: Explain the code and analyze its complexity...
```

### Assessment with Mermaid Diagram

```markdown
!!! freetext-assessment
    title: System Design Assessment
    
    Based on this system architecture, identify potential bottlenecks:
    
    ```mermaid
    graph TD
        A[User] --> B[Load Balancer]
        B --> C[Web Server 1]
        B --> D[Web Server 2]
        C --> E[Database]
        D --> E
    ```
    ---
    marks: 10, placeholder: Identify and explain potential bottlenecks...
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🔗 Links

- [PyPI Package](https://pypi.org/project/mkdocs-freetext/) (Available after publishing)
- [📖 Documentation & Live Demo](https://d-kearsey.github.io/mkdocs-freetext/)
- [GitHub Repository](https://github.com/D-Kearsey/mkdocs-freetext)
- [Issue Tracker](https://github.com/D-Kearsey/mkdocs-freetext/issues)

## 🏆 Why Choose MkDocs Free-Text?

- **Educational Focus**: Built specifically for learning and assessment
- **Modern Design**: Beautiful, responsive interface that works everywhere
- **Rich Content**: Support for diagrams, code, images, and complex markdown
- **Developer Friendly**: Clean API, extensive documentation, and active maintenance
- **Production Ready**: Used in educational institutions and corporate training
