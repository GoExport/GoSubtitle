"""
Console module for GoSubtitle application.

This module provides a command-line interface for processing subtitles
without the GUI, supporting batch operations and automated workflows.
"""

import logging
from typing import List, Dict, Optional
from pathlib import Path

from .subtitle_processor import SubtitleProcessor
from .parameters import Parameters

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class Console:
    """
    Console interface for GoSubtitle.
    
    Handles command-line operations for loading Movie XML files, applying
    transformations, and exporting to SRT format.
    """
    
    def __init__(self):
        """Initialize the console interface."""
        self.processor = SubtitleProcessor()
        self.subtitles: List[Dict[str, any]] = []
        
    def run(self, params: Parameters) -> None:
        """
        Main entry point for console mode.
        
        Args:
            params: Parsed command-line parameters
        """
        # Get input file path
        input_file = params.get_param_value('file')
        if not input_file:
            logger.error("No input file specified. Use -f or --file to specify an XML file.")
            print("Error: No input file specified.")
            print("Usage: GoSubtitle.exe -f <input.xml> -s <output.srt> [options]")
            return
        
        # Validate input file exists
        input_path = Path(input_file)
        if not input_path.exists():
            logger.error(f"Input file not found: {input_file}")
            print(f"Error: Input file not found: {input_file}")
            return
        
        if input_path.suffix.lower() != '.xml':
            logger.error(f"Input file must be an XML file: {input_file}")
            print(f"Error: Input file must be an XML file (got {input_path.suffix})")
            return
        
        # Get output file path (default to same name as input with .srt extension)
        output_file = params.get_param_value('srt')
        if not output_file:
            output_file = input_path.with_suffix('.srt')
            logger.info(f"No output file specified, using: {output_file}")
        
        output_path = Path(output_file)
        
        # Parse XML file
        print(f"Loading subtitles from: {input_file}")
        try:
            self.subtitles = self.processor.parse_xml(str(input_path))
            
            if not self.subtitles:
                logger.warning("No subtitles found in XML file")
                print("Warning: No subtitles found in the XML file.")
                return
            
            print(f"Successfully loaded {len(self.subtitles)} subtitle(s)")
            
        except Exception as e:
            logger.error(f"Failed to parse XML file: {e}", exc_info=True)
            print(f"Error: Failed to parse XML file: {e}")
            return
        
        # Apply offset if specified
        offset = params.get_param_value('offset')
        if offset is not None and offset != 0:
            print(f"Applying offset of {offset} frames...")
            SubtitleProcessor.apply_offset(self.subtitles, offset)
            logger.info(f"Applied offset of {offset} frames")
        
        # Apply speaker replacements if specified
        replace_map = params.get_param_value('replace_speakers')
        if replace_map:
            print("Applying speaker replacements...")
            self.apply_speaker_replacements(replace_map)
        
        # Apply max words per line if specified
        max_words = params.get_param_value('max_words')
        if max_words and max_words != self.processor.max_words_per_line:
            print(f"Re-processing with max {max_words} words per line...")
            self.processor.max_words_per_line = max_words
            # Re-parse to apply new word limit
            self.subtitles = self.processor.parse_xml(str(input_path))
            if offset is not None and offset != 0:
                SubtitleProcessor.apply_offset(self.subtitles, offset)
            if replace_map:
                self.apply_speaker_replacements(replace_map)
        
        # Display subtitle statistics
        if params.get_param_value('verbose'):
            self.display_statistics()
        
        # Save to SRT file
        print(f"Saving subtitles to: {output_path}")
        try:
            self.save_srt(str(output_path))
            print(f"Successfully saved {len(self.subtitles)} subtitle(s) to {output_path}")
            logger.info(f"Successfully saved subtitles to {output_path}")
            
        except Exception as e:
            logger.error(f"Failed to save SRT file: {e}", exc_info=True)
            print(f"Error: Failed to save SRT file: {e}")
            return
    
    def apply_speaker_replacements(self, replace_map: Dict[str, str]) -> None:
        """
        Replace speaker names according to the provided mapping.
        
        Args:
            replace_map: Dictionary mapping old speaker names to new names
        """
        replacement_count = {}
        
        for subtitle in self.subtitles:
            old_speaker = subtitle['speaker']
            if old_speaker in replace_map:
                new_speaker = replace_map[old_speaker]
                subtitle['speaker'] = new_speaker
                replacement_count[old_speaker] = replacement_count.get(old_speaker, 0) + 1
        
        # Log replacements
        for old_name, count in replacement_count.items():
            new_name = replace_map[old_name]
            print(f"  Replaced '{old_name}' with '{new_name}' ({count} occurrence(s))")
            logger.info(f"Replaced speaker '{old_name}' with '{new_name}' ({count} occurrences)")
    
    def display_statistics(self) -> None:
        """Display statistics about the loaded subtitles."""
        if not self.subtitles:
            return
        
        # Count speakers
        speaker_counts = {}
        total_duration = 0.0
        
        for subtitle in self.subtitles:
            speaker = subtitle['speaker']
            speaker_counts[speaker] = speaker_counts.get(speaker, 0) + 1
            total_duration += (subtitle['stop'] - subtitle['start'])
        
        # Convert total duration to time format
        duration_str = SubtitleProcessor.format_time(total_duration)
        
        print("\n=== Subtitle Statistics ===")
        print(f"Total subtitles: {len(self.subtitles)}")
        print(f"Total duration: {duration_str}")
        print(f"Unique speakers: {len(speaker_counts)}")
        print("\nSpeaker breakdown:")
        for speaker, count in sorted(speaker_counts.items()):
            print(f"  {speaker}: {count} subtitle(s)")
        print("===========================\n")
    
    def save_srt(self, output_path: str) -> None:
        """
        Save subtitles to an SRT file.
        
        Args:
            output_path: Path where the SRT file will be saved
            
        Raises:
            IOError: If the file cannot be written
        """
        with open(output_path, 'w', encoding='utf-8') as f:
            for idx, subtitle in enumerate(self.subtitles, start=1):
                start_time = SubtitleProcessor.format_time(subtitle['start'])
                end_time = SubtitleProcessor.format_time(subtitle['stop'])
                
                f.write(f"{idx}\n")
                f.write(f"{start_time} --> {end_time}\n")
                f.write(f"{subtitle['speaker']}: {subtitle['text']}\n\n")
        pass