# GPS-Based Timezone Conversion Implementation Summary

## Overview

This implementation upgrades the timezone conversion feature to use GPS coordinates to automatically detect and convert timestamps to the **actual timezone where each photo/video was taken**, rather than just converting to the system's local timezone.

## Key Features

### 1. GPS-Based Timezone Detection
- Uses `timezonefinder` library to lookup timezone from GPS coordinates
- Automatically determines timezone (e.g., "America/New_York", "Europe/Paris") from lat/long
- Falls back to system local timezone if GPS coordinates not available

### 2. EXIF Metadata with Timezone Offset
- Properly sets EXIF metadata with timezone information:
  - `DateTimeOriginal`: Local time when photo was taken
  - `OffsetTimeOriginal`: UTC offset (e.g., "-04:00" for EDT, "+02:00" for CEST)
  - `OffsetTime` and `OffsetTimeDigitized`: UTC offsets
- Allows photo software to correctly display time in any timezone

### 3. Detailed Tracking
- New `timezone_conversions.json` file tracks:
  - Original UTC timestamp
  - GPS coordinates used
  - Detected timezone name
  - Converted local timestamp
  - UTC offset
  - File path and type
  - Conversion timestamp
- Updated `download_progress.json` to store GPS location data

### 4. Statistics and Reporting
- Shows timezone distribution across your memories
- Counts GPS-based vs system timezone fallbacks
- Lists all detected timezones with file counts

### 5. User-Friendly Warnings
- **Clear warning** when running `--convert-timezone` without required dependencies
- **Interactive prompt** - user must confirm to proceed with system timezone fallback
- **Detailed explanation** of what features won't work without GPS timezone
- **Installation instructions** shown directly in the warning

## Implementation Details

### Files Modified

1. **`scripts/timezone_converter.py`** - Enhanced timezone conversion
   - Added GPS coordinate parsing
   - Added timezone lookup from coordinates
   - Added EXIF metadata timezone updates
   - Added requirement checking and validation

2. **`scripts/progress.py`** - Progress tracking enhancements
   - Store GPS location data during download
   - Add method to retrieve location for timezone conversion

3. **`scripts/downloader.py`** - Main download orchestration
   - Updated `convert_all_to_local_timezone()` method
   - Uses GPS-based timezone conversion
   - Updates EXIF metadata with timezone offset
   - Displays timezone statistics after conversion

4. **`CLAUDE.md`** - Documentation updates
   - Updated timezone conversion documentation
   - Added GPS-based timezone examples
   - Added EXIF metadata explanation
   - Updated version history

### Files Created

1. **`scripts/timezone_tracker.py`** - New tracking system
   - Track detailed timezone conversion information
   - Store conversion history
   - Provide statistics on conversions

2. **`requirements.txt`** - Dependency management
   - `timezonefinder>=6.0.0` for GPS-based timezone lookup
   - `pytz>=2023.3` for Python < 3.9 (Python 3.9+ has built-in zoneinfo)

## Dependencies

### Required
- `requests>=2.31.0` - HTTP requests for downloads

### Optional (for GPS-based timezone conversion)
- `timezonefinder>=6.0.0` - **GPS-based timezone detection** (highly recommended)
- `pytz>=2023.3` - Timezone support (Python < 3.9 only, 3.9+ has built-in zoneinfo)

**Note:** GPS timezone conversion is **optional** but **highly recommended**. Without it:
- All files converted to system timezone (not GPS-based)
- Photos from different locations all use same timezone
- EXIF timezone metadata not set correctly
- User will see a **warning** and must confirm to proceed

### Other Optional Dependencies
- `Pillow>=10.0.0` - Image overlay compositing
- `pywin32>=306` - Windows file creation time (Windows only)

## EXIF Metadata Standards

The implementation follows proper EXIF standards for timezone information:

1. **DateTime Fields**: Store local time (not UTC)
   - `DateTimeOriginal`: When photo was taken (local time)
   - `DateTimeDigitized`: When photo was digitized (local time)
   - `DateTime`: File modification time (local time)

2. **Offset Fields**: Store UTC offset
   - `OffsetTimeOriginal`: UTC offset for DateTimeOriginal (e.g., "-04:00")
   - `OffsetTimeDigitized`: UTC offset for DateTimeDigitized
   - `OffsetTime`: UTC offset for DateTime

