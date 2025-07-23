# MkDocs Free Text Questions Plugin

Welcome to the MkDocs Free Text Questions Plugin documentation!

## Overview

This plugin adds interactive free text questions to your MkDocs documentation. It allows you to create engaging educational content where readers can type answers and receive feedback.

## Features

- Easy-to-use syntax based on MkDocs admonitions
- Interactive text input fields
- Answer checking with feedback
- Customizable styling
- Show/hide answer functionality

## Installation

Install the plugin using pip:

```bash
pip install mkdocs-freetext
```

## Configuration

Add the plugin to your `mkdocs.yml`:

```yaml
plugins:
  - freetext:
      question_class: 'freetext-question'     # CSS class for question containers
      answer_class: 'freetext-answer'         # CSS class for answer containers
      container_class: 'freetext-container'   # CSS class for overall containers
      enable_css: true                        # Whether to include default CSS
```

## Usage

Use the special `freetext` admonition syntax in your markdown:

```markdown
!!! freetext "What is the capital of France?"
    Paris

!!! freetext "Explain the concept of inheritance in OOP"
    Inheritance is a mechanism where a new class inherits properties and methods from an existing class. It promotes code reusability and establishes a relationship between classes.
```

## Examples

### Simple Question

```markdown
!!! freetext "What is 2 + 2?"
    4
```

### Complex Question

```markdown
!!! freetext "Describe the benefits of using version control"
    Version control helps track changes, collaborate with others, maintain history, 
    enable rollbacks, and manage different versions of code or documents.
```

## Customization

### Custom CSS Classes

You can customize the appearance by providing your own CSS classes:

```yaml
plugins:
  - freetext:
      question_class: 'my-custom-question'
      answer_class: 'my-custom-answer'
      container_class: 'my-custom-container'
      enable_css: false  # Disable default CSS to use your own
```

### Custom Styling

If you disable the default CSS (`enable_css: false`), you can provide your own styles:

```css
.my-custom-container {
    border: 2px solid #007bff;
    border-radius: 10px;
    padding: 20px;
    margin: 15px 0;
}

.my-custom-question textarea {
    width: 100%;
    min-height: 100px;
    border: 1px solid #ccc;
    border-radius: 5px;
    padding: 10px;
}

.my-custom-question button {
    background-color: #28a745;
    color: white;
    padding: 10px 20px;
    border: none;
    border-radius: 5px;
    cursor: pointer;
    margin: 5px;
}
```

## Development

See the [GitHub repository](https://github.com/your-username/mkdocs-freetext) for development instructions and to report issues.

## License

This plugin is licensed under the MIT License.
