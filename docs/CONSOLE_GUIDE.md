# GoSubtitle Console Mode - Quick Start Guide

## Overview

The console mode provides a command-line interface for processing Movie XML files and converting them to SRT format. It's perfect for batch processing and automation.

## Basic Commands

### 1. Simple Conversion

Convert an XML file to SRT (output will have the same name as input):

```bash
python main.py -f movie.xml
```

### 2. Specify Output File

Choose a specific output filename:

```bash
python main.py -f movie.xml -s subtitles.srt
```

### 3. Apply Time Offset

Shift all subtitles by a number of frames (24 fps):

```bash
# Add 24 frames (1 second delay)
python main.py -f movie.xml -o 24

# Subtract 12 frames (0.5 second earlier)
python main.py -f movie.xml -o -12
```

### 4. Replace Speaker Names

Replace one or more speaker names:

```bash
# Single replacement
python main.py -f movie.xml -r "narrator:Narrator"

# Multiple replacements
python main.py -f movie.xml -r "narrator:Narrator" -r "assistant:Assistant"
```

### 5. Control Word Count

Set maximum words per subtitle line:

```bash
python main.py -f movie.xml --max-words 15
```

### 6. View Statistics

Display detailed information about the subtitles:

```bash
python main.py -f movie.xml --verbose
```

### 7. Combined Operations

Combine multiple options for complex processing:

```bash
python main.py -f movie.xml -s output.srt -o 24 -r "narrator:Narrator" -r "assistant:Assistant" --max-words 12 --verbose
```

## Example with Test File

Try the included test file:

```bash
# Basic conversion with statistics
python main.py -f test_movie.xml --verbose

# Convert with speaker name replacements
python main.py -f test_movie.xml -s demo.srt -r "Narrator:John" -r "Assistant:Sarah" --verbose
```

## Force GUI Mode

If you're running from a console but want to use the GUI:

```bash
python main.py -g
```

## Tips

1. **Batch Processing**: Use shell scripts or batch files to process multiple files
2. **Automation**: Integrate into build pipelines or workflows
3. **Testing**: Use the verbose flag to verify your settings before processing large batches
4. **Speaker Names**: Use quotes around speaker replacements if they contain spaces
5. **Negative Offsets**: Use negative numbers to shift subtitles earlier in time

## Output Format

The console mode produces standard SRT files with the following format:

```
1
00:00:00,000 --> 00:00:03,000
Narrator: Welcome to the demonstration.

2
00:00:03,000 --> 00:00:06,000
Narrator: This is a test subtitle.
```

## Error Handling

The console mode provides clear error messages:

- Missing input file: Displays usage instructions
- Invalid XML: Shows parsing error details
- File not found: Reports the missing file path
- Invalid parameters: Warns about incorrect format

## Getting Help

View all available options:

```bash
python main.py --help
```

Check version:

```bash
python main.py --version
```