3. **GPS Fields**: Already set during download
   - `GPSLatitude`: Latitude coordinate
   - `GPSLongitude`: Longitude coordinate
   - `GPSLatitudeRef`: N or S
   - `GPSLongitudeRef`: E or W

## Usage

### Install Dependencies
```bash
# Install all dependencies
pip install -r requirements.txt

# Or install only timezone conversion dependencies
pip install timezonefinder
pip install pytz  # Only needed for Python < 3.9
```

### Run Timezone Conversion
```bash
python download_snapchat_memories.py --convert-timezone
```

### Expected Output (With timezonefinder installed)
```
Converting files from UTC to GPS-based timezone...
GPS-based timezone conversion enabled (using zoneinfo)
System timezone (fallback): EDT

Processing images/...
Processing videos/...
Processing overlays/...

Timezone Conversion Complete!
============================================================
Total files processed: 500
Converted: 500
Skipped (already converted): 0
Failed: 0
============================================================

Timezone Statistics:
GPS-based conversions: 450
System timezone fallbacks: 50

Timezones detected:
  America/New_York: 350 files
  Europe/London: 75 files
  Asia/Tokyo: 25 files
  system_local: 50 files

Conversion details saved to: timezone_conversions.json
============================================================
```

### Expected Output (WITHOUT timezonefinder installed)
```
Converting files from UTC to GPS-based timezone...

======================================================================
WARNING: GPS-based timezone conversion is NOT available!
======================================================================

Missing required library: timezonefinder
  Install with: pip install timezonefinder

Without GPS-based timezone conversion:
  - All files will be converted to your SYSTEM timezone (Eastern Daylight Time)
  - Photos taken in different timezones will ALL use the same timezone
  - EXIF timezone metadata will NOT be set correctly

With GPS-based timezone conversion:
  - Each file uses the timezone where it was taken (e.g., NYC photos use EDT)
  - Photos from different locations get correct local times
  - EXIF metadata includes proper timezone offsets

======================================================================
Continue with system timezone only? (yes/no): no
======================================================================

[15:47:03] Timezone conversion cancelled.
[15:47:03] Install timezonefinder and try again:
[15:47:03]   pip install timezonefinder
```

## Example Use Cases

### Scenario 1: Travel Photography
User traveled from New York to Paris:
- Photos in NYC: Converted to EDT (UTC-04:00)
- Photos in Paris: Converted to CEST (UTC+02:00)
- All photos show correct local time when taken

### Scenario 2: Memories Without GPS
Some older Snapchat memories don't have GPS:
- Falls back to system local timezone
- Still properly sets EXIF metadata
- Tracked separately in statistics

### Scenario 3: Reviewing Conversion Details
User wants to see which timezone was used for each file:
- Check `timezone_conversions.json`
- See GPS coordinates, detected timezone, UTC offset
- Verify conversion was correct

## Testing

### Unit Tests
Test cases to verify:
1. GPS coordinate parsing from Snapchat location strings
2. Timezone lookup from coordinates
3. UTC to timezone conversion
4. EXIF metadata updates
5. Filename generation with timezone

### Integration Tests
1. Download files with GPS coordinates
2. Run timezone conversion
3. Verify filenames changed correctly
4. Verify EXIF metadata has timezone offsets
5. Verify tracking files created correctly

## Backward Compatibility

- Existing `download_progress.json` files are automatically upgraded
- Missing `location` field is added with `None` value
- Old timezone conversions (system-based) continue to work
- Safe to run on partially converted file sets

## Future Enhancements

1. **Manual Timezone Override**
   - Allow user to specify timezone for files without GPS
   - Useful for fixing incorrect timezone detections

2. **Bulk Timezone Operations**
   - Convert only specific date ranges
   - Convert only specific folders
   - Revert timezone conversions

3. **Timezone Validation**
   - Verify timezone detection accuracy
   - Flag suspicious timezone detections
   - Allow user review before applying

4. **Export Functionality**
   - Export timezone conversion report to CSV
   - Include travel timeline based on timezone changes
   - Generate map of where photos were taken

## Notes

- GPS-based timezone detection requires `timezonefinder` library
- Falls back gracefully to system timezone if library not available
- EXIF metadata updates require ExifTool to be installed
- Safe to run multiple times - skips already converted files
- Original UTC timestamps preserved in progress file for reference
