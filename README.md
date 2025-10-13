# GoSubtitle

A PyQt6-based desktop application for converting Movie XML files to SRT subtitle format with speaker identification and timing controls. Also includes a powerful command-line interface for batch processing and automation.

## Features

- **XML to SRT Conversion**: Convert Movie XML files containing TTS data to standard SRT subtitle format
- **Speaker Management**:
  - View and edit speaker names for each subtitle
  - Mass replace speaker names across all subtitles
  - Automatic handling of overlapping speaker dialogue
- **Timing Controls**:
  - Adjust subtitle timing with frame-based offset
  - Smart subtitle splitting based on word count and sentence boundaries
  - Automatic time distribution based on speaking rate
- **Dual Interface**:
  - GUI mode with intuitive visual interface
  - Console mode for batch processing and automation
  - Automatic mode detection (console when available, GUI otherwise)
- **Robust Error Handling**: Comprehensive logging and validation

## Requirements

- Python 3.8+
- PyQt6

## Installation

1. Clone or download this repository
2. Install dependencies:

```bash
pip install PyQt6
```

## Usage

### GUI Mode

1. Run the application:

```bash
python main.py
```

2. Click "Select" to open a Movie XML file
3. Edit speakers and subtitle text as needed
4. Use the offset spinbox to adjust timing (in frames at 24 fps)
5. Mass replace speaker names if needed
6. Click "Save" to export as an SRT file

### Console Mode

The console mode activates automatically when running from a terminal/command prompt. Force GUI mode with the `-g` flag.

**Basic usage:**

```bash
python main.py -f movie.xml
```

**Specify output file:**

```bash
python main.py -f movie.xml -s subtitles.srt
```

**Apply time offset (in frames):**

```bash
python main.py -f movie.xml -o 24
```

**Replace speaker names:**

```bash
python main.py -f movie.xml -r "John:Jane" -r "Bob:Robert"
```

**Set maximum words per line:**

```bash
python main.py -f movie.xml --max-words 15
```

**Display detailed statistics:**

```bash
python main.py -f movie.xml --verbose
```

**Combined example:**

```bash
python main.py -f movie.xml -s output.srt -o -12 -r "Unknown:Narrator" --max-words 12 --verbose
```

### Command-Line Options

```
-g, --gui              Force GUI mode even when console is available
-f, --file PATH        Input Movie XML file path (required)
-s, --srt PATH         Output SRT file path (default: input filename with .srt)
-o, --offset FRAMES    Offset all subtitles by frames (can be negative)
-w, --max-words COUNT  Maximum words per subtitle line (default: 10)
-r, --replace OLD:NEW  Replace speaker names (can be used multiple times)
-v, --verbose          Display detailed statistics about subtitles
--version              Show program version and exit
```

## Project Structure

```
GoSubtitle/
├── main.py                      # Application entry point
├── helpers.py                   # Utility functions
├── modules/
│   ├── __init__.py             # Module exports
│   ├── window.py               # Main window GUI logic
│   └── subtitle_processor.py  # Subtitle processing business logic
└── ui/
    ├── main_window.ui          # Main window UI design
    └── timeline_object.ui      # Subtitle timeline widget UI
```

## Architecture

The application follows a clean architecture pattern:

- **Presentation Layer** (`window.py`): Handles all GUI interactions and user events
- **Business Logic Layer** (`subtitle_processor.py`): Manages subtitle parsing, merging, and splitting
- **Utility Layer** (`helpers.py`): Provides common utility functions

### Key Features of the Code

- **Type Hints**: Full type annotations for better IDE support and code clarity
- **Comprehensive Logging**: Detailed logging for debugging and monitoring
- **Docstrings**: Every class and method is documented
- **Error Handling**: Robust exception handling with user-friendly error messages
- **Path Handling**: Platform-independent path handling using `pathlib`
- **Proper Closures**: Fixed lambda closure bugs for correct event handling
- **Tab Order Management**: Intuitive keyboard navigation through timeline objects

## Configuration

Constants in `SubtitleProcessor`:

- `FPS = 24`: Fixed to 24 frames per second
- `DEFAULT_MAX_WORDS_PER_LINE = 10`: Maximum words per subtitle line
- `DEFAULT_WORDS_PER_SECOND = 2.5`: Average speaking rate for timing
- `MIN_SUBTITLE_DURATION = 0.5`: Minimum subtitle duration in seconds

## XML Format

Expected Movie XML format:

```xml
<root duration="[total_frames]">
    <sound tts="1">
        <start>[start_frame]</start>
        <stop>[stop_frame]</stop>
        <ttsdata>
            <text>[subtitle_text]</text>
            <voice>[speaker_name]</voice>
        </ttsdata>
    </sound>
    ...
</root>
```

## Development

### Recent Improvements (Code Review Implementation)

✅ **Separation of Concerns**: Extracted business logic into `SubtitleProcessor` class  
✅ **Type Hints**: Added throughout codebase for better type safety  
✅ **Docstrings**: Comprehensive documentation for all classes and methods  
✅ **Logging System**: Proper logging instead of silent exception catching  
✅ **Input Validation**: Robust validation for XML structure and edge cases  
✅ **Path Handling**: Using `pathlib` for cross-platform compatibility  
✅ **Fixed Lambda Bug**: Proper closure handling in event callbacks  
✅ **Tab Order**: Intuitive keyboard navigation through timeline objects  
✅ **Editable Content**: Subtitle text is now editable in the UI  
✅ **Constants**: Properly defined configuration constants  
✅ **Helper Functions**: Useful utilities in `helpers.py`  
✅ **Clean Imports**: Module-level exports in `__init__.py`

### Testing

Currently no automated tests. Recommended additions:

- Unit tests for `SubtitleProcessor` methods
- Integration tests for XML parsing
- UI tests for user interactions

## License

This is a personal project. Feel free to use and modify as needed.

## Contributing

This is a learning project, but suggestions and improvements are welcome!

## Troubleshooting

**UI files not found**: Make sure you run the application from the project root directory, or the path resolution will work from any directory thanks to `pathlib`.

**XML parsing errors**: Ensure your XML file follows the expected format with proper `duration`, `start`, `stop`, `text`, and `voice` elements.

**Import errors**: Make sure PyQt6 is installed: `pip install PyQt6`

## Future Enhancements

Potential improvements:

- Undo/redo functionality
- Subtitle preview with video sync
- Configurable FPS support
- Import/export multiple formats
- Search and filter subtitles
- Keyboard shortcuts
- Auto-save feature
- Dark mode theme
