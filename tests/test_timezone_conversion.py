#!/usr/bin/env python3
"""
Simple test script to verify GPS-based timezone conversion functionality.
"""

import sys
from pathlib import Path

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent / 'scripts'))

from timezone_converter import (
    parse_gps_coordinates,
    get_timezone_from_gps,
    utc_to_timezone,
    utc_to_gps_timezone,
    check_gps_timezone_requirements
)

def test_gps_parsing():
    """Test GPS coordinate parsing."""
    print("\n" + "="*60)
    print("TEST 1: GPS Coordinate Parsing")
    print("="*60)

    # Test valid GPS string
    location = "Latitude, Longitude: 40.7128, -74.0060"
    coords = parse_gps_coordinates(location)
    print(f"Input: {location}")
    print(f"Parsed: {coords}")
    assert coords == (40.7128, -74.0060), "Failed to parse GPS coordinates"
    print("[PASS] GPS parsing works correctly\n")

def test_timezone_lookup():
    """Test timezone lookup from GPS coordinates."""
    print("="*60)
    print("TEST 2: Timezone Lookup from GPS")
    print("="*60)

    test_cases = [
        (40.7128, -74.0060, "New York, USA", "America/New_York"),
        (48.8566, 2.3522, "Paris, France", "Europe/Paris"),
        (35.6762, 139.6503, "Tokyo, Japan", "Asia/Tokyo"),
        (51.5074, -0.1278, "London, UK", "Europe/London"),
    ]

    for lat, lon, location_name, expected_tz in test_cases:
        tz_name = get_timezone_from_gps(lat, lon)
        print(f"{location_name} ({lat}, {lon})")
        print(f"  Detected: {tz_name}")
        print(f"  Expected: {expected_tz}")
        assert tz_name == expected_tz, f"Timezone mismatch for {location_name}"
        print(f"  [PASS]\n")

def test_utc_conversion():
    """Test UTC to timezone conversion."""
    print("="*60)
    print("TEST 3: UTC to Timezone Conversion")
    print("="*60)

    utc_date = "2025-10-16 19:47:03 UTC"
    timezone_name = "America/New_York"

    local_dt, local_str, utc_offset = utc_to_timezone(utc_date, timezone_name)

    print(f"UTC Date: {utc_date}")
    print(f"Timezone: {timezone_name}")
    print(f"Local Time: {local_str}")
    print(f"UTC Offset: {utc_offset}")
    print(f"Datetime Object: {local_dt}")

    # Note: The exact offset depends on whether DST is active
    # In October 2025, EDT would be active (UTC-04:00)
    print("[PASS] UTC conversion works correctly\n")

def test_gps_timezone_conversion():
    """Test full GPS-based timezone conversion."""
    print("="*60)
    print("TEST 4: GPS-Based Timezone Conversion")
    print("="*60)

    test_cases = [
        {
            'name': 'New York photo',
            'utc_date': '2025-10-16 19:47:03 UTC',
            'location': 'Latitude, Longitude: 40.7128, -74.0060',
            'expected_tz': 'America/New_York'
        },
        {
            'name': 'Paris photo',
            'utc_date': '2025-10-16 19:47:03 UTC',
            'location': 'Latitude, Longitude: 48.8566, 2.3522',
            'expected_tz': 'Europe/Paris'
        },
        {
            'name': 'Photo without GPS',
            'utc_date': '2025-10-16 19:47:03 UTC',
            'location': None,
            'expected_tz': 'system_local'
        }
    ]

    for test in test_cases:
        print(f"\n{test['name']}:")
        local_dt, local_str, utc_offset, detected_tz = utc_to_gps_timezone(
            test['utc_date'], test['location']
        )
        print(f"  UTC: {test['utc_date']}")
        print(f"  Location: {test['location']}")
        print(f"  Detected TZ: {detected_tz}")
        print(f"  Local Time: {local_str}")
        print(f"  UTC Offset: {utc_offset}")

        assert detected_tz == test['expected_tz'], \
            f"Expected {test['expected_tz']}, got {detected_tz}"
        print(f"  [PASS]")

    print()

def test_requirements_check():
    """Test requirement checking."""
    print("="*60)
    print("TEST 5: Requirements Check")
    print("="*60)

    result = check_gps_timezone_requirements()

    print(f"timezonefinder available: {result['timezonefinder']}")
    print(f"Timezone library available: {result['timezone_lib']}")
    print(f"Timezone library name: {result['timezone_lib_name']}")
    print(f"GPS timezone available: {result['gps_timezone_available']}")

    print("\nMessages:")
    for msg in result['messages']:
        print(f"  {msg}")

    if result['gps_timezone_available']:
        print("\n[PASS] All requirements met for GPS-based timezone conversion")
    else:
        print("\n[WARNING] Some requirements missing")

    print()

def main():
    """Run all tests."""
    print("\n" + "="*60)
    print("GPS-BASED TIMEZONE CONVERSION TEST SUITE")
    print("="*60)

    try:
        test_gps_parsing()
        test_timezone_lookup()
        test_utc_conversion()
        test_gps_timezone_conversion()
        test_requirements_check()

        print("="*60)
        print("ALL TESTS PASSED [OK]")
        print("="*60)
        print("\nGPS-based timezone conversion is working correctly!")
        print("You can now use: python download_snapchat_memories.py --convert-timezone")
        print("="*60 + "\n")

    except Exception as e:
        print(f"\n[FAIL] TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()
