# Auto Park

Educational project demonstrating how to automate the collection of episode metadata from [southpark.lat](https://www.southpark.lat), work with video/audio streams, and validate multimedia files using **Python**, **Selenium**, **BeautifulSoup**, and **FFmpeg**.

⚠️ **Important notice**: This project is **not intended to promote the downloading of copyrighted content**. It is designed for **technical learning, experimentation, and personal study** in web scraping, automation, and multimedia stream handling.

---

## Overview

This project contains three main scripts:

1. **`south_scrapper.py`** – gathers episode metadata.
2. **`autopark.py`** – automates stream detection and audio/video merging.
3. **`tegridy_check.py`** – verifies video file integrity.

Below is a detailed description of each script.

---

## 1. `south_scrapper.py`

This script collects structured information for **all seasons and episodes** of South Park in both Spanish and English.

### Functionality:

* Accesses the page for each season on [southpark.lat](https://www.southpark.lat).
* Extracts internal identifiers (*MGID*) associated with each season.
* Queries the site's public API to retrieve the list of episodes and metadata (titles, episode numbers, URLs).
* Combines the data into a single JSON file `all_southpark_episodes.json` with the structure:

```json
[
  {
    "season": 1,
    "number": 1,
    "name": "Cartman gets an anal probe",
    "url_es": "https://www.southpark.lat/episodios/940f8z/...",
    "url_en": "https://www.southpark.lat/en/episodes/940f8z/..."
  },
  ...
]
```

### Technical details:

* Uses **requests** and **BeautifulSoup** for web scraping.
* Handles **pagination** of episodes and corrects URLs for English.
* Adds a manual example for season 1 due to special site structure.
* Combines Spanish and English season data by episode number.

---

## 2. `autopark.py`

Automates **stream detection** and **audio/video merging** using Selenium and FFmpeg.

### Functionality:

1. **Episode loading**

   * Opens Firefox using Selenium Wire.
   * Loads the episode page in Spanish and English.
   * Interacts with the player to start playback and select HD quality.

2. **`.m3u8` link capture**

   * Intercepts network requests to obtain video and audio URLs.
   * Filters the highest quality video stream (e.g., 1080p) and audio streams in Spanish and English.

3. **Download and merge streams**

   * Uses FFmpeg to download video and audio separately.
   * Merges them into a single `.mkv` file with multilingual audio tracks.
   * Organizes episodes into season folders.

4. **Error handling and validation**

   * Detects if the file already exists and if it meets the desired resolution (1080p).
   * Retries failed downloads up to 3 times with configurable delays.
   * Maintains a detailed log (`descargas.log`) with the status of each episode.

### Technical details:

* **Selenium Wire** intercepts HTTP requests to capture `.m3u8` streams.
* **FFmpeg** uses copy mode (`-c copy`) to avoid re-encoding and preserve original quality.
* `filter_streams` selects the best video stream by MTP (Media Time Point) and the first available audio stream.
* `sanitize_filename` ensures filenames are valid for the operating system.
* Supports 720p or 1080p quality selection if available.

---

## 3. `tegridy_check.py`

Verifies the **integrity of video files** in the project folder.

### Functionality:

* Walks through directories searching for video files (`.mp4`, `.mkv`, `.avi`, `.mov`).
* Analyzes each file using FFmpeg to detect possible corruption or incomplete files.
* Displays a final report listing potentially damaged files.

### Technical details:

* Uses a **timeout** to avoid long blocks when analyzing large files.
* Interprets FFmpeg stderr errors as possible corruption.
* Allows quick checks of the health of a multimedia file collection.

---

## Requirements

* **Python 3.8+**
* **Firefox** and **Geckodriver** in PATH
* Python libraries:

  ```bash
  pip install selenium selenium-wire beautifulsoup4 requests
  ```
* **FFmpeg** (installed and accessible from command line)
* Internet connection for scraping and stream access
* Valid Firefox profile configured for playback without blocking (set `profile_path`)

---

## Usage Examples

### 1. Generate JSON with episodes

```bash
python south_scrapper.py
```

→ Creates `all_southpark_episodes.json` with seasons, episodes, and URLs.

### 2. Automate stream download and merging

```bash
python autopark.py
```

* Configure `profile_path` with your Firefox profile.
* Episodes are organized in `downloads/Season XX/` folders.
* Logs are saved in `descargas.log`.

### 3. Verify video file integrity

```bash
python tegridy_check.py
```

* Lists files with potential corruption issues.

---

## Advanced Technical Details

* **Logs and retries**: `autopark.py` logs each step with timestamps and handles automatic retries.
* **Stream selection**: Video streams are filtered by MTP, and audio by language.
* **Resolution validation**: `es_1080p` uses FFprobe to check minimum required resolution.
* **Filename handling**: `sanitize_filename` replaces invalid characters to prevent filesystem errors.

---

## Warnings and Notes

* Site structure may change, potentially breaking the scripts.
* This project is **for educational and technical purposes only**.
* Do not distribute downloaded copyrighted content.
* Ensure sufficient disk space for large files.
* Downloading full seasons may take significant time depending on internet speed.
* Configure your Firefox profile to avoid captchas or playback blocks.

---

## Main Files

| File                          | Purpose                                                       |
| ----------------------------- | ------------------------------------------------------------- |
| `south_scrapper.py`           | Retrieves seasons, episodes, and URLs in Spanish and English. |
| `autopark.py`                 | Automates stream retrieval, download, and merging of tracks.  |
| `tegridy_check.py`            | Analyzes video files and detects corruption.                  |
| `all_southpark_episodes.json` | Generated JSON containing complete episode metadata.          |

---

## Example `profile_path` configuration in `autopark.py`

```python
profile_path = r"C:\Users\mikey\AppData\Roaming\Mozilla\Firefox\Profiles\123456abcd.default-release"
```

Adjust according to your operating system and Firefox profile.

---

## License

* For **personal and educational use only**.
* Do not redistribute copyrighted content obtained using these examples.

