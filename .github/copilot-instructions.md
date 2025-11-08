# GoSubtitle AI Coding Agent Instructions

## Project Overview

GoSubtitle is a PyQt6 desktop application that converts Movie XML files (containing TTS data) to SRT subtitle format. It features dual interface modes: GUI for interactive editing and console mode for batch processing/automation.

## Architecture Pattern

The codebase follows a clean 3-layer architecture:

- **Presentation Layer**: `modules/window.py` (GUI), `modules/console.py` (CLI)
- **Business Logic**: `modules/subtitle_processor.py` (core XML parsing, subtitle processing)
- **Utilities**: `helpers.py`, `modules/parameters.py` (command-line parsing)

**Key principle**: All subtitle processing logic lives in `SubtitleProcessor` class. GUI and console are thin clients that delegate to this core engine.

## Entry Point & Mode Detection

`main.py` automatically detects execution context:

- Console available → console mode via `Console` class
- No console OR `-g/--gui` flag → GUI mode via `MainWindow`
- Uses `helpers.has_console()` with Windows-specific `ctypes.windll.kernel32.GetConsoleWindow()`

## Critical Development Patterns

### UI File Loading

UI files are loaded from `ui/` directory using `pathlib` for cross-platform compatibility:

```python
BASE_DIR = Path(__file__).resolve().parent.parent
UI_DIR = BASE_DIR / "ui"
uic.loadUi(str(UI_DIR / "main_window.ui"), self)
```

### Frame-Based Timing System

All timing calculations use **frames at 24 FPS** (hardcoded constant):

- XML contains frame numbers, not timestamps
- `SubtitleProcessor.format_time()` converts frames → SRT timestamp format
- Offset operations work in frame units

### Subtitle Processing Pipeline

1. **Parse XML**: Extract TTS sound elements with `tts='1'` attribute
2. **Merge Overlapping**: Combine subtitles with overlapping time ranges
3. **Smart Splitting**: Break long subtitles by sentence boundaries + word count limits
4. **Time Distribution**: Calculate timing based on `words_per_second` rate

### Command-Line Integration

`Parameters` class handles argparse with custom post-processing:

- Speaker replacements: `"old:new"` format → dictionary mapping
- Multiple `-r` flags supported for batch replacements
- Uses `getattr(self.args, param_name)` pattern for parameter access

## Development Workflows

### Building Executables

PyInstaller spec generates TWO executables:

```bash
pyinstaller GoSubtitle.spec
# Creates: dist/GoSubtitle.exe (GUI) and dist/GoSubtitle_CLI.exe (console)
```

Spec includes UI and assets folders as data files.

### Testing Subtitle Processing

Use console mode for quick validation:

```bash
python main.py -f test.xml --verbose  # Shows statistics
python main.py -f test.xml -o 24 -r "old:new" --max-words 15
```

### Logging Configuration

Each module configures its own logger:

```python
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
```

## Key Configuration Constants

In `SubtitleProcessor`:

- `FPS = 24`: Fixed frame rate (do not make configurable without XML format changes)
- `DEFAULT_MAX_WORDS_PER_LINE = 10`: Subtitle splitting threshold
- `DEFAULT_WORDS_PER_SECOND = 2.5`: Speaking rate for timing calculations
- `MIN_SUBTITLE_DURATION = 0.5`: Minimum subtitle duration in seconds

## Expected XML Format

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
</root>
```

## Module Import Pattern

Uses `__init__.py` with explicit `__all__` exports:

```python
from .window import MainWindow
from .console import Console
# Import from modules package, not direct file paths
```

## PyQt6 Specifics

- UI files created with Qt Designer, loaded via `uic.loadUi()`
- Icons and assets bundled in `assets/` directory
- Uses `pathlib` for all file operations (Windows + cross-platform)
- No custom widgets - uses standard PyQt6 components

## Common Debugging Points

1. **UI Not Loading**: Check that `ui/` directory is accessible from execution path
2. **XML Parse Errors**: Validate XML has required `duration` attribute and TTS sound elements
3. **Timing Issues**: Remember all operations are frame-based at 24 FPS
4. **Speaker Replacements**: Must use exact string matching (case-sensitive)

## Extension Guidelines

- New features → add to `SubtitleProcessor` first, then expose via GUI/console
- UI changes → modify `.ui` files with Qt Designer, not hand-coding
- CLI options → extend `Parameters` class argument definitions
- Keep frame-based timing system for XML compatibility
