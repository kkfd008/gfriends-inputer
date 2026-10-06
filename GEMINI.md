# Gfriends Inputer Instructions

## Project Overview
Gfriends Inputer is a media server (Emby/Jellyfin) actor avatar and metadata import tool. It integrates with the [Gfriends](https://github.com/gfriends/gfriends) repository and uses AI-powered face detection for optimal avatar cropping.

## Tech Stack
- **Language:** Python 3.6+
- **Core Libraries:** `requests` (API interaction), `PIL/Pillow` (Image processing), `opencv-python` (Face detection), `lxml` (Web scraping), `alive-progress` (UI).
- **AI Models:** OpenCV DNN (local) and Baidu AI (cloud).

## Architecture & Conventions
- **Main Entry:** `Gfriends Inputer.py`.
- **Logic Segregation:** 
  - AI and external model logic resides in the `Lib/` directory.
  - Runtime logs, caches, and temporary files are stored in `./Getter/`.
  - Downloaded avatars go to `./Downloads/` (configurable).
  - User-provided local avatars are in `./Avatar/` (configurable).
- **Configuration:** Managed via `config.ini` (INI format, uses `RawConfigParser`).
- **Coding Style:** 
  - Prefer functional programming patterns.
  - Extensive use of `logging` for debugging and `alive-bar` for user feedback.
  - Use `threading` for concurrent downloads and uploads.
  - Character encoding: Source files use UTF-8. Configuration files use UTF-8-SIG for Windows compatibility.
- **Error Handling:** Robust `try-except` blocks around network I/O and image processing are mandatory.

## Workflows
- **Building:** The project uses `PyInstaller` to generate standalone executables for Windows, Mac, and Linux. See `.github/workflows/main.yml` for build steps.
- **Dependencies:** Always update `requirements.txt` when adding new libraries.
- **Testing:** Verify changes against a local Emby/Jellyfin instance or mock APIs where possible.

## Subdirectory Instructions
- [Lib/GEMINI.md](./Lib/GEMINI.md): AI models and computer vision logic.
