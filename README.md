# GoSubtitle

GoSubtitle is a PyQt6 desktop application for converting **Wrapper: Offline** Movie XML files (containing TTS entries) into standard SRT subtitle files. It supports both an interactive GUI for editing and a powerful command-line interface for batch processing and automation.

## Key Features

- **Wrapper: Offline XML to SRT**: Converts Movie XML files with `<sound tts="1">` entries to SRT, preserving speaker names and timing.
- **Speaker Management**: Edit, mass-replace, and manage speaker names; handles overlapping dialogue.
- **Frame-Based Timing**: All timing is based on 24 FPS frame numbers from the XML, with accurate conversion to SRT timestamps.
- **Smart Subtitle Splitting**: Automatically splits long subtitles by sentence and word count for readability.
- **Dual Interface**: Use the GUI for interactive editing or the CLI for automation—mode is auto-detected.
- **Robust Logging & Validation**: Comprehensive error handling and detailed logs for troubleshooting.

## Requirements

- Python 3.8+
- PyQt6

## Installation

```bash
pip install PyQt6
```

## Usage

### GUI Mode

```bash
python main.py
```

- Open a Wrapper: Offline XML file.
- Edit speakers and subtitles.
- Adjust timing offsets (in frames at 24 FPS).
- Mass-replace speaker names.
- Export to SRT.

### Console Mode

```bash
python main.py -f movie.xml
```

- Use `-g` to force GUI mode.
- Use `-o` for frame offsets, `-r` for speaker replacements, `--max-words` for line splitting, and `--verbose` for stats.

### Example

```bash
python main.py -f movie.xml -s output.srt -o 24 -r "Old:New" --max-words 12 --verbose
```

## Command-Line Options

```
-g, --gui              Force GUI mode
-f, --file PATH        Input Wrapper: Offline XML file (required)
-s, --srt PATH         Output SRT file (default: input with .srt)
-o, --offset FRAMES    Offset subtitles by frames (can be negative)
-w, --max-words COUNT  Max words per subtitle line (default: 10)
-r, --replace OLD:NEW  Replace speaker names (multiple allowed)
-v, --verbose          Show detailed statistics
--version              Show version and exit
```

## Project Structure

```
GoSubtitle/
├── main.py
├── helpers.py
├── modules/
│   ├── __init__.py
│   ├── window.py
│   ├── console.py
│   └── subtitle_processor.py
└── ui/
  ├── main_window.ui
  └── timeline_object.ui
```

## XML Format (Wrapper: Offline)

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

## Configuration

- `FPS = 24` (fixed)
- `DEFAULT_MAX_WORDS_PER_LINE = 10`
- `DEFAULT_WORDS_PER_SECOND = 2.5`
- `MIN_SUBTITLE_DURATION = 0.5`

## Troubleshooting

- **UI not loading**: Ensure the `ui/` directory is accessible.
- **XML errors**: Validate your Wrapper: Offline XML structure.
- **Timing issues**: All offsets and durations are in frames at 24 FPS.
- **Speaker replacements**: Use exact, case-sensitive names.

## License

Personal project—use and modify as needed.

## Contributing

Suggestions and improvements are welcome!
