"""
Timezone conversion utilities for Snapchat memories.

Converts file timestamps and filenames from UTC to timezone based on GPS coordinates.
Falls back to system local timezone if GPS coordinates are not available.
"""

import os
import sys
from pathlib import Path
from datetime import datetime, timezone
from typing import Tuple, Optional

# Try to import timezonefinder for GPS-based timezone lookup
try:
    from timezonefinder import TimezoneFinder
    HAS_TIMEZONEFINDER = True
except ImportError:
    HAS_TIMEZONEFINDER = False
    TimezoneFinder = None

# Try to use zoneinfo (Python 3.9+), fallback to pytz
try:
    from zoneinfo import ZoneInfo
    HAS_ZONEINFO = True
except ImportError:
    HAS_ZONEINFO = False
    try:
        import pytz
        HAS_PYTZ = True
    except ImportError:
        HAS_PYTZ = False


def parse_gps_coordinates(location_str: Optional[str]) -> Optional[Tuple[float, float]]:
    """Parse GPS coordinates from location string.

    Args:
        location_str: Location string from Snapchat (e.g., "Latitude, Longitude: 42.438072, -82.91975")

    Returns:
        Tuple of (latitude, longitude) or None
    """
    if not location_str:
        return None

    try:
        if 'Latitude, Longitude:' in location_str:
            coords = location_str.split('Latitude, Longitude:')[1].strip()
            lat_str, lon_str = coords.split(',')
            lat = float(lat_str.strip())
            lon = float(lon_str.strip())
            return (lat, lon)
    except (ValueError, IndexError):
        return None

    return None


def get_timezone_from_gps(lat: float, lon: float) -> Optional[str]:
    """Get timezone name from GPS coordinates.

    Args:
        lat: Latitude
        lon: Longitude

    Returns:
        Timezone name (e.g., "America/New_York") or None
    """
    if not HAS_TIMEZONEFINDER:
        return None

    try:
        tf = TimezoneFinder()
        tz_name = tf.timezone_at(lat=lat, lng=lon)
        return tz_name
    except Exception:
        return None


def utc_to_timezone(utc_date_str: str, timezone_name: str) -> Tuple[datetime, str, str]:
    """Convert UTC date string to specific timezone.

    Args:
        utc_date_str: Date string in format "YYYY-MM-DD HH:MM:SS UTC"
        timezone_name: Timezone name (e.g., "America/New_York")

    Returns:
        Tuple of (datetime object in target timezone, formatted string, UTC offset)
    """
    # Parse UTC date string
    date_str = utc_date_str.replace(' UTC', '')
    utc_dt = datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')
    utc_dt = utc_dt.replace(tzinfo=timezone.utc)

    # Convert to target timezone
    if HAS_ZONEINFO:
        try:
            tz = ZoneInfo(timezone_name)
            local_dt = utc_dt.astimezone(tz)
        except Exception:
            # Fallback to system local timezone
            local_dt = utc_dt.astimezone()
    elif HAS_PYTZ:
        try:
            tz = pytz.timezone(timezone_name)
            local_dt = utc_dt.astimezone(tz)
        except Exception:
            # Fallback to system local timezone
            local_dt = utc_dt.astimezone()
    else:
        # No timezone library, use system local
        local_dt = utc_dt.astimezone()

    # Format as string
    local_str = local_dt.strftime('%Y-%m-%d %H:%M:%S') + f' {local_dt.tzname()}'

    # Get UTC offset in format like "-04:00" or "+02:00"
    offset = local_dt.strftime('%z')  # Format: +0200 or -0400
    utc_offset = f"{offset[:3]}:{offset[3:]}"  # Format: +02:00 or -04:00

    return local_dt, local_str, utc_offset


def utc_to_local(utc_date_str: str) -> Tuple[datetime, str]:
    """Convert UTC date string to system local timezone.

    Args:
        utc_date_str: Date string in format "YYYY-MM-DD HH:MM:SS UTC"

    Returns:
        Tuple of (datetime object in local timezone, formatted string)
    """
    # Parse UTC date string
    date_str = utc_date_str.replace(' UTC', '')
    utc_dt = datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')

    # Add UTC timezone info
    utc_dt = utc_dt.replace(tzinfo=timezone.utc)

    # Convert to local timezone
    local_dt = utc_dt.astimezone()

    # Format as string (same format as UTC but with local timezone)
    local_str = local_dt.strftime('%Y-%m-%d %H:%M:%S') + f' {local_dt.tzname()}'

    return local_dt, local_str


def utc_to_gps_timezone(utc_date_str: str, location_str: Optional[str]) -> Tuple[datetime, str, str, Optional[str]]:
    """Convert UTC date to timezone based on GPS coordinates.

    Args:
        utc_date_str: Date string in format "YYYY-MM-DD HH:MM:SS UTC"
        location_str: Location string from Snapchat or None

    Returns:
        Tuple of (datetime object, formatted string, UTC offset, timezone name)
        Falls back to system local timezone if GPS not available
    """
    # Try to get GPS coordinates
    coords = parse_gps_coordinates(location_str)

    if coords and HAS_TIMEZONEFINDER:
        lat, lon = coords
        tz_name = get_timezone_from_gps(lat, lon)

        if tz_name:
            # GPS-based timezone conversion
            local_dt, local_str, utc_offset = utc_to_timezone(utc_date_str, tz_name)
            return local_dt, local_str, utc_offset, tz_name

    # Fallback to system local timezone
    local_dt, local_str = utc_to_local(utc_date_str)
    offset = local_dt.strftime('%z')  # Format: +0200 or -0400
    utc_offset = f"{offset[:3]}:{offset[3:]}" if offset else "+00:00"

    return local_dt, local_str, utc_offset, "system_local"


