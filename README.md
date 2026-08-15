# RUNEAutoCracker

A one-click Windows tool that automates Steam DRM removal using the RUNE Steam emulator — select a game folder, and it handles the rest.

https://cs.rin.ru/forum/viewtopic.php?f=20&t=159883

## Features

- 🖱️ Drag & drop the game folder (or browse for it)
- 🔍 Automatic game search: name or AppID → Steam Store lookup, with web-scrape and DuckDuckGo fallbacks
- 🎮 Three emulator profiles: **Regular**, **Steakclient**, **Steamclient**
- 🧹 SteamStub DRM removal via Steamless or a standalone patcher
- 📦 DLC auto-unlock: pulls the full DLC list straight from Steam
- 🧩 Steam interface auto-extraction from the original `steam_api(64).dll`
- 🗃️ Crack-Only mode: builds a standalone `Crack.Only.zip` without touching the game folder
- ⬆️ Emulator auto-updates with SHA-256 verification
- ⚙️ Configurable via Settings dialog — saved to `settings.ini`

## Screenshots

<a href="https://img.ptscreens.com/image675827968b9de920.png"><img src="https://img.ptscreens.com/image675827968b9de920.png" width="400"></a> <a href="https://img.ptscreens.com/imageaf370d8d368c41e1.png"><img src="https://img.ptscreens.com/imageaf370d8d368c41e1.png" width="400"></a>

## Requirements

- **OS:** Windows (64-bit)
- **Python:** 3.7+
- **Internet:** Required (connects to `store.steampowered.com` for game/DLC data)

### Python Dependencies

```
pip install customtkinter tkinterdnd2 requests pywin32 beautifulsoup4 ddgs steam
```

`beautifulsoup4` and `ddgs` are optional — they enable extra search fallbacks.

### Emulator Files

On first launch, the GUI downloads the required emulator components automatically:

| Directory | Component |
|---|---|
| `rune/emu` | Regular emulator files |
| `rune/steakclient` | Steakclient loader |
| `rune/steamclient` | Steamclient loader (x64 + x86) |
| `rune/Steam stub patcher` | SteamStub patcher DLLs |

Steamless CLI should be placed in a `steamless/` directory alongside the script.

## How to Use

1. Run `python rune_auto_cracker.py`.
2. Drag the game folder into the window (or press **Browse**).
3. Enter the game name or AppID and press **Search**.
4. Pick a crack profile — **Regular**, **Steakclient**, or **Steamclient**.
5. Press **Crack** — done.

## Settings

| Setting | Options | Default |
|---|---|---|
| SteamStub DRM Removal | Steamless / SteamStub patcher | Steamless |
| Backup Suffix | Any string (e.g. `.rne`, `.bak`) | `.rne` |
| Default Emu | Regular / Steakclient / Steamclient / Always ask | Always ask |
| Crack Mode | Full Crack / Crack Only / Full Crack + Crack Only | Full Crack |
| Check Updates on Startup | On / Off | On |

## How It Works

1. Recursively scans the game folder for `steam_api.dll` / `steam_api64.dll`
2. Strips SteamStub DRM via Steamless CLI or the standalone patcher
3. Backs up the original DLLs and deploys the emulator files, writing AppID, API version, and DLC list into the config
4. Extracts Steam interface strings from the original DLL and injects them into the emulator config
5. *(Optional)* Packages a `Crack.Only.zip` containing just the crack files

## Privacy

Network requests go only to `store.steampowered.com` (game/DLC data) and the configured GitHub release URL (emulator updates). Nothing is logged or sent anywhere else.

## License

BSD-3-Clause
