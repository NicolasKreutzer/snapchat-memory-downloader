"""
Centralized error logging system for Snapchat memories downloader.

Logs all errors during downloading and compositing to a structured JSON file
with timestamps, command context, and full error details.
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional, Any


class ErrorLogger:
    """Centralized error logging for download and composite operations."""

    def __init__(self, log_file: str = "errors.json"):
        """Initialize error logger.

        Args:
            log_file: Path to JSON file for storing error logs
        """
        self.log_file = log_file
        self.logs = self._load_logs()

    def _load_logs(self) -> Dict:
        """Load existing error logs from JSON file."""
        if os.path.exists(self.log_file):
            try:
                with open(self.log_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if not isinstance(data, dict):
                        raise ValueError("Error log file is not a JSON object")
                    return data
            except Exception as e:
                print(f"WARNING: Could not load error log file: {e}")
                print(f"Creating new error log file...")

        return {
            'download_errors': [],
            'composite_errors': [],
            'other_errors': []
        }

    def _save_logs(self):
        """Save error logs to JSON file with atomic write."""
        import tempfile

        temp_file = self.log_file + '.tmp'
        try:
            with open(temp_file, 'w', encoding='utf-8') as f:
                json.dump(self.logs, f, indent=2)

            # Replace original file with temp file
            if os.path.exists(self.log_file):
                os.replace(temp_file, self.log_file)
            else:
                os.rename(temp_file, self.log_file)
        except Exception as e:
            if os.path.exists(temp_file):
                try:
                    os.remove(temp_file)
                except:
                    pass
            print(f"ERROR: Failed to save error log: {e}")
            raise

    def log_download_error(
        self,
        sid: str,
        url: str,
        error_message: str,
        exception: Optional[Exception] = None,
        additional_context: Optional[Dict[str, Any]] = None
    ):
        """Log a download error.

        Args:
            sid: Session ID
            url: Download URL
            error_message: Human-readable error message
            exception: Optional exception object for additional details
            additional_context: Optional dict with extra context (e.g., retry count)
        """
        error_entry = {
            'timestamp': datetime.now().isoformat(),
            'operation': 'download',
            'sid': sid,
            'url': url,
            'error_message': error_message,
            'error_type': type(exception).__name__ if exception else 'Unknown',
            'error_details': str(exception) if exception else error_message
        }

        if additional_context:
            error_entry['additional_context'] = additional_context

        self.logs['download_errors'].append(error_entry)
        self._save_logs()

    def log_composite_error(
        self,
        sid: str,
        media_type: str,
        base_file: str,
        overlay_file: str,
        error_message: str,
        exception: Optional[Exception] = None,
        command: Optional[str] = None,
        additional_context: Optional[Dict[str, Any]] = None
    ):
        """Log a composite error.

        Args:
            sid: Session ID
            media_type: 'image' or 'video'
            base_file: Path to base file
            overlay_file: Path to overlay file
            error_message: Human-readable error message
            exception: Optional exception object for additional details
            command: Optional command that was running (e.g., ffmpeg command)
            additional_context: Optional dict with extra context (e.g., ffmpeg stderr)
        """
        error_entry = {
            'timestamp': datetime.now().isoformat(),
            'operation': 'composite',
            'media_type': media_type,
            'sid': sid,
            'base_file': str(base_file),
            'overlay_file': str(overlay_file),
            'error_message': error_message,
            'error_type': type(exception).__name__ if exception else 'Unknown',
            'error_details': str(exception) if exception else error_message
        }

        if command:
            error_entry['command'] = command

        if additional_context:
            error_entry['additional_context'] = additional_context

        self.logs['composite_errors'].append(error_entry)
        self._save_logs()

    def log_general_error(
        self,
        operation: str,
        error_message: str,
        exception: Optional[Exception] = None,
        additional_context: Optional[Dict[str, Any]] = None
    ):
        """Log a general error not specific to download or composite.

        Args:
            operation: Description of what operation was being performed
            error_message: Human-readable error message
            exception: Optional exception object for additional details
            additional_context: Optional dict with extra context
        """
        error_entry = {
            'timestamp': datetime.now().isoformat(),
            'operation': operation,
            'error_message': error_message,
            'error_type': type(exception).__name__ if exception else 'Unknown',
            'error_details': str(exception) if exception else error_message
        }

        if additional_context:
            error_entry['additional_context'] = additional_context

        self.logs['other_errors'].append(error_entry)
        self._save_logs()

    def get_summary(self) -> Dict[str, int]:
        """Get summary statistics of logged errors.

        Returns:
            Dict with counts of each error type
        """
        return {
            'download_errors': len(self.logs['download_errors']),
            'composite_errors': len(self.logs['composite_errors']),
            'other_errors': len(self.logs['other_errors']),
            'total_errors': (
                len(self.logs['download_errors']) +
                len(self.logs['composite_errors']) +
                len(self.logs['other_errors'])
            )
        }

    def get_recent_errors(self, count: int = 10) -> list:
        """Get the most recent errors across all categories.

        Args:
            count: Number of recent errors to return

        Returns:
            List of most recent error entries
        """
        all_errors = (
            self.logs['download_errors'] +
            self.logs['composite_errors'] +
            self.logs['other_errors']
        )

        # Sort by timestamp (most recent first)
        all_errors.sort(key=lambda x: x['timestamp'], reverse=True)

        return all_errors[:count]

    def clear_logs(self):
        """Clear all error logs."""
        self.logs = {
            'download_errors': [],
            'composite_errors': [],
            'other_errors': []
        }
        self._save_logs()