def generate_local_filename(utc_date_str: str, media_type: str, sid_short: str, extension: str, suffix: str = "") -> str:
    """Generate filename with local timezone.

    Args:
        utc_date_str: Date string in format "YYYY-MM-DD HH:MM:SS UTC"
        media_type: "Image" or "Video"
        sid_short: First 8 characters of SID
        extension: File extension (without dot)
        suffix: Optional suffix like "_overlay" or "_composited"

    Returns:
        Filename in format: YYYY-MM-DD_HHMMSS_Type_sidXXXXXXXX{suffix}.ext
    """
    local_dt, _ = utc_to_local(utc_date_str)

    date_part = local_dt.strftime('%Y-%m-%d')
    time_part = local_dt.strftime('%H%M%S')

    return f"{date_part}_{time_part}_{media_type}_{sid_short}{suffix}.{extension}"


def parse_filename_for_sid(filename: str) -> Optional[str]:
    """Extract SID from filename.

    Args:
        filename: Filename in format YYYY-MM-DD_HHMMSS_Type_sidXXXXXXXX.ext

    Returns:
        SID (8 character prefix) or None if not found
    """
    try:
        # Remove extension
        name = Path(filename).stem

        # Handle overlay and composited suffixes
        if name.endswith('_overlay'):
            name = name[:-8]
        elif name.endswith('_composited'):
            name = name[:-11]

        # Split by underscore and get last part (sid)
        parts = name.split('_')
        if len(parts) >= 4:
            return parts[-1]  # sidXXXXXXXX
    except Exception:
        pass

    return None


def convert_file_timestamps_to_local(file_path: Path, utc_date_str: str, has_pywin32: bool = False):
    """Update file modification and creation times to local timezone.

    Args:
        file_path: Path to file
        utc_date_str: Original UTC date string
        has_pywin32: Whether pywin32 is available (Windows only)
    """
    local_dt, _ = utc_to_local(utc_date_str)
    local_timestamp = local_dt.timestamp()

    # Set modification time (works on all platforms)
    os.utime(file_path, (local_timestamp, local_timestamp))

    # Set creation time (Windows only with pywin32)
    if has_pywin32 and os.name == 'nt':
        try:
            import pywintypes
            import win32file
            import win32con

            # Convert to Windows FILETIME format
            win_timestamp = pywintypes.Time(local_timestamp)

            # Open file handle
            handle = win32file.CreateFile(
                str(file_path),
                win32con.GENERIC_WRITE,
                win32con.FILE_SHARE_READ | win32con.FILE_SHARE_WRITE,
                None,
                win32con.OPEN_EXISTING,
                win32con.FILE_ATTRIBUTE_NORMAL,
                None
            )

            # Set creation time
            win32file.SetFileTime(handle, win_timestamp, None, None)
            handle.close()
        except Exception:
            pass  # Silently fail if pywin32 not available


def update_exif_timezone(file_path: Path, local_dt: datetime, utc_offset: str, has_exiftool: bool = False):
    """Update EXIF metadata with timezone information.

    Args:
        file_path: Path to file
        local_dt: datetime object in local timezone
        utc_offset: UTC offset string (e.g., "-04:00")
        has_exiftool: Whether exiftool is available
    """
    if not has_exiftool:
        return False

    try:
        from snap_config import get_exiftool_path
        import subprocess

        exiftool_cmd = get_exiftool_path()
        if not exiftool_cmd:
            return False

        # Format datetime for EXIF (local time)
        datetime_str = local_dt.strftime('%Y:%m:%d %H:%M:%S')

        # Set EXIF datetime fields with timezone offset
        # DateTimeOriginal: when the photo was taken (in local time)
        # OffsetTimeOriginal: UTC offset for DateTimeOriginal
        result = subprocess.run([
            exiftool_cmd,
            f'-DateTimeOriginal={datetime_str}',
            f'-OffsetTimeOriginal={utc_offset}',
            f'-OffsetTime={utc_offset}',
            f'-OffsetTimeDigitized={utc_offset}',
            '-overwrite_original',
            '-q',
            str(file_path)
        ], capture_output=True, timeout=30, text=True)

        return result.returncode == 0

    except Exception:
        return False


def check_gps_timezone_requirements() -> dict:
    """Check if GPS-based timezone conversion requirements are met.

    Returns:
        Dictionary with availability status and messages
    """
    result = {
        'timezonefinder': HAS_TIMEZONEFINDER,
        'timezone_lib': HAS_ZONEINFO or HAS_PYTZ,
        'timezone_lib_name': 'zoneinfo' if HAS_ZONEINFO else ('pytz' if HAS_PYTZ else None),
        'gps_timezone_available': HAS_TIMEZONEFINDER and (HAS_ZONEINFO or HAS_PYTZ),
        'messages': []
    }

    if not HAS_TIMEZONEFINDER:
        result['messages'].append(
            "timezonefinder not found - GPS-based timezone detection disabled\n"
            "  Install with: pip install timezonefinder"
        )

    if not (HAS_ZONEINFO or HAS_PYTZ):
        result['messages'].append(
            "No timezone library found - using system local timezone only\n"
            "  Python 3.9+: zoneinfo is built-in\n"
            "  Python < 3.9: Install pytz with: pip install pytz"
        )

    if result['gps_timezone_available']:
        result['messages'].append(
            f"GPS-based timezone conversion enabled (using {result['timezone_lib_name']})"
        )

    return result
