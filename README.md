# Soundbar Tone Player

A Windows system tray application that plays audio files (WAV/MP3) at regular intervals.

![Python](https://img.shields.io/badge/python-3.14+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Platform](https://img.shields.io/badge/platform-Windows-lightgrey.svg)

## Features

- 🎵 Play audio files (WAV/MP3) at configurable intervals
- 🖥️ Runs silently in Windows system tray
- ⚙️ Easy configuration via JSON file
- 🚀 Quick interval presets (3, 5, 10 minutes)
- 🔄 Optional startup with Windows
- 🎯 Manual play on demand
- 📦 Standalone executable - no Python installation required

## Quick Start

### Option 1: Download Pre-built Executable (Windows)

> ⚠️ **Note:** Some antivirus software may flag the executable as a false positive. See [Antivirus False Positives](#antivirus-false-positives) section below. If concerned, build from source instead.

1. Download `SoundbarTonePlayer.exe` from the [Releases](../../releases) page

2. Create a folder and copy these files together:
   - `SoundbarTonePlayer.exe`
   - `player_settings.json` (download from repo or let the app create it)
   - Your audio file (e.g., `tone.wav`)

3. Double-click `SoundbarTonePlayer.exe` to run

4. The app will appear in your system tray (look for the speaker icon near the clock)

5. Right-click the tray icon for controls

### Option 2: Run from Source (Recommended for Development)

```powershell
# Clone the repository
git clone https://github.com/grhawkeye/Soundbar_Tone_Player.git
cd soundbar-tone-player

# Install dependencies
pip install -r requirements.txt

# Run the application
python soundbar_tone_player.py

# Or test mode (plays once and exits)
python soundbar_tone_player.py --test
```

### Important: File Locations

**The .exe looks for files in the same folder as the executable!**

Example folder structure:
```
C:\SoundbarTonePlayer\
├── SoundbarTonePlayer.exe
├── player_settings.json
└── tone.wav
```

### Configuration

Edit `player_settings.json`:
```json
{
    "tone_file": "tone.wav",
    "interval_minutes": 10
}
```

- `tone_file`: Name of the audio file to play (must be in same folder as exe)
- `interval_minutes`: How often to play (in minutes)

### System Tray Menu

- **Start with Windows** - Toggle startup with Windows
- **Play Now** - Play the tone immediately
- **Interval** - Quick presets (3, 5, 10 minutes) or set custom
- **Exit** - Close the application

### Command Line Options

Run from Command Prompt or PowerShell:

```powershell
# Test play once (with console output)
SoundbarTonePlayer.exe --test

# Show help
SoundbarTonePlayer.exe --help
```

### Supported Audio Formats

- **WAV** - Full support (recommended)
- **MP3** - Basic support

---

## Development

To run from source code:

```powershell
# Install dependencies
pip install -r requirements.txt

# Run the application
python soundbar_tone_player.py

# Test mode
python soundbar_tone_player.py --test
```

### Building from Source

**Recommended if you have antivirus concerns - build it yourself!**

```powershell
# Clone the repository
git clone https://github.com/yourusername/soundbar-tone-player.git
cd soundbar-tone-player

# Create virtual environment (optional but recommended)
python -m venv .venv
.venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt

# Install PyInstaller
pip install pyinstaller

# Build the executable
pyinstaller --onefile --windowed --name "SoundbarTonePlayer" tone_player.py

# Find the exe in the dist folder
```

The built executable will be in `dist\SoundbarTonePlayer.exe`

## Project Structure

```
Soundbar_Tone_Player/
├── soundbar_tone_player.py          # Main application source code
├── player_settings.json    # Configuration file (auto-created)
├── requirements.txt        # Python dependencies
├── README.md              # This file
└── dist/                  # Built executable (after running PyInstaller)
    └── SoundbarTonePlayer.exe
```

## Dependencies

- `sounddevice` - Audio playback
- `soundfile` - Audio file loading (WAV/MP3)
- `pystray` - System tray icon
- `Pillow` - Icon image creation

See `requirements.txt` for exact versions.

## License

This project is open source and available under the MIT License.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Security

This application:
- Does NOT connect to the internet
- Does NOT collect any data
- Does NOT access files outside its folder
- Only accesses Windows Registry for the "Start with Windows" feature (optional)

All source code is available for review in this repository.

---

## Troubleshooting

### Audio file not found?
- Make sure the audio file is in the **same folder** as `SoundbarTonePlayer.exe`
- Check that the filename in `player_settings.json` matches exactly (including extension)

### Settings file not found?
- The app will create a default `player_settings.json` in the same folder as the exe
- Check that folder for the newly created file

### Can't see the system tray icon?
- Look in the hidden icons area (click the up arrow near the system tray)
- The icon looks like a small speaker with sound waves

### Antivirus False Positives

**⚠️ IMPORTANT: This application may trigger false positive detections by some antivirus software.**

[VirusTotal Scan Results](https://www.virustotal.com/gui/file/6d7f1a76dde813c978e68605d87fd0557b45b21572a22fcbe82fbbf0a528fc4f/behavior) typically show **~4-6 detections out of 70+ scanners**.

**Why this happens:**

1. **PyInstaller Packaging** - The executable is built using PyInstaller, which bundles Python and all dependencies into a single .exe file. This technique is also used by malware, causing heuristic-based antivirus tools to flag it as suspicious.

2. **No Code Signing Certificate** - This is an open-source project without a paid code signing certificate ($300+/year). Unsigned executables are often flagged by security software.

3. **System Tray & Registry Access** - The app legitimately accesses Windows registry (for startup settings) and runs in the background, which some scanners consider suspicious behavior.

**This is safe software:**

- ✅ **100% open source** - All source code is available in this repository for inspection
- ✅ **No network activity** - The app doesn't connect to the internet
- ✅ **No data collection** - Zero telemetry or tracking
- ✅ **Simple functionality** - Just plays audio files at intervals

**Verification:**

1. Review the source code in `soundbar_tone_player.py` - it only plays audio files
2. Build the executable yourself from source (see instructions below)
3. The detections are from generic heuristics, not actual malware signatures
4. Major antivirus vendors (Windows Defender, Kaspersky, Bitdefender, etc.) typically show clean results

If you're concerned, **build the executable yourself from the source code** rather than using a pre-built binary.
