#!/usr/bin/env python3
"""
Snapchat Memories Downloader - Main Entry Point

This is the main entry point for the Snapchat Memories Downloader.
It simply delegates to the actual implementation in the scripts/ folder.

For documentation and usage, see docs/CLAUDE.md or docs/README.md
"""

import sys
from pathlib import Path

# Add scripts directory to path
scripts_dir = Path(__file__).parent / 'scripts'
sys.path.insert(0, str(scripts_dir))

from cli import main


if __name__ == '__main__':
    try:
        main()
        print("\n" + "="*60)
        print("Operation completed successfully!")
    except KeyboardInterrupt:
        print("\n\nOperation cancelled by user.")
    except Exception as e:
        print("\n" + "="*60)
        print(f"ERROR: {e}")
        print("="*60)
        import traceback
        traceback.print_exc()
    finally:
        print("\nPress Enter to exit...")
        input()
