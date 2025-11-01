"""
Timezone conversion tracking for Snapchat memories.

Stores detailed timezone conversion information for each file including:
- Original UTC timestamp
- GPS coordinates
- Detected timezone from GPS
- Converted local timestamp
- UTC offset
"""

import json
import os
from typing import Dict, Optional
from datetime import datetime


class TimezoneConversionTracker:
    """Track timezone conversion details for each file."""

    def __init__(self, tracking_file: str = "timezone_conversions.json"):
        """Initialize timezone conversion tracker.

        Args:
            tracking_file: Path to JSON file for storing conversion tracking
        """
        self.tracking_file = tracking_file
        self.conversions = self._load_tracking()

    def _load_tracking(self) -> Dict:
        """Load timezone conversion tracking from JSON file."""
        if os.path.exists(self.tracking_file):
            try:
                with open(self.tracking_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if not isinstance(data, dict):
                        raise ValueError("Tracking file is not a JSON object")
                    return data
            except (json.JSONDecodeError, ValueError) as e:
                print(f"\n{'='*70}")
                print(f"WARNING: Timezone conversion tracking file is corrupted!")
                print(f"{'='*70}")
                print(f"File: {self.tracking_file}")
                print(f"Error: {e}")
                print(f"\nStarting fresh with empty tracking file.")
                print(f"{'='*70}\n")
                return {'conversions': {}}
            except Exception as e:
                print(f"WARNING: Failed to load tracking file: {e}")
                return {'conversions': {}}
        return {'conversions': {}}

    def save_tracking(self):
        """Save timezone conversion tracking to JSON file."""
        try:
            with open(self.tracking_file, 'w', encoding='utf-8') as f:
                json.dump(self.conversions, f, indent=2)
        except Exception as e:
            print(f"ERROR: Failed to save timezone conversion tracking: {e}")
            raise

    def is_converted(self, sid: str) -> bool:
        """Check if a file has been converted.

        Args:
            sid: Session ID

        Returns:
            True if already converted
        """
        return sid in self.conversions.get('conversions', {})

    def record_conversion(
        self,
        sid: str,
        utc_timestamp: str,
        gps_coords: Optional[tuple],
        detected_timezone: str,
        local_timestamp: str,
        utc_offset: str,
        file_path: str,
        file_type: str
    ):
        """Record a timezone conversion.

        Args:
            sid: Session ID
            utc_timestamp: Original UTC timestamp (e.g., "2025-10-16 19:47:03 UTC")
            gps_coords: Tuple of (latitude, longitude) or None
            detected_timezone: Timezone name (e.g., "America/New_York", "system_local")
            local_timestamp: Converted local timestamp (e.g., "2025-10-16 15:47:03 EDT")
            utc_offset: UTC offset string (e.g., "-04:00", "+02:00")
            file_path: Path to the converted file
            file_type: Type of file (e.g., "image", "video", "overlay", "composited_image")
        """
        if 'conversions' not in self.conversions:
            self.conversions['conversions'] = {}

        self.conversions['conversions'][sid] = {
            'original_utc': utc_timestamp,
            'gps_coordinates': {
                'latitude': gps_coords[0] if gps_coords else None,
                'longitude': gps_coords[1] if gps_coords else None
            } if gps_coords else None,
            'detected_timezone': detected_timezone,
            'local_timestamp': local_timestamp,
            'utc_offset': utc_offset,
            'file_path': str(file_path),
            'file_type': file_type,
            'converted_at': datetime.now().isoformat()
        }

        self.save_tracking()

    def get_conversion(self, sid: str) -> Optional[Dict]:
        """Get conversion details for a SID.

        Args:
            sid: Session ID

        Returns:
            Conversion dictionary or None
        """
        return self.conversions.get('conversions', {}).get(sid)

    def get_stats(self) -> Dict:
        """Get statistics about conversions.

        Returns:
            Dictionary with conversion statistics
        """
        conversions = self.conversions.get('conversions', {})
        total = len(conversions)

        # Count by timezone
        timezone_counts = {}
        gps_based = 0
        system_based = 0

        for conv in conversions.values():
            tz = conv.get('detected_timezone', 'unknown')
            timezone_counts[tz] = timezone_counts.get(tz, 0) + 1

            if conv.get('gps_coordinates'):
                gps_based += 1
            else:
                system_based += 1

        return {
            'total_conversions': total,
            'gps_based_conversions': gps_based,
            'system_based_conversions': system_based,
            'timezones': timezone_counts
        }
