# Debugging & Troubleshooting

This guide helps you debug issues and understand what's happening when the MkDocs Free-Text Plugin processes your content.

## 🔍 Debug Mode (v1.2.0+)

The plugin includes a comprehensive logging system to help you troubleshoot issues and understand the content processing flow.

### Enable Debug Mode

Add debug configuration to your `mkdocs.yml`:

```yaml
plugins:
  - freetext:
      debug: true
      debug_output_dir: "./debug"  # Optional: custom debug file location
```

### Debug Features

#### Professional Logging System
- **Clean Output**: Quiet operation by default, detailed logging when enabled
- **Categorized Messages**: DEBUG, INFO, WARNING, and ERROR levels
- **Structured Format**: Timestamps, logger names, and clear message hierarchy
- **No Print Statements**: Professional logging replaces all random print output

#### Log Levels Explained

**DEBUG Level** - Verbose development information:
```
DEBUG - Processing page: demo.md
DEBUG - Found 3 freetext admonition(s) on page demo.md
DEBUG - Generated JavaScript for question abc123
DEBUG - Parsing content: What is the capital...
```

**INFO Level** - Important process information:
```
INFO - FreetextPlugin initialized successfully
INFO - Processed freetext questions on page demo.md
```

**WARNING Level** - Configuration issues and fallbacks:
```
WARNING - Invalid configuration format. Expected comma-separated format: 'marks: 10, type: long, rows: 5'. Found line-based format. Using default values.
WARNING - Invalid configuration value 'invalid' for 'type'. Expected string (short/long). Using default value.
```

**ERROR Level** - Serious problems:
```
ERROR - Plugin configuration contains errors. Please fix them before proceeding.
ERROR - Could not write debug files to ./debug: Permission denied
```

### Debug File Output

When `debug_output_dir` is configured, the plugin generates HTML comparison files:

```
./debug/
├── demo_before.html    # Original HTML before processing
├── demo_after.html     # Processed HTML with questions
├── index_before.html
└── index_after.html
```

These files help you:
- See exactly what content was processed
- Compare input vs output HTML
- Debug question parsing issues
- Understand the transformation process

## 🛠️ Common Issues & Solutions

### Configuration Problems

#### Issue: Questions not appearing
**Symptoms**: Admonitions render as normal admonitions instead of interactive questions

**Solutions:**
1. Check admonition syntax:
   ```markdown
   !!! freetext
       Your question here
       ---
       marks: 5
   ```

2. Verify plugin is loaded in `mkdocs.yml`:
   ```yaml
   plugins:
     - freetext
   ```

3. Enable debug mode to see processing details:
   ```yaml
   plugins:
     - freetext:
         debug: true
   ```

#### Issue: Configuration not working
**Symptoms**: Default values used instead of your configuration

**Solutions:**
1. Use comma-separated format:
   ```markdown
   !!! freetext
       Question text
       ---
       marks: 10, type: long, rows: 6
   ```

2. Check for typos in configuration keys:
   ```markdown
   # ✅ Correct
   marks: 5, type: short, show_answer: true
   
   # ❌ Incorrect
   mark: 5, typ: short, show_answers: true
   ```

3. Enable debug mode to see configuration parsing:
   ```yaml
   plugins:
     - freetext:
         debug: true
   ```

### Content Processing Issues

#### Issue: Rich content not rendering
**Symptoms**: Markdown, code blocks, or diagrams appear as plain text

**Solutions:**
1. Ensure content comes before the `---` separator:
   ```markdown
   !!! freetext
       Your question with **markdown** and:
       
       ```python
       def hello():
           print("world")
       ```
       ---
       marks: 5
   ```

2. Check for syntax conflicts in your content
3. Use debug files to see the HTML transformation

#### Issue: JavaScript errors in browser
**Symptoms**: Questions appear but don't respond to interactions

**Solutions:**
1. Check browser console for JavaScript errors
2. Verify CSS classes aren't being overridden
3. Enable debug mode to see JavaScript generation:
   ```
   DEBUG - Generated JavaScript for question abc123
   ```

### Assessment Problems

#### Issue: Questions not shuffling
**Symptoms**: Questions always appear in the same order

**Solutions:**
1. Enable shuffling in assessment configuration:
   ```markdown
   !!! freetext-assessment
       title: My Assessment, shuffle: true
       
       Question 1
       ---
       marks: 5
       
       <hr>
       
       Question 2
       ---
       marks: 10
   ```

2. Or enable globally:
   ```yaml
   plugins:
     - freetext:
         shuffle_questions: true
   ```

## 📝 Getting Help

### Enable Debug Mode First
Before reporting issues, enable debug mode to gather detailed information:

```yaml
plugins:
  - freetext:
      debug: true
      debug_output_dir: "./debug"
```

### Information to Include
When asking for help, please include:

1. **Your `mkdocs.yml` configuration**
2. **The problematic markdown content**
3. **Debug log output** (with debug mode enabled)
4. **Expected vs actual behavior**
5. **Browser console errors** (if applicable)
6. **Debug files** from `debug_output_dir` (if relevant)

### Log Level Configuration

You can also control logging programmatically:

```python
import logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```

This gives you complete control over log formatting and output destination.

## 🔧 Advanced Debugging

### Custom Log Handlers

For advanced debugging, you can add custom log handlers:

```python
import logging
from mkdocs_freetext.plugin import logger

# Add file handler
file_handler = logging.FileHandler('plugin.log')
file_handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)
```

### Performance Monitoring

Enable debug mode to see processing times and identify performance bottlenecks:

```
DEBUG - Processing page: large_assessment.md
DEBUG - Found 25 freetext admonition(s) on page large_assessment.md
INFO - Processed freetext questions on page large_assessment.md
```

The new logging system provides much better visibility into plugin operation compared to the old print-based debugging approach.
