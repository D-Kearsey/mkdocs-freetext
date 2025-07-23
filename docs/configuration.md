# Configuration Reference

## Plugin Configuration

Add configuration options under the `freetext` plugin in your `mkdocs.yml`:

```yaml
plugins:
  - freetext:
      question_class: "freetext-question"
      assessment_class: "freetext-assessment"
      enable_css: true
      shuffle_questions: false
      show_character_count: true
```

## Available Options

### `question_class`
- **Type**: String
- **Default**: `"freetext-question"`
- **Description**: CSS class applied to individual question containers

```yaml
plugins:
  - freetext:
      question_class: "my-custom-question"
```

### `assessment_class`
- **Type**: String
- **Default**: `"freetext-assessment"`
- **Description**: CSS class applied to assessment containers

```yaml
plugins:
  - freetext:
      assessment_class: "my-custom-assessment"
```

### `enable_css`
- **Type**: Boolean
- **Default**: `true`
- **Description**: Whether to include the plugin's built-in CSS styling

```yaml
plugins:
  - freetext:
      enable_css: false  # Use your own CSS
```

### `shuffle_questions`
- **Type**: Boolean
- **Default**: `false`
- **Description**: Whether to shuffle question order in assessments by default

```yaml
plugins:
  - freetext:
      shuffle_questions: true  # Randomize all assessments
```

### `show_character_count`
- **Type**: Boolean
- **Default**: `true`
- **Description**: Whether to show character counters on text inputs

```yaml
plugins:
  - freetext:
      show_character_count: false  # Hide character counters
```

## Question-Level Configuration

Each question supports the following options:

### `question`
- **Type**: String (supports HTML/Markdown)
- **Required**: Yes
- **Description**: The question text content

```markdown
!!! freetext
    question: What is the purpose of version control in software development?
```

### `type`
- **Type**: String
- **Default**: `"short"`
- **Options**: `"short"`, `"long"`
- **Description**: Type of answer expected (affects textarea height)

```markdown
!!! freetext
    question: Explain in detail...
    type: long
```

### `marks`
- **Type**: Integer
- **Default**: `0`
- **Description**: Point value for the question (displayed as badge)

```markdown
!!! freetext
    question: Simple question
    marks: 5
```

### `placeholder`
- **Type**: String
- **Default**: `"Enter your answer..."`
- **Description**: Placeholder text for the answer textarea

```markdown
!!! freetext
    question: Your favorite color?
    placeholder: Type your favorite color here...
```

### `show_answer`
- **Type**: Boolean
- **Default**: `true`
- **Description**: Whether to show sample answer after submission

```markdown
!!! freetext
    question: What is 2 + 2?
    show_answer: true
    answer: The answer is 4.
```

### `answer`
- **Type**: String (supports HTML/Markdown)
- **Description**: Sample answer to display when `show_answer` is true

```markdown
!!! freetext
    question: Explain variables in Python
    answer: |
        Variables in Python are containers for storing data values.
        They are created when you assign a value to them.
```

## Assessment-Level Configuration

Assessments support additional configuration:

### `title`
- **Type**: String
- **Default**: `"Assessment"`
- **Description**: Title displayed at the top of the assessment

```markdown
!!! freetext-assessment
    title: Python Fundamentals Quiz
    
    question: What is a function?
    marks: 3
```

### `shuffle`
- **Type**: Boolean
- **Default**: Uses global `shuffle_questions` setting
- **Description**: Whether to randomize question order for this assessment

```markdown
!!! freetext-assessment
    title: Randomized Quiz
    shuffle: true
    
    question: First question
    ---
    question: Second question
```

## Material Theme Variables

The plugin uses Material theme CSS variables for consistent styling:

- `--md-default-fg-color`: Text color
- `--md-default-bg-color`: Background color
- `--md-code-bg-color`: Code/input background
- `--md-primary-fg-color`: Accent colors (buttons, links)
- `--md-default-fg-color--lighter`: Border colors

## Custom CSS Integration

To override default styles:

```css
/* Custom question styling */
.freetext-question {
    border-left: 4px solid var(--md-primary-fg-color);
    background: linear-gradient(45deg, #f0f0f0, #ffffff);
}

/* Custom button styling */
.submit-btn {
    background: linear-gradient(45deg, #007acc, #0099ff);
    border-radius: 25px;
}
```

## Advanced Configuration Example

```yaml
site_name: My Educational Site
theme:
  name: material
  palette:
    - scheme: default
      primary: indigo
      accent: indigo
    - scheme: slate
      primary: blue
      accent: blue

plugins:
  - freetext:
      question_class: "edu-question"
      assessment_class: "edu-assessment"
      shuffle_questions: true
      show_character_count: false

extra_css:
  - stylesheets/custom-questions.css
```
