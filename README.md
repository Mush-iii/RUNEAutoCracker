<div align="center">

<h1>RUNEAutoCracker</h1>

<strong>An automatic Steam DRM removal & crack tool using the RUNE steam emulator</strong>

<a href="https://github.com/Mush-iii/RUNEAutoCracker/releases"><img src="https://img.shields.io/github/v/release/Mush-iii/RUNEAutoCracker" alt="Release"></a>
<a href="https://github.com/Mush-iii/RUNEAutoCracker/releases"><img src="https://img.shields.io/github/downloads/Mush-iii/RUNEAutoCracker/total" alt="downloads"></a>

</div>


🔗 Forum thread: https://cs.rin.ru/forum/viewtopic.php?f=20&t=159883

## What it does

| | |
|---|---|
| 📂 **Folder detection** | Drag & drop a game folder, or browse for one |
| 🔎 **Smart search** | Type a name or AppID — resolves via Steam Store API, with BeautifulSoup / DuckDuckGo fallbacks |
| 🧬 **Three emu profiles** | Regular, Steakclient, or Steamclient — pick per crack |
| 🛡️ **DRM stripping** | Removes SteamStub via Steamless CLI, or a standalone patcher DLL |
| 🎁 **DLC unlock** | Pulls the game's full DLC list straight from Steam and writes it into the config |
| 🧩 **Interface extraction** | Reads Steam interface strings out of the original `steam_api(64).dll` automatically |
| 📦 **Crack-only export** | Optionally spits out a standalone `Crack.Only.zip`, no game files touched |
| 🔄 **Self-updating** | Emulator components auto-update from GitHub, verified via SHA-256 |

## Screenshots

<a href="https://img.ptscreens.com/image675827968b9de920.png"><img src="https://img.ptscreens.com/image675827968b9de920.png" width="400"></a> <a href="https://img.ptscreens.com/imageaf370d8d368c41e1.png"><img src="https://img.ptscreens.com/imageaf370d8d368c41e1.png" width="400"></a>

## Getting Started

**Requirements:** Windows x64, Python 3.7+, an internet connection (talks to `store.steampowered.com` for game/DLC lookups).

Install the dependencies:

```
pip install customtkinter tkinterdnd2 requests pywin32 beautifulsoup4 ddgs steam
```

> `beautifulsoup4` and `ddgs` are optional — they just add extra fallbacks when the Steam API search comes up short.

Then launch it:

```
python rune_auto_cracker.py
```

**Steamless CLI** needs to live in a `steamless/` folder next to the script for SteamStub removal to work.

## Walkthrough

1. Drop the game folder in, or hit **Browse**
2. Type the game name / AppID and hit **Search**
3. Choose a profile — Regular, Steakclient, or Steamclient
4. Hit **Crack**, you're done

First launch will auto-download the emulator components it needs into a local `rune/` folder — no manual setup required:

| Folder | What's inside |
|---|---|
| `rune/emu` | Regular emulator files |
| `rune/steakclient` | Steakclient loader |
| `rune/steamclient` | Steamclient loader (x86 + x64) |
| `rune/Steam stub patcher` | SteamStub patcher DLLs |

## Under the Hood

1. Scans the folder tree for `steam_api.dll` / `steam_api64.dll`
2. Strips SteamStub protection (Steamless or the standalone patcher)
3. Backs up the originals, drops in the emulator, and writes AppID / API version / DLC list into its config
4. Pulls interface version strings from the original DLL and feeds them into the emulator config
5. *(Optional)* Bundles everything into a portable `Crack.Only.zip`

## Settings (`settings.ini`)

| Setting | Options | Default |
|---|---|---|
| SteamStub DRM Removal | Steamless / SteamStub patcher | Steamless |
| Backup Suffix | any string, e.g. `.rne`, `.bak` | `.rne` |
| Default Emu | Regular / Steakclient / Steamclient / Always ask | Always ask |
| Crack Mode | Full Crack / Crack Only / Both | Full Crack |
| Check Updates on Startup | On / Off | On |

All of this is also editable from the in-app Settings dialog.

## Privacy

The only network calls made are to `store.steampowered.com` (game/DLC lookups) and the GitHub release used for emulator updates. Nothing else, no telemetry.

## License

BSD-3-Clause
