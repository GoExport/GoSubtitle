"""
Parameters module for GoSubtitle application.

Handles command-line argument parsing and parameter management.
"""

import argparse
from typing import Dict, Optional


class Parameters:
    """
    Command-line parameter parser and manager.
    
    Provides a unified interface for accessing command-line arguments
    and application parameters.
    """
    
    def __init__(self):
        """Initialize the argument parser with all available options."""
        self.parser = argparse.ArgumentParser(
            description="GoSubtitle - Convert Movie XML files to SRT subtitles",
            epilog="Examples:\n"
                   "  GoSubtitle.exe -f movie.xml\n"
                   "  GoSubtitle.exe -f movie.xml -s subtitles.srt -o 24\n"
                   "  GoSubtitle.exe -f movie.xml -r \"John:Jane\" -r \"Bob:Robert\"\n"
                   "  GoSubtitle.exe -f movie.xml --max-words 15 --verbose\n",
            formatter_class=argparse.RawDescriptionHelpFormatter
        )
        
        # GUI mode flag
        self.parser.add_argument(
            '-g', '--gui',
            action='store_true',
            help='Force GUI mode even when console is available'
        )
        
        # Input/Output files
        self.parser.add_argument(
            '-f', '--file',
            type=str,
            metavar='PATH',
            help='Input Movie XML file path'
        )
        
        self.parser.add_argument(
            '-s', '--srt',
            type=str,
            metavar='PATH',
            help='Output SRT file path (default: same as input with .srt extension)'
        )
        
        # Processing options
        self.parser.add_argument(
            '-o', '--offset',
            type=float,
            default=0,
            metavar='FRAMES',
            help='Offset all subtitles by the specified number of frames (can be negative)'
        )
        
        self.parser.add_argument(
            '-w', '--max-words',
            type=int,
            metavar='COUNT',
            help='Maximum words per subtitle line (default: 10)'
        )
        
        self.parser.add_argument(
            '-r', '--replace',
            action='append',
            metavar='OLD:NEW',
            dest='replace_list',
            help='Replace speaker names in format "OldName:NewName" (can be used multiple times)'
        )
        
        # Output options
        self.parser.add_argument(
            '-v', '--verbose',
            action='store_true',
            help='Display detailed statistics about subtitles'
        )
        
        self.parser.add_argument(
            '--version',
            action='version',
            version='GoSubtitle 1.0.0',
            help='Show program version and exit'
        )
        
        self.args = self.parser.parse_args()
        
        # Process speaker replacements into a dictionary
        self._process_speaker_replacements()
    
    def _process_speaker_replacements(self) -> None:
        """
        Process the list of speaker replacements into a dictionary.
        
        Converts command-line arguments like "John:Jane" into a dictionary
        mapping old names to new names.
        """
        replace_map = {}
        
        if self.args.replace_list:
            for replacement in self.args.replace_list:
                if ':' not in replacement:
                    print(f"Warning: Invalid replacement format '{replacement}'. Expected 'OldName:NewName'")
                    continue
                
                old_name, new_name = replacement.split(':', 1)
                old_name = old_name.strip()
                new_name = new_name.strip()
                
                if not old_name or not new_name:
                    print(f"Warning: Empty name in replacement '{replacement}'")
                    continue
                
                replace_map[old_name] = new_name
        
        # Store the processed map
        self.args.replace_speakers = replace_map if replace_map else None

    def get_param_value(self, param_name: str):
        """
        Get the value of a parameter by name.
        
        Args:
            param_name: Name of the parameter to retrieve
            
        Returns:
            The parameter value, or None if not found
        """
        return getattr(self.args, param_name, None)
    
    def set_param_value(self, param_name: str, value):
        """
        Set the value of a parameter.
        
        Args:
            param_name: Name of the parameter to set
            value: New value for the parameter
        """
        setattr(self.args, param_name, value)