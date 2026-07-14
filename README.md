# RUNEAutoCracker

A tool that automatically removes Steam DRM from games using RUNE steam emulators.
https://cs.rin.ru/forum/viewtopic.php?f=20&t=159883

---

## Features

- **Three types of RUNE steam emulators**
  - **Regular** — Replaces Steam API DLLs with the Rune emulator
  - **Steakclient** — Uses `steakclient64.dll` + `winmm.dll` loader (64-bit games only)
  - **Steamclient** — Automatically patches the SHELL32.dll import string in the original Steam API DLL and deploys steamclient loader files
- **SteamStub DRM Removal** — Strips SteamStub DRM via Steamless or a standalone SteamStub patcher (`winmm.dll`)
- **Automatic Steam Search** — Enter a game name or AppID; the tool queries the Steam Store API, falls back to web scraping (BeautifulSoup) and DuckDuckGo search
- **DLC Unlocking** — Fetches the full DLC list from Steam and writes it into the emulator config
- **Steam Interface Extraction** — Automatically generates interfaces from the original `steam_api.dll` / `steam_api64.dll` 
- **Crack-Only Mode** — Generates a standalone `Crack.Only.zip` without modifying the game folder
- **Emulator Auto-Updates** — Checks a GitHub release manifest for newer emulator components and downloads them with SHA-256 verification
- **Drag & Drop** — Drop a game folder onto the window to select it
- **Configurable** — Backup suffix, default profile, DRM method, crack output mode, and update behavior are all saved to `settings.ini`

## Requirements

- **OS:** Windows (64-bit)
- **Python:** 3.7+
- **Internet:** Required (connects to `store.steampowered.com` for game/DLC data)

### Python Dependencies

```
customtkinter
tkinterdnd2
requests
pywin32
steam
```

**Optional** (enable extra search fallbacks):

```
beautifulsoup4
ddgs
```

Install all dependencies:

```
pip install customtkinter tkinterdnd2 requests pywin32 beautifulsoup4 ddgs steam
```

### Emulator Files

On first launch, the GUI automatically downloads the required emulator components from the configured GitHub release. The following directories are populated under `rune/`:

| Directory | Component |
|---|---|
| `rune/emu` | Regular emulator files |
| `rune/steakclient` | Steakclient loader |
| `rune/steamclient` | Steamclient loader (x64 + x86) |
| `rune/Steam stub patcher` | SteamStub patcher DLLs |

Steamless CLI should be placed in a `steamless/` directory alongside the script.

## Usage

```
python rune_auto_cracker.py
```

1. **Select a game folder** — Click Browse or drag & drop a folder onto the window
2. **Search for the game** — Enter the game name or Steam AppID, then click Search
3. **Crack** — Choose a crack profile (Regular / Steakclient / Steamclient) and the tool handles the rest

## Settings

Settings are saved to `settings.ini` and can be changed from the GUI Settings dialog:

| Setting | Options | Default |
|---|---|---|
| SteamStub DRM Removal | Steamless / SteamStub patcher | Steamless |
| Backup Suffix | Any string (e.g. `.rne`, `.bak`) | `.rne` |
| Default Emu | Regular / Steakclient / Steamclient / Always ask | Always ask |
| Crack Mode | Full Crack / Crack Only / Full Crack + Crack Only | Full Crack |
| Check Updates on Startup | On / Off | On |

## How It Works

1. **Locate Steam API DLLs** — Recursively scans the game folder for `steam_api.dll` and `steam_api64.dll`
2. **Remove SteamStub DRM** — Runs Steamless CLI on every `.exe` to strip SteamStub protection (or deploys the SteamStub patcher DLL)
3. **Deploy emulator** — Backs up original DLLs (renamed with the configured suffix) and copies emulator files into the game directory, writing the AppID, API version, and DLC list into the emulator config
4. **Generate interfaces** — Extracts Steam interface version strings from the original DLL binary and injects them into the emulator config
5. **Package (optional)** — In Crack-Only or Both mode, builds a zip containing only the crack files

## Privacy

- Network requests are made only to `store.steampowered.com` (game/DLC data) and the configured GitHub release URL (emulator updates)
- Nothing is logged or sent to any third-party service

## License

BSD-3-Clause
