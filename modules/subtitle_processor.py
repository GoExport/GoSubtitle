"""
Subtitle processing module for GoSubtitle.

This module handles all subtitle-related business logic including XML parsing,
subtitle merging, splitting, and time formatting.
"""

import xml.etree.ElementTree as ET
import logging
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)


class SubtitleProcessor:
    """
    Processes and manipulates subtitle data from Movie XML files.
    
    This class handles parsing XML files, merging overlapping subtitles,
    splitting long subtitles based on word count and sentence boundaries,
    and formatting time stamps.
    """
    
    # Configuration constants
    FPS = 24  # Frames per second (fixed to 24 fps)
    DEFAULT_MAX_WORDS_PER_LINE = 10  # Maximum words per subtitle line
    DEFAULT_WORDS_PER_SECOND = 2.5  # Average speaking rate
    MIN_SUBTITLE_DURATION = 0.5  # Minimum duration in seconds
    
    def __init__(
        self,
        max_words_per_line: int = DEFAULT_MAX_WORDS_PER_LINE,
        words_per_second: float = DEFAULT_WORDS_PER_SECOND
    ):
        """
        Initialize the SubtitleProcessor.
        
        Args:
            max_words_per_line: Maximum number of words allowed per subtitle line
            words_per_second: Average speaking rate for timing calculations
        """
        self.max_words_per_line = max_words_per_line
        self.words_per_second = words_per_second
        self.tree: Optional[ET.ElementTree] = None
        self.root: Optional[ET.Element] = None
        self.length: float = 0.0
    
    def parse_xml(self, file_path: str) -> List[Dict[str, any]]:
        """
        Parse a Movie XML file and extract subtitle information.
        
        Args:
            file_path: Path to the XML file to parse
            
        Returns:
            List of subtitle dictionaries with 'start', 'stop', 'text', and 'speaker' keys
            
        Raises:
            FileNotFoundError: If the file doesn't exist
            ET.ParseError: If the XML is malformed
            ValueError: If required XML elements are missing
        """
        logger.info(f"Parsing XML file: {file_path}")
        
        try:
            self.tree = ET.parse(file_path)
            self.root = self.tree.getroot()
            
            # Validate that duration attribute exists
            duration_str = self.root.get("duration")
            if duration_str is None:
                raise ValueError("XML root element missing 'duration' attribute")
            
            self.length = float(duration_str)
            logger.info(f"XML parsed successfully. Duration: {self.length} frames")
            
            # Convert XML data to dictionary format
            subtitles = self._convert_to_dict()
            
            logger.info(f"Extracted {len(subtitles)} subtitles")
            return subtitles
            
        except ET.ParseError as e:
            logger.error(f"XML parse error: {e}")
            raise
        except ValueError as e:
            logger.error(f"Invalid XML structure: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error parsing XML: {e}")
            raise
    
    def _convert_to_dict(self) -> List[Dict[str, any]]:
        """
        Convert XML elements to a list of subtitle dictionaries.
        
        Returns:
            List of subtitle dictionaries, sorted by start time, with overlapping
            subtitles merged and long subtitles split
        """
        subtitles = []
        
        # Find all sound elements with tts='1'
        sound_elements = self.root.findall(".//sound[@tts='1']")
        
        if not sound_elements:
            logger.warning("No TTS sound elements found in XML")
            return []
        
        for sound in sound_elements:
            try:
                start_elem = sound.find("start")
                stop_elem = sound.find("stop")
                text_elem = sound.find("ttsdata/text")
                voice_elem = sound.find("ttsdata/voice")
                
                # Validate all required elements exist
                if start_elem is None or stop_elem is None:
                    logger.warning("Skipping sound element: missing start or stop")
                    continue
                
                start = float(start_elem.text) if start_elem.text else 0.0
                stop = float(stop_elem.text) if stop_elem.text else 0.0
                text = text_elem.text if text_elem is not None and text_elem.text else ""
                speaker = voice_elem.text if voice_elem is not None and voice_elem.text else "Unknown"
                
                # Skip empty subtitles
                if not text.strip():
                    logger.debug(f"Skipping empty subtitle at {start}")
                    continue
                
                subtitles.append({
                    'start': start,
                    'stop': stop,
                    'text': text.strip(),
                    'speaker': speaker.capitalize()
                })
                
            except (ValueError, AttributeError) as e:
                logger.warning(f"Error processing sound element: {e}")
                continue
        
        # Sort subtitles by start time
        subtitles.sort(key=lambda x: x['start'])
        
        # Merge overlapping subtitles
        merged_subtitles = self._merge_overlapping(subtitles)
        
        # Split long subtitles into multiple entries
        split_subtitles = []
        for subtitle in merged_subtitles:
            split_entries = self._split_subtitle_entry(subtitle)
            split_subtitles.extend(split_entries)
        
        return split_subtitles
    
    def _merge_overlapping(self, subtitles: List[Dict[str, any]]) -> List[Dict[str, any]]:
        """
        Merge overlapping subtitles.
        
        When two subtitles overlap in time, they are combined with their speakers
        and text merged appropriately.
        
        Args:
            subtitles: List of subtitle dictionaries sorted by start time
            
        Returns:
            List of merged subtitle dictionaries
        """
        if not subtitles:
            return []
        
        merged_subtitles = []
        
        for subtitle in subtitles:
            # Check if this subtitle overlaps with the last merged one
            if merged_subtitles and subtitle['start'] < merged_subtitles[-1]['stop']:
                # Overlapping - merge them
                last = merged_subtitles[-1]
                
                # Combine speakers if different
                if subtitle['speaker'] != last['speaker']:
                    combined_speaker = f"{last['speaker']}/{subtitle['speaker']}"
                else:
                    combined_speaker = last['speaker']
                
                # Combine text
                combined_text = f"{last['text']}\n{subtitle['text']}"
                
                # Update the last subtitle with merged data
                last['speaker'] = combined_speaker
                last['text'] = combined_text
                last['stop'] = max(last['stop'], subtitle['stop'])
                
                logger.debug(f"Merged overlapping subtitles at {subtitle['start']}")
            else:
                # No overlap - add as new subtitle
                merged_subtitles.append(subtitle.copy())
        
        return merged_subtitles
    
    def _split_subtitle_entry(self, subtitle: Dict[str, any]) -> List[Dict[str, any]]:
        """
        Split a subtitle entry into multiple entries based on sentence boundaries and word count.
        
        Long subtitles are split to improve readability, with timing calculated based
        on word count and speaking rate.
        
        Args:
            subtitle: A subtitle dictionary with 'start', 'stop', 'text', and 'speaker'
            
        Returns:
            List of subtitle dictionaries (one or more)
        """
        text = subtitle['text']
        if not text:
            return [subtitle]
        
        # Sentence ending punctuation
        sentence_endings = ['. ', '! ', '? ', ': ']
        
        segments = []
        
        # Split by existing newlines first (preserve intentional breaks)
        paragraphs = text.split('\n')
        
        for paragraph in paragraphs:
            words = paragraph.split()
            current_segment = ""
            
            i = 0
            while i < len(words):
                word = words[i]
                
                # Check if adding this word would exceed the word limit
                current_word_count = len(current_segment.split()) if current_segment else 0
                
                if current_segment:
                    test_segment = current_segment + " " + word
                else:
                    test_segment = word
                
                # Check if current segment ends with sentence ending punctuation
                ends_with_sentence = any(
                    current_segment.rstrip().endswith(ending.strip()) 
                    for ending in sentence_endings
                )
                
                # Decide whether to start a new segment
                if current_segment and (ends_with_sentence or current_word_count >= self.max_words_per_line):
                    segments.append(current_segment.strip())
                    current_segment = word
                else:
                    current_segment = test_segment
                
                i += 1
            
            # Add remaining text
            if current_segment:
                segments.append(current_segment.strip())
        
        # If only one segment, return the original subtitle
        if len(segments) <= 1:
            return [subtitle]
        
        # Create multiple subtitle entries with timing based on estimated speech duration
        result = []
        total_duration = subtitle['stop'] - subtitle['start']
        
        # Calculate estimated duration for each segment based on word count
        segment_word_counts = [len(seg.split()) for seg in segments]
        total_words = sum(segment_word_counts)
        
        # Calculate ideal duration for each segment based on speaking rate
        segment_durations = [
            word_count / self.words_per_second 
            for word_count in segment_word_counts
        ]
        total_ideal_duration = sum(segment_durations)
        
        # If our ideal total exceeds available time, scale proportionally
        # If we have extra time, distribute it proportionally as well
        if total_ideal_duration > 0:
            scale_factor = total_duration / total_ideal_duration
            segment_durations = [duration * scale_factor for duration in segment_durations]
        else:
            # Fallback to equal distribution if calculation fails
            segment_durations = [total_duration / len(segments)] * len(segments)
        
        # Ensure minimum duration per subtitle
        min_duration_frames = self.MIN_SUBTITLE_DURATION * self.FPS
        for i in range(len(segment_durations)):
            if segment_durations[i] < min_duration_frames:
                segment_durations[i] = min_duration_frames
        
        # Adjust if total exceeds available time after applying minimums
        adjusted_total = sum(segment_durations)
        if adjusted_total > total_duration:
            scale_factor = total_duration / adjusted_total
            segment_durations = [duration * scale_factor for duration in segment_durations]
        
        # Create subtitle entries with calculated timing
        current_start = subtitle['start']
        for i, segment in enumerate(segments):
            duration = segment_durations[i]
            new_subtitle = {
                'start': current_start,
                'stop': current_start + duration,
                'text': segment,
                'speaker': subtitle['speaker']
            }
            result.append(new_subtitle)
            current_start += duration
        
        # Adjust the last subtitle to end exactly at the original stop time
        if result:
            result[-1]['stop'] = subtitle['stop']
        
        logger.debug(f"Split subtitle into {len(result)} segments")
        return result
    
    @staticmethod
    def format_time(frames: float, fps: int = FPS) -> str:
        """
        Convert frame number to SRT timestamp format.
        
        Args:
            frames: Number of frames from the start
            fps: Frames per second (defaults to 24)
            
        Returns:
            Formatted timestamp string (HH:MM:SS,mmm)
        """
        # Convert frames to seconds
        seconds = frames / fps

        # Format as SRT timestamp (HH:MM:SS,mmm)
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        millis = int((seconds % 1) * 1000)

        return f"{hours:02}:{minutes:02}:{secs:02},{millis:03}"
    
    @staticmethod
    def apply_offset(subtitles: List[Dict[str, any]], offset: float) -> None:
        """
        Apply a time offset to all subtitles.
        
        Args:
            subtitles: List of subtitle dictionaries to modify in-place
            offset: Offset in frames to add to start and stop times
        """
        for subtitle in subtitles:
            subtitle['start'] += offset
            subtitle['stop'] += offset
        
        logger.info(f"Applied offset of {offset} frames to {len(subtitles)} subtitles")
