# MkDocs Free-Text Questions Plugin

A comprehensive MkDocs plugin for adding **interactive free-text questions and assessments** to your documentation. Perfect for educational content, tutorials, and training materials.

![Plugin Demo](https://img.shields.io/badge/Live%20Demo-Available-brightgreen?style=for-the-badge)
![PyPI](https://img.shields.io/pypi/v/mkdocs-freetext?style=for-the-badge)
![License](https://img.shields.io/github/license/D-Kearsey/mkdocs-freetext?style=for-the-badge)

## ✨ Key Features

- **🎯 Interactive Questions**: Add free-text input questions directly to your documentation
- **📝 Multi-Question Assessments**: Create comprehensive assessments with multiple questions  
- **🎨 Rich Content Support**: Questions support Mermaid diagrams, code blocks, images, and markdown
- **🌓 Material Theme Integration**: Seamless integration with automatic dark/light mode support
- **💾 Persistent Storage**: Auto-saves user answers in browser localStorage
- **🔀 Question Shuffling**: Optional randomization of assessment question order
- **📊 Character Counting**: Optional character counter for text inputs
- **💡 Sample Answers**: Show/hide sample answers for learning reinforcement

## 🚀 Quick Start

### Installation

```bash
pip install mkdocs-freetext
```

### Basic Setup

Add the plugin to your `mkdocs.yml`:

```yaml
plugins:
  - freetext
```

### Your First Question

```markdown
!!! freetext
    What is the capital of France?
    
    ---
    
    placeholder: Enter your answer here...
    marks: 2
    show_answer: true
    answer: Paris is the capital of France.
```

## 📖 Navigation

- **[Installation Guide](installation.md)** - Complete setup instructions
- **[Live Demo](demo.md)** - See the plugin in action with working examples
- **[Configuration](configuration.md)** - All available options and settings
- **[Advanced Usage](advanced.md)** - Advanced features and customization

## 🏆 Why Choose This Plugin?

- **Educational Focus**: Built specifically for learning and assessment
- **Modern Design**: Beautiful, responsive interface that works everywhere
- **Rich Content**: Support for diagrams, code, images, and complex markdown
- **Developer Friendly**: Clean API, extensive documentation, and active maintenance
- **Production Ready**: Used in educational institutions and corporate training

---

Ready to get started? Check out our **[Live Demo](demo.md)** to see the plugin in action!
