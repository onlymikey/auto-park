# South Park Downloader

Project to fetch the complete list of South Park episodes (seasons and episodes) with URLs in Spanish and English from [southpark.lat](https://www.southpark.lat), and automatically download episodes with audio in both languages using Selenium and FFmpeg.

---

## Overview

This project consists of two main scripts:

### 1. `south_scrapper.py`

- Retrieves the full list of South Park seasons and episodes in Spanish and English.
- Extracts unique MGID identifiers for each season.
- Queries the public API to list episodes per season with metadata.
- Generates a JSON file `all_southpark_episodes.json` containing episode info, including properly formatted URLs for both Spanish and English.

### 2. `auto_park.py`

- Reads the `all_southpark_episodes.json` file.
- Uses Selenium Wire with Firefox to load episode pages (both Spanish and English).
- Interacts with the player to start playback and select HD quality.
- Captures network requests to obtain `.m3u8` video and audio stream URLs.
- Downloads video and audio streams separately for Spanish and English using FFmpeg.
- Merges the streams into a single MKV file with multilingual audio.
- Saves episodes organized by season into a local folder.

---

## Requirements

- Python 3.8+
- [Firefox](https://www.mozilla.org/firefox/)
- [Geckodriver](https://github.com/mozilla/geckodriver/releases) (in your system PATH)
- Selenium and Selenium Wire:
  ```bash
  pip install selenium selenium-wire

* BeautifulSoup4:

  ```bash
  pip install beautifulsoup4
  ```
* FFmpeg (installed and accessible from command line)
* Internet connection for scraping and downloading
* A Firefox profile configured to avoid playback blocks (set the path in `profile_path` in `auto_park.py`)

---

## Usage

### 1. Generate the JSON file with episodes

Run:

```bash
python south_scrapper.py
```

This will create `all_southpark_episodes.json` with structure like:

```json
[
  {
    "temporada": 1,
    "numero": 1,
    "nombre": "Cartman consigue una sonda anal",
    "url_es": "https://www.southpark.lat/episodios/940f8z/south-park-cartman-consigue-una-sonda-anal-temporada-1-ep-1",
    "url_en": "https://www.southpark.lat/en/episodes/940f8z/south-park-cartman-consigue-una-sonda-anal-temporada-1-ep-1"
  },
  ...
]
```

---

### 2. Download episodes with Spanish and English audio

Run:

```bash
python auto_park.py
```

* Make sure to update `profile_path` to point to your local Firefox profile.
* Downloads will be saved inside the `descargas` folder, organized by season subfolders.
* The script finds `.m3u8` links for video and audio, downloads, and merges streams using FFmpeg.
* On errors, you can choose to retry or skip the episode.

---

## Technical details

* Uses Selenium Wire to intercept HTTP requests and find streaming URLs.
* FFmpeg downloads and merges streams without re-encoding to preserve original quality.
* English URLs are corrected to use `/en/episodes/` to ensure correct language content.
* `south_scrapper.py` handles pagination to get all episodes per season.
* `auto_park.py` selects 720p or 1080p quality if available.

---

## Warnings and notes

* Scraping and downloading depend on the current structure of `southpark.lat` and may break if the site changes.
* This project is for personal and educational use only. Always respect terms of service and copyright.
* Ensure sufficient disk space for full episode downloads.
* Firefox profile should allow video playback without captcha or blocking issues.
* Downloading the entire series may take a long time.

---

## Main files

* `south_scrapper.py`: Fetches seasons, episodes, and URLs in Spanish and English.
* `auto_park.py`: Automates download and merging of streams per episode.
* `all_southpark_episodes.json`: Generated file listing all episodes with URLs.

---

## Example `profile_path` setting in `auto_park.py`

```python
profile_path = r"C:\Users\mikey\AppData\Roaming\Mozilla\Firefox\Profiles\123456abcd.default-release"
```

Modify according to your OS and Firefox profile.

---

## License

This project is for personal and educational use only. Do not distribute or publish protected content without permission.

---

Enjoy downloading South Park with multilingual audio!

