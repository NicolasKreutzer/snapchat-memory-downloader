I am not a bot but the rest of this is. Created with that claude fucker. This assumes you've exported your data and they sent you something like my_data_blah blah folder (after extracting zip) with html in it.

Added pre-built releases for all platforms -------------------------------->>>>>>>>>>>>>>>>>>>>>>>>>> https://github.com/shoeless03/snapchat-memory-downloader/releases

I don't have a Mac so let me know if it works.

Recommended you

create a new folder for each export and place this program inside.
move the folder from snapchat (after extracting zip) into same folder.
change that folder (my_data_blah blah folder) name to "data from snapchat".
download release or follow build instructions below.

snapchat gives the original video/image and the overlay as seperate files, this scipt doesn't remove them, just origanizes them. You can re-create the effect with the menu to create new images/vidoes with the snapchat overlay embedded (leaving originals untouched) in a new folder.

see below for futher usage.

If this tool has helped you and you feel like contributing please consider donating to Palestine Children's Relief Fund: https://www.pcrf.net/donate

End human.

# Snapchat Memory Downloader

This tool automatically downloads all your Snapchat memories (photos and videos) from the HTML export file, organizing them with human-readable filenames and preserving the original creation timestamps.

## Key Features

- 🎯 **Interactive Menu**: User-friendly interface with arrow key navigation.
- 📁 **Organized Output**: Sorts files into `images/`, `videos/`, and `overlays/`.
- 📅 **Smart Naming**: Human-readable filenames with timestamps (e.g., `2025-10-16_194703_Image_9ce001ca.jpg`).
- ⏰ **Metadata Preservation**: Preserves original Snapchat creation dates in file metadata.
- 🎨 **Overlay Compositing**: Can re-apply Snapchat overlays (stickers, text, filters) to your local files.
- 📍 **GPS Embedding**: Automatically embeds GPS coordinates if ExifTool is installed.
- 🌍 **Timezone Correction**: Convert UTC timestamps to the local time of where the photo/video was taken.
- 🛡️ **Robust**: Handles rate limits (HTTP 429) allowing you to resume if interrupted.

---

## Installation

### Option 1: Pre-built Executables (Recommended)
**No Python installation required.** Just download, extract, and run.

1.  Download the **[latest release](../../releases/latest)** for your platform (Windows, macOS, or Linux).
2.  Unzip the downloaded file.
3.  Proceed to [Usage](#usage).

### Option 2: Run from Source (Advanced)
For developers or users who prefer running the raw Python script.

**Prerequisites:** [Python 3.11+](https://www.python.org/downloads/)

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/shoeless03/snapchat-memory-downloader.git
    cd snapchat-memory-downloader
    ```

2.  **Set up a Virtual Environment:**
    *   **Windows:**
        ```bash
        python -m venv venv
        .\venv\Scripts\activate
        ```
    *   **macOS / Linux:**
        ```bash
        python3 -m venv venv
        source venv/bin/activate
        ```

3.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Optional External Tools:**
    The script works without these, but they enable advanced features:
    *   **[ExifTool](https://exiftool.org/):** Required for embedding GPS metadata and correct timezone offsets.
        *   *Windows:* Place `exiftool.exe` in `tools/exiftool/`.
        *   *Mac:* `brew install exiftool`
        *   *Linux:* `sudo apt install libimage-exiftool-perl`
    *   **[FFmpeg](https://ffmpeg.org/download.html):** Required if you want to composite overlays onto **videos**.

---

## Usage

### 1. Prepare Your Data
1.  Request your data export from Snapchat Settings.
2.  Extract the ZIP file you received.
3.  Rename the extracted folder to `data from snapchat` (exactly).
4.  Place it inside the `snapchat-memory-downloader` folder.

**Folder Structure should look like this:**
```text
snapchat-memory-downloader/
├── snapchat-memories-downloader.exe  # (or .py script)
├── venv/                             # (if running from source)
└── data from snapchat/               # Your renamed export folder
    └── html/
        └── memories_history.html
```

### 2. Run the Tool
**Windows User:** Double-click the `.exe` or run in terminal.
**Python User:**
```bash
python download_snapchat_memories.py
```

### 3. Interactive Menu
Upon launching, you will see a menu. Use **Up/Down** arrows and **Enter** to select:
*   **Download Memories**: The main function. Parses HTML and downloads everything.
*   **Apply Overlays**: Re-combines your photos with their stickers/text.
*   **Convert Timezones**: Fixes UTC timestamps to be local time (requires GPS data).
*   **Verify**: Checks if all files were downloaded correctly.

---

## Advanced Features

### Overlay Compositing
Snapchat exports the original media and the "overlay" (text, stickers) as separate files. This tool can combine them back together.
*   **Images**: Uses `Pillow` (included in requirements).
*   **Videos**: Uses `FFmpeg` (must be installed separately).
*   **Command**: `python download_snapchat_memories.py --apply-overlays`

### GPS & Timezone Correction
Snapchat exports timestamps in UTC. This feature uses the GPS data in your memories to figure out the actual local time (e.g., converting 14:00 UTC to 10:00 EST if the photo was taken in New York).
*   **Command**: `python download_snapchat_memories.py --convert-timezone`
*   **Note**: Requires `timezonefinder` (included in requirements) and works best with `ExifTool` installed.

### Command Line Arguments
If you prefer automation over the menu:
```bash
# Custom input/output
python download_snapchat_memories.py --html "path/to/memories.html" --output "my_backup"

# Rate limit handling (increase delay)
python download_snapchat_memories.py --delay 5.0
```

---

## Troubleshooting

### "File is not a zip file" / HTTP 429 Errors
this means Snapchat is rate-limiting your downloads.
*   **Solution**: Restart the script and select a higher delay (e.g., 5 seconds) or use `--delay 5.0`. The script also has auto-backoff logic to handle this.

### Missing Dependencies
If you see errors about `requests` or `PIL`:
*   Ensure you activated your virtual environment (`source venv/bin/activate`).
*   Run `pip install -r requirements.txt` again.

---

## License
MIT License - provided as-is for personal backup use.
