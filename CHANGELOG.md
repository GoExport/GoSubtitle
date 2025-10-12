# Changelog

All notable changes to GoSubtitle are documented in this file.

## [2.0.0] - Code Review Refactor

### Major Architectural Changes

#### Added

- **New `SubtitleProcessor` class**: Extracted all business logic from GUI into dedicated class
  - XML parsing with comprehensive error handling
  - Subtitle merging algorithm for overlapping dialogue
  - Smart subtitle splitting based on word count and sentences
  - Time formatting utilities
  - Offset application logic
- **Comprehensive Logging System**:
  - Structured logging throughout application
  - Different log levels (INFO, WARNING, ERROR, DEBUG)
  - Better debugging and monitoring capabilities
- **Type Hints**: Full type annotations for all methods
  - Better IDE support
  - Improved code maintainability
  - Catches type errors early
- **Docstrings**: Complete documentation for all classes and methods

  - Explains parameters and return values
  - Describes purpose and behavior
  - Better code discoverability

- **Helper Functions** in `helpers.py`:

  - File validation utilities
  - Path handling functions
  - Duration formatting
  - Project directory helpers

- **Module Exports**: Clean imports through `modules/__init__.py`

#### Fixed

- **Critical Lambda Closure Bug**:
  - **Issue**: Speaker change callbacks captured wrong index
  - **Impact**: Editing speakers could modify wrong subtitle
  - **Solution**: Proper closure creation with factory functions
- **Tab Order Navigation**:
  - **Issue**: Tab key navigation was unintuitive
  - **Solution**: Proper `setTabOrder` calls for speaker → content → next speaker flow
- **Path Handling**:
  - **Issue**: Hardcoded relative paths failed when running from different directories
  - **Solution**: Using `pathlib` with `__file__` resolution for cross-platform compatibility
- **Magic Numbers**:
  - **Issue**: Hardcoded values scattered throughout code
  - **Solution**: Defined constants at class level (FPS, MAX_WORDS_PER_LINE, etc.)

#### Changed

- **Subtitle Content Now Editable**:

  - Changed `timeline_object.ui` readOnly property to false
  - Added `change_content` method to handle text changes
  - Connected textChanged signal with proper closure

- **Better Error Messages**:

  - More specific error messages for different failure cases
  - Separate handling for FileNotFoundError vs ParseError
  - User-friendly warnings for edge cases

- **Improved Code Organization**:

  - Separated GUI logic from business logic
  - Better method organization and grouping
  - Clearer responsibility separation

- **Enhanced Validation**:
  - Check for XML structure validity
  - Validate required elements exist
  - Skip empty subtitles automatically
  - Handle missing or malformed data gracefully

#### Removed

- Direct XML manipulation from `MainWindow`
- Inline subtitle processing logic
- Hardcoded FPS calculations
- `hasattr` checks (replaced with proper initialization)

### Performance

- No significant performance changes
- Slightly better memory management with widget cleanup
- More efficient timeline object creation

### Documentation

- Added comprehensive README.md
- Created CHANGELOG.md
- Inline code documentation with docstrings
- Better code comments for complex logic

### Testing

- No automated tests added yet
- Code is now more testable due to separation of concerns
- SubtitleProcessor can be unit tested independently

### Migration Notes

- Import changed from `from modules.window import MainWindow` to `from modules import MainWindow`
- If extending the code, use `SubtitleProcessor` for subtitle operations
- All paths now automatically resolve relative to script location

---

## [1.0.0] - Initial Release

### Features

- Basic XML to SRT conversion
- Speaker name editing
- Mass speaker replacement
- Frame-based offset adjustment
- Timeline view of subtitles
- Subtitle merging for overlapping dialogue
- Automatic subtitle splitting based on word count

### Known Issues (Fixed in 2.0.0)

- Lambda closure bug in speaker callbacks
- Poor tab navigation
- Hardcoded paths
- Mixed GUI and business logic
- Limited error handling
- No logging system
