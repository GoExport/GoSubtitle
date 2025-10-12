"""
Main window module for GoSubtitle application.

This module contains the MainWindow class which manages the GUI and user interactions.
"""

from pathlib import Path
from typing import List, Dict, Optional
import logging

from PyQt6.QtWidgets import QMainWindow, QMessageBox, QFileDialog, QWidget
from PyQt6 import uic

from .subtitle_processor import SubtitleProcessor

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Path configuration - paths relative to this file
BASE_DIR = Path(__file__).resolve().parent.parent
UI_DIR = BASE_DIR / "ui"


class MainWindow(QMainWindow):
    """
    Main application window for GoSubtitle.
    
    Handles user interactions for loading Movie XML files, editing subtitles,
    and exporting to SRT format.
    """
    
    def __init__(self):
        """Initialize the main window and set up UI connections."""
        super(MainWindow, self).__init__()
        
        # Load UI from file
        uic.loadUi(str(UI_DIR / "main_window.ui"), self)
        self.setWindowTitle("GoSubtitle")
        
        # Initialize subtitle processor
        self.processor = SubtitleProcessor()
        
        # Connect UI signals to slots
        self.openButton.clicked.connect(self.open_file)
        self.saveButton.clicked.connect(self.save_srt)
        self.offsetSpinBox.valueChanged.connect(self.offset_beginning)
        self.massButtonoSave.clicked.connect(self.mass_replace_speaker)
        
        # State variables
        self.subtitles: List[Dict[str, any]] = []
        self.current_offset: float = 0.0
        self.timeline_widgets: List[QWidget] = []
        
        logger.info("MainWindow initialized successfully")
    
    def open_file(self) -> bool:
        """
        Open a file dialog to select and load a Movie XML file.
        
        Returns:
            True if file was loaded successfully, False otherwise
        """
        file_dialog = QFileDialog(self)
        file_path, file_type = file_dialog.getOpenFileName(
            self, 
            "Open Movie XML File", 
            "", 
            "XML Files (*.xml);;All Files (*)"
        )
        
        if not file_path:
            QMessageBox.warning(self, "No File Selected", "No file was selected.")
            logger.warning("File selection cancelled by user")
            return False
        
        self.movieFile.setText(file_path)
        logger.info(f"Selected file: {file_path}")
        return self.parse_xml(file_path)
    
    def parse_xml(self, file_path: str) -> bool:
        """
        Parse the XML file and load subtitles.
        
        Args:
            file_path: Path to the XML file to parse
            
        Returns:
            True if parsing was successful, False otherwise
        """
        try:
            logger.info(f"Attempting to parse XML file: {file_path}")
            self.subtitles = self.processor.parse_xml(file_path)
            
            if not self.subtitles:
                QMessageBox.warning(
                    self, 
                    "No Subtitles Found", 
                    "The XML file contains no valid subtitle data."
                )
                logger.warning("No subtitles found in XML file")
                return False
            
            # Reset offset when loading new file
            self.current_offset = 0.0
            self.offsetSpinBox.setValue(0)
            
            self.display_subtitles(self.subtitles)
            self.populate_speaker_combo()
            
            logger.info(f"Successfully loaded {len(self.subtitles)} subtitles")
            return True
            
        except FileNotFoundError:
            QMessageBox.critical(
                self, 
                "File Not Found", 
                f"The file '{file_path}' was not found."
            )
            logger.error(f"File not found: {file_path}")
            return False
            
        except Exception as e:
            QMessageBox.critical(
                self, 
                "Error", 
                f"Failed to read file: {str(e)}"
            )
            logger.error(f"Error parsing XML: {e}", exc_info=True)
            return False
    
    def display_subtitles(self, subtitles: List[Dict[str, any]]) -> None:
        """
        Display subtitles in the timeline layout.
        
        Creates a timeline object widget for each subtitle and sets up proper
        tab ordering for intuitive keyboard navigation.
        
        Args:
            subtitles: List of subtitle dictionaries to display
        """
        # Clear existing timeline objects
        while self.timelineLayout.layout().count():
            item = self.timelineLayout.layout().takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        self.timeline_widgets.clear()
        
        # Keep track of previous widget for tab order
        previous_speaker_widget = None
        previous_content_widget = None
        
        for idx, subtitle in enumerate(subtitles):
            # Load a fresh copy of the timeline object UI
            item = uic.loadUi(str(UI_DIR / "timeline_object.ui"))
            
            # Set subtitle information
            start_time = SubtitleProcessor.format_time(subtitle['start'])
            end_time = SubtitleProcessor.format_time(subtitle['stop'])
            item.label.setText(f"Start: {start_time}, End: {end_time}")
            item.speaker.setText(subtitle['speaker'])
            item.content.setPlainText(subtitle['text'])
            
            # Make content editable
            item.content.setReadOnly(False)
            
            # Connect speaker change with proper closure to capture correct index
            def make_speaker_callback(index: int, widget: QWidget) -> callable:
                """Create a callback that properly captures the index."""
                def callback():
                    self.change_speaker(index, widget.text())
                return callback
            
            item.speaker.editingFinished.connect(
                make_speaker_callback(idx, item.speaker)
            )
            
            # Connect content change with proper closure
            def make_content_callback(index: int, widget: QWidget) -> callable:
                """Create a callback that properly captures the index."""
                def callback():
                    self.change_content(index, widget.toPlainText())
                return callback
            
            item.content.textChanged.connect(
                make_content_callback(idx, item.content)
            )
            
            # Set up tab order - speaker -> content -> next speaker
            if previous_content_widget is not None:
                self.setTabOrder(previous_content_widget, item.speaker)
            if previous_speaker_widget is not None:
                self.setTabOrder(item.speaker, item.content)
            
            previous_speaker_widget = item.speaker
            previous_content_widget = item.content
            
            # Add to layout and track widget
            self.timelineLayout.layout().addWidget(item)
            self.timeline_widgets.append(item)
        
        logger.info(f"Displayed {len(subtitles)} subtitle timeline objects with proper tab order")

    def offset_beginning(self, offset: int) -> None:
        """
        Offset all subtitles by the specified amount.
        
        Args:
            offset: Offset in frames to apply to all subtitles
        """
        if not self.subtitles:
            QMessageBox.warning(
                self, 
                "No Subtitles", 
                "No subtitles to offset. Please load a Movie XML file first."
            )
            logger.warning("Attempted to offset with no subtitles loaded")
            return
        
        # Calculate the difference from the previous offset
        offset_delta = offset - self.current_offset
        self.current_offset = offset
        
        # Apply only the delta to preserve user modifications
        SubtitleProcessor.apply_offset(self.subtitles, offset_delta)
        
        self.display_subtitles(self.subtitles)
        logger.info(f"Applied offset delta of {offset_delta} frames (total offset: {offset})")
    
    def change_speaker(self, index: int, new_speaker: str) -> None:
        """
        Update the speaker for a specific subtitle.
        
        Args:
            index: Index of the subtitle to update
            new_speaker: New speaker name
        """
        if 0 <= index < len(self.subtitles):
            old_speaker = self.subtitles[index]['speaker']
            self.subtitles[index]['speaker'] = new_speaker
            self.populate_speaker_combo()
            logger.debug(f"Changed speaker at index {index} from '{old_speaker}' to '{new_speaker}'")
        else:
            logger.warning(f"Invalid subtitle index: {index}")
    
    def change_content(self, index: int, new_content: str) -> None:
        """
        Update the content text for a specific subtitle.
        
        Args:
            index: Index of the subtitle to update
            new_content: New subtitle text
        """
        if 0 <= index < len(self.subtitles):
            self.subtitles[index]['text'] = new_content
            logger.debug(f"Changed content at index {index}")
        else:
            logger.warning(f"Invalid subtitle index: {index}")
    
    def populate_speaker_combo(self) -> None:
        """
        Populate the combo box with unique speakers from the subtitles.
        
        Extracts all unique speaker names (including combined speakers like
        "Speaker1/Speaker2") and populates the mass replace combo box.
        """
        if not self.subtitles:
            return
        
        # Get unique speakers (including combined speakers)
        unique_speakers = set(subtitle['speaker'] for subtitle in self.subtitles)
        
        # Sort speakers alphabetically
        sorted_speakers = sorted(unique_speakers)
        
        # Clear and populate combo box
        self.massComboSpeaker.clear()
        self.massComboSpeaker.addItems(sorted_speakers)
        
        logger.debug(f"Populated speaker combo with {len(sorted_speakers)} unique speakers")
    
    def mass_replace_speaker(self) -> None:
        """
        Replace all occurrences of the selected speaker with a new name.
        
        Shows a confirmation dialog with the number of replacements made.
        """
        if not self.subtitles:
            QMessageBox.warning(
                self, 
                "No Subtitles", 
                "No subtitles to modify. Please load a Movie XML file first."
            )
            logger.warning("Attempted mass replace with no subtitles loaded")
            return
        
        # Get the selected speaker from combo box
        selected_speaker = self.massComboSpeaker.currentText()
        if not selected_speaker:
            QMessageBox.warning(
                self, 
                "No Speaker Selected", 
                "Please select a speaker from the dropdown."
            )
            logger.warning("Mass replace attempted with no speaker selected")
            return
        
        # Get the replacement text
        replacement_text = self.massLineReplace.text().strip()
        if not replacement_text:
            QMessageBox.warning(
                self, 
                "Empty Replacement", 
                "You can't replace with an empty text. Please enter a new speaker name."
            )
            logger.warning("Mass replace attempted with empty replacement text")
            return
        
        # Count and replace
        replace_count = 0
        for subtitle in self.subtitles:
            if subtitle['speaker'] == selected_speaker:
                subtitle['speaker'] = replacement_text
                replace_count += 1
        
        # Update the display and combo box
        self.display_subtitles(self.subtitles)
        self.populate_speaker_combo()
        
        # Clear the replacement field
        self.massLineReplace.clear()
        
        # Show success message
        QMessageBox.information(
            self, 
            "Success", 
            f"Replaced {replace_count} occurrence(s) of '{selected_speaker}' with '{replacement_text}'."
        )
        logger.info(f"Mass replaced {replace_count} occurrences of '{selected_speaker}' with '{replacement_text}'")
    
    def save_srt(self) -> None:
        """
        Save subtitles to an SRT file.
        
        Opens a file dialog to select save location and writes all subtitles
        in SRT format with speaker names.
        """
        if not self.subtitles:
            QMessageBox.warning(
                self, 
                "No Subtitles", 
                "No subtitles to save. Please load a Movie XML file first."
            )
            logger.warning("Attempted to save with no subtitles loaded")
            return
        
        file_dialog = QFileDialog(self)
        save_path, _ = file_dialog.getSaveFileName(
            self, 
            "Save SRT File", 
            "", 
            "SRT Files (*.srt);;All Files (*)"
        )
        
        if not save_path:
            QMessageBox.warning(
                self, 
                "No File Selected", 
                "No file was selected for saving."
            )
            logger.warning("Save cancelled by user")
            return
        
        try:
            with open(save_path, 'w', encoding='utf-8') as f:
                for idx, subtitle in enumerate(self.subtitles, start=1):
                    start_time = SubtitleProcessor.format_time(subtitle['start'])
                    end_time = SubtitleProcessor.format_time(subtitle['stop'])
                    
                    f.write(f"{idx}\n")
                    f.write(f"{start_time} --> {end_time}\n")
                    f.write(f"{subtitle['speaker']}: {subtitle['text']}\n\n")
            
            QMessageBox.information(
                self, 
                "Success", 
                f"Subtitles saved to {save_path}"
            )
            logger.info(f"Successfully saved {len(self.subtitles)} subtitles to {save_path}")
            
        except Exception as e:
            QMessageBox.critical(
                self, 
                "Error", 
                f"Failed to save file: {str(e)}"
            )
            logger.error(f"Error saving SRT file: {e}", exc_info=True)

