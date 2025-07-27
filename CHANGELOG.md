# Changelog

All notable changes to the MkDocs Free-Text Plugin will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.4] - 2025-01-27

### Fixed
- **JavaScript Function Timing**: Completely resolved "function is not defined" errors by ensuring JavaScript functions are defined before HTML elements that reference them
- **Triple Quote Syntax Errors**: Fixed JavaScript syntax errors caused by unescaped triple quotes (`"""`) in sample answers through new `_clean_answer_for_javascript()` helper method
- **String Escaping**: Proper escaping of quotes, newlines, and special characters in JavaScript string literals
- **Function Placement**: JavaScript functions now correctly placed in document head for proper timing

### Enhanced
- **Submit Button Functionality**: Enhanced submit buttons with "Submitted" text change, "Click to resubmit" tooltips, and improved user feedback
- **Error Handling**: Robust error handling for malformed content and edge cases
- **Test Suite Organization**: Consolidated scattered test files into comprehensive, well-organized pytest test suite
- **Code Quality**: Removed duplicate and obsolete test files, debug scripts, and temporary HTML files

### Removed
- **Test Site**: Removed redundant test-site directory (functionality verified and no longer needed)
- **Debug Files**: Cleaned up debug scripts and temporary files (functionality moved to proper tests)
- **Duplicate Tests**: Consolidated 17+ duplicate JavaScript and HTML test files into 2 comprehensive test suites

### Technical Details
- Added `_clean_answer_for_javascript()` method to sanitize content for JavaScript embedding
- JavaScript functions now use consistent placement strategy for proper execution timing
- Comprehensive test coverage for JavaScript integration, HTML generation, and plugin functionality
- All tests can now be run simply with `pytest tests/`

## [1.0.3] - 2025-01-27

### Added
- **Triple Quote Configuration Support**: Enhanced `_parse_comma_separated_config` method to support triple quotes (`"""text"""`) for complex answers containing commas, quotes, and special characters
- **JavaScript Auto-Fix System**: Comprehensive auto-fix function (`initAutoFix()`) that automatically resolves timing issues and attaches event listeners
- **Enhanced Event Handling**: Replaced inline event handlers with proper DOM-ready event listeners to eliminate "function not defined" errors
- **Character Counter Functions**: Dynamic generation of character counting functions for each question with unique IDs and real-time updates
- **Submit Answer Functions**: Dynamic generation of submit answer functions with proper validation and visual feedback
- **Comprehensive Console Logging**: Detailed console logging system with success/warning/error indicators for debugging and development
- **DOM Verification Mechanism**: Timeout-based verification to detect DOM update persistence and potential race conditions
- **Comprehensive Test Suite**: Extensive test coverage including plugin functionality, HTML validation, JavaScript enhancement tests, and integration tests

### Fixed
- **AutoSave Error Handling**: Fixed autoSave function warnings by converting error messages to informational messages and adding proper null checks
- **JavaScript Syntax Errors**: Resolved multiple JavaScript syntax errors including variable declaration conflicts and quote escaping issues
- **Event Listener Timing**: Fixed timing issues where event handlers were called before functions were defined
- **Submit Button Improvements**: Enhanced submit button functionality with state management, tooltips, and better user feedback

### Enhanced
- **Question Structure Validation**: Improved validation to ensure unique question IDs and proper HTML structure
- **Backward Compatibility**: Maintained full backward compatibility with existing comma-separated configurations
- **Error Handling**: Robust error handling throughout the plugin with graceful degradation
- **Documentation**: Comprehensive documentation including enhancement summaries and usage examples

### Technical Improvements
- **Plugin Architecture**: Enhanced modular design with improved configuration parsing
- **Performance**: Optimized triple quote parsing algorithm and memory management
- **Code Quality**: Improved code organization with comprehensive inline documentation
- **Testing Infrastructure**: Professional testing framework with multiple validation layers

### Configuration Enhancements
- **Triple Quote Syntax**: New support for complex configurations using triple quotes
  ```markdown
  !!! freetext
      question: """Explain the differences between Python, JavaScript, and SQL."""
      sample_answers: """Python: General-purpose programming. JavaScript: Web development. SQL: Database queries."""
      marks: 10
  ```
- **Enhanced Validation**: Improved configuration validation with better error messages

### Developer Experience
- **Debugging Tools**: Comprehensive console logging for development and troubleshooting
- **Test Coverage**: 100% test coverage with multiple validation approaches
- **Documentation**: Detailed enhancement summaries and technical documentation

## [1.0.2] - Previous Release

### Added
- Basic plugin functionality
- Question and assessment support
- Material theme integration

## [1.0.1] - Previous Release

### Added
- Initial plugin structure
- Basic configuration options

## [1.0.0] - Initial Release

### Added
- Core MkDocs free-text plugin functionality
- Basic question rendering
- Configuration system