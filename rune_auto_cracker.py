import traceback

try:
    import customtkinter as ctk
    from tkinter import filedialog
    from tkinterdnd2 import DND_FILES, TkinterDnD

    import requests
    import configparser
    import json
    import os
    import subprocess
    import threading
    import queue
    from time import sleep
    import re
    import urllib.parse
    from pathlib import Path
    from typing import List, Set, Dict, Tuple, Optional
    import shutil
    import tkinter as tk
    import hashlib
    import zipfile
    import tempfile
    import concurrent.futures

    from steam.client import SteamClient
    from steam.enums.common import EResult

    import win32api
    def GetFileVersion(filename: str) -> str:
        fileInfos = win32api.GetFileVersionInfo(filename, "\\")
        return "%d.%d.%d.%d" % (
            fileInfos['FileVersionMS'] / 65536,
            fileInfos['FileVersionMS'] % 65536,
            fileInfos['FileVersionLS'] / 65536,
            fileInfos['FileVersionLS'] % 65536,
        )

    try:
        from bs4 import BeautifulSoup
        BS4_AVAILABLE = True
    except ImportError:
        BS4_AVAILABLE = False

    try:
        from ddgs import DDGS
        DDGS_AVAILABLE = True
    except ImportError:
        try:
            from duckduckgo_search import DDGS
            DDGS_AVAILABLE = True
        except ImportError:
            DDGS_AVAILABLE = False

    VERSION = "1.2.1"

    RETRY_DELAY = 15
    RETRY_MAX = 30
    BYPASS_GAME_VERIFICATION = "0"
    CRACK_OPTION = "0"

    HIGH_DLC_WARNING = 125
    USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

    CONFIG_FILENAME = "settings.ini"

    # ─── EMULATOR UPDATES ────────────────────────────────────────────────────────
    EMU_MANIFEST_URL = "https://github.com/Mush-iii/rune-emu/releases/latest/download/manifest.json"

    # ─── SELF (APP) UPDATE ───────────────────────────────────────────────────────
    SELF_UPDATE_VERSION_URL = "https://raw.githubusercontent.com/Mush-iii/RUNEAutoCracker/Updater/latestversion.json"
    SELF_UPDATE_EXE_URL = "https://raw.githubusercontent.com/Mush-iii/RUNEAutoCracker/Updater/Updater.exe"

    COMPONENT_DIRS = {
        "rune_emu":    os.path.join("rune", "emu"),
        "steakclient": os.path.join("rune", "steakclient"),
        "steamclient": os.path.join("rune", "steamclient"),
        "steamstub":   os.path.join("rune", "Steam stub patcher"),
    }

    COMPONENT_LABELS = {
        "rune_emu":    "Regular Emu",
        "steakclient": "Steakclient",
        "steamclient": "Steamclient",
        "steamstub":   "SteamStub Patcher",
    }

    def _parse_version(v):
        parts = []
        for p in re.split(r'[.\-]', str(v)):
            try:
                parts.append(int(p))
            except ValueError:
                parts.append(0)
        return tuple(parts)

    import sys

    def resource_path(relative_path):
        base_path = getattr(sys, "_MEIPASS", os.path.abspath("."))
        return os.path.join(base_path, relative_path)

    folder_path = ""
    appID = 0
    gameSearchDone = False
    gameName = ""
    dlcIDs = []
    dlcNames = []

    # ─── THEME ───────────────────────────────────────────────────────────────────
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")

    BG          = "#0a0e16"
    SURFACE     = "#10151f"
    CARD        = "#131a26"
    CARD2       = "#161d2b"
    BORDER      = "#22304a"
    BORDER2     = "#1c2740"
    ACCENT      = "#3b82f6"
    ACCENT_HOVER= "#2563eb"
    ACCENT2     = "#8b5cf6"
    ACCENT2_HOVER = "#7c3aed"
    SUCCESS     = "#10b981"
    WARN        = "#f59e0b"
    DANGER      = "#ef4444"
    TEXT        = "#f1f5f9"
    TEXT2       = "#94a3b8"
    DIM         = "#334155"
    ENTRY_BG    = "#0c1119"
    MUTED       = "#64748b"

    # ─── STEAM INTERFACE EXTRACTOR ───────────────────────────────────────────────
    class SteamInterfaceExtractor:
        def __init__(self, pl3_path: str):
            self.pl3_path = pl3_path

        def extract_strings_from_pl3(self) -> List[str]:
            strings = []
            try:
                with open(self.pl3_path, 'rb') as f:
                    data = f.read()
                current_string = b""
                for byte in data:
                    if byte == 0:
                        if len(current_string) > 3:
                            try:
                                decoded = current_string.decode('ascii', errors='ignore')
                                if decoded.isprintable() and decoded.strip():
                                    strings.append(decoded.strip())
                            except: pass
                        current_string = b""
                    elif 32 <= byte <= 126:
                        current_string += bytes([byte])
                    else:
                        if len(current_string) > 3:
                            try:
                                decoded = current_string.decode('ascii', errors='ignore')
                                if decoded.isprintable() and decoded.strip():
                                    strings.append(decoded.strip())
                            except: pass
                        current_string = b""
                if len(current_string) > 3:
                    try:
                        decoded = current_string.decode('ascii', errors='ignore')
                        if decoded.isprintable() and decoded.strip():
                            strings.append(decoded.strip())
                    except: pass
            except Exception:
                try:
                    with open(self.pl3_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                        for line in content.split('\n'):
                            if line.strip():
                                strings.append(line.strip())
                except: pass
            return strings

        def find_steam_interfaces(self, strings: List[str]) -> Set[str]:
            interfaces = set()
            patterns = [
                r'Steam[A-Za-z]+\d{3}', r'ISteam[A-Za-z]+\d{3}',
                r'STEAM[A-Z]+_INTERFACE_VERSION\d{3}', r'STEAM[A-Z]+_INTERFACE_V\d{3}',
                r'STEAM[A-Z_]+\d{3}',
            ]
            for string in strings:
                if len(string) > 200: continue
                for pattern in patterns:
                    for match in re.findall(pattern, string):
                        if self.is_steam_interface(match):
                            interfaces.add(match)
                for part in re.split(r'[^\w]', string):
                    if 8 <= len(part) <= 50:
                        for pattern in patterns:
                            if re.fullmatch(pattern, part) and self.is_steam_interface(part):
                                interfaces.add(part)
            return interfaces

        def is_steam_interface(self, name: str) -> bool:
            return ('Steam' in name or 'STEAM' in name) and name[-1].isdigit() and 8 <= len(name) <= 50 and not name.endswith(('.dll', '.exe'))

        def normalize_name(self, full_interface: str) -> str:
            if full_interface.startswith('STEAM') and '_INTERFACE_' in full_interface:
                base = full_interface.split('_INTERFACE_')[0][5:]
                mappings = {
                    'GAMESERVER': 'SteamGameServer', 'GAMESERVERSTATS': 'SteamGameServerStats',
                    'HTMLSURFACE': 'SteamHTMLSurface', 'MUSICREMOTE': 'SteamMusicRemote',
                    'MATCHMAKING': 'SteamMatchMaking', 'MATCHMAKINGSERVERS': 'SteamMatchMakingServers',
                    'MATCHGAMESEARCH': 'SteamMatchGameSearch', 'PARENTALSETTINGS': 'SteamParentalSettings',
                    'REMOTEPLAY': 'SteamRemotePlay', 'REMOTESTORAGE': 'SteamRemoteStorage',
                    'USERSTATS': 'SteamUserStats', 'HTTP': 'SteamHTTP', 'UGC': 'SteamUGC',
                    'UNIFIEDMESSAGES': 'SteamUnifiedMessages',
                }
                return mappings.get(base, 'Steam' + base.capitalize())
            elif full_interface.startswith('Steam'):
                result = full_interface
                while result and result[-1].isdigit(): result = result[:-1]
                return result
            elif full_interface.startswith('ISteam'):
                result = full_interface[1:]
                while result and result[-1].isdigit(): result = result[:-1]
                return result
            return full_interface

        def extract_interfaces(self) -> Dict[str, str]:
            strings = self.extract_strings_from_pl3()
            interfaces = self.find_steam_interfaces(strings)
            mapping = {}
            for full_interface in interfaces:
                simple_name = self.normalize_name(full_interface)
                if simple_name:
                    mapping[simple_name] = full_interface
            return mapping

    def generate_steam_interfaces(dll_locations, ini_filename="steam_emu.ini", source_files=None):
        total_generated = 0
        for dll_location in dll_locations:
            if source_files and dll_location in source_files:
                candidate_paths = [source_files[dll_location]]
            else:
                candidate_paths = [
                    os.path.join(dll_location, "steam_api64.rne"),
                    os.path.join(dll_location, "steam_api.rne"),
                ]
            for src_path in candidate_paths:
                if not os.path.exists(src_path):
                    continue
                try:
                    extractor = SteamInterfaceExtractor(src_path)
                    interface_mapping = extractor.extract_interfaces()
                    if interface_mapping:
                        config_files = []
                        for root_dir, dirs, files in os.walk(dll_location):
                            for file in files:
                                if file.lower() == ini_filename.lower():
                                    config_files.append(os.path.join(root_dir, file))
                        files_modified = 0
                        for config_file in config_files:
                            try:
                                with open(config_file, 'r', encoding='utf-8', errors='ignore') as f:
                                    content = f.read()
                                if 'RUNE_Interfaces' in content:
                                    interface_lines = [f"{k}={v}" for k, v in sorted(interface_mapping.items())]
                                    new_content = content.replace('RUNE_Interfaces', '\n'.join(interface_lines))
                                    with open(config_file, 'w', encoding='utf-8') as f:
                                        f.write(new_content)
                                    files_modified += 1
                            except Exception:
                                pass
                        if files_modified > 0:
                            total_generated += len(interface_mapping)
                except Exception:
                    pass
                break
        return total_generated

    # ─── NETWORK ─────────────────────────────────────────────────────────────────
    class RuneRequest:
        def __init__(self, url: str, name: str = "Unnamed"):
            self.url = url
            self.tries = 0
            self.name = name
            self.DoRequest()

        def DoRequest(self):
            self.tries += 1
            req = requests.get(self.url, timeout=10, headers={"User-Agent": USER_AGENT})
            if not req.ok:
                if self.tries < RETRY_MAX:
                    update_logs(f"  ⟳ {self.name} failed, retrying in {RETRY_DELAY}s... ({self.tries}/{RETRY_MAX})")
                    sleep(RETRY_DELAY)
                    self.DoRequest()
                else:
                    update_logs(f"[!] Connection failed after {RETRY_MAX} tries.")
                    raise Exception(f"RuneRequest: failed after {RETRY_MAX} tries")
            else:
                self.req = req

    # ─── STEAM SEARCH ────────────────────────────────────────────────────────────
    def search_steam_appid(query: str) -> Optional[str]:
        try:
            url = f"https://store.steampowered.com/api/storesearch/?term={urllib.parse.quote(query)}&l=en&cc=US"
            resp = requests.get(url, timeout=15, headers={"User-Agent": USER_AGENT})
            if resp.status_code == 200:
                items = resp.json().get("items", [])
                if items:
                    return str(items[0]["id"])
        except Exception:
            pass

        if BS4_AVAILABLE:
            try:
                url2 = f"https://store.steampowered.com/search/suggest?term={urllib.parse.quote(query)}&f=games&cc=US&l=en"
                resp2 = requests.get(url2, timeout=10, headers={"User-Agent": USER_AGENT})
                soup = BeautifulSoup(resp2.text, "html.parser")
                first = soup.select_one("a[href*='/app/']")
                if first:
                    m = re.search(r"/app/(\d+)/", first.get("href", ""))
                    if m:
                        return m.group(1)
            except Exception:
                pass

        def _extract_appid_from_url(url: str) -> Optional[str]:
            for pattern in [
                r'store\.steampowered\.com/app/(\d+)',
                r'steamcommunity\.com/app/(\d+)',
                r'/?app/(\d+)[/?#]',
            ]:
                match = re.search(pattern, url, re.IGNORECASE)
                if match:
                    return match.group(1)
            return None

        if DDGS_AVAILABLE:
            for q in [f"{query} site:store.steampowered.com", f'"{query}" steam store']:
                try:
                    with DDGS() as ddgs:
                        results = ddgs.text(q, max_results=10)
                    if not results:
                        continue
                    for r in results:
                        href = r.get("href", "")
                        appid = _extract_appid_from_url(href)
                        if appid:
                            return appid
                except Exception:
                    continue
        return None

    # ─── CONFIG ──────────────────────────────────────────────────────────────────
    def UpdateConfig():
        with open(CONFIG_FILENAME, "w", encoding="utf-8") as f:
            config.write(f)

    def UpdateConfigKey(key, value):
        config["Settings"][key] = value
        UpdateConfig()

    def ResetConfig(customConfig=None):
        c = customConfig if customConfig else config
        c["Settings"] = {
            "DRMMethod": "steamless",
            "GameEXE": ".rne",
            "last_selected_folder": "",
            "DefaultMode": "ask",
            "CheckUpdatesOnStartup": "1",
            "CrackOption": "crack",
        }
        if not customConfig:
            UpdateConfig()

    def FillConfig(currentConfig, configDefault):
        changed = False
        for k, v in configDefault.items():
            if k not in currentConfig:
                currentConfig[k] = v
                changed = True
            if type(v) == configparser.SectionProxy:
                if FillConfig(currentConfig[k], v):
                    changed = True
        return changed

    def ReloadConfig():
        global config
        config = configparser.ConfigParser()
        if config.read(CONFIG_FILENAME) == [] or "Settings" not in config:
            ResetConfig()
        else:
            configDefault = configparser.ConfigParser()
            ResetConfig(configDefault)
            if FillConfig(config, configDefault):
                UpdateConfig()

        changed = False
        if "EmuVersions" not in config:
            config["EmuVersions"] = {}
            changed = True
        for name in COMPONENT_DIRS:
            if name not in config["EmuVersions"]:
                config["EmuVersions"][name] = "0"
                changed = True
        if changed:
            UpdateConfig()

    ReloadConfig()

    # ─── UI HELPERS ──────────────────────────────────────────────────────────────
    def _lighten(hex_color, amt=20):
        try:
            h = hex_color.lstrip('#')
            r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
            r = min(255, r + amt); g = min(255, g + amt); b = min(255, b + amt)
            return f"#{r:02x}{g:02x}{b:02x}"
        except Exception:
            return hex_color

    def _dim(hex_color, amt=45):
        try:
            h = hex_color.lstrip('#')
            r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
            r = max(0, r - amt); g = max(0, g - amt); b = max(0, b - amt)
            return f"#{r:02x}{g:02x}{b:02x}"
        except Exception:
            return hex_color

    # ─── MAIN APP CLASS (TkinterDnD root + CustomTkinter widgets) ────────────────
    class RuneApp(TkinterDnD.Tk):
        def __init__(self):
            super().__init__()

            self.title(f"RUNEAutoCracker  v{VERSION}")
            self.geometry("640x520")
            self.minsize(560, 460)
            self.configure(bg="#242424")

            try:
                self.iconbitmap(resource_path("steam.ico"))
            except Exception:
                pass

            self.drop_target_register(DND_FILES)
            self.dnd_bind("<<Drop>>", self._on_drop)

            self._step1_done = False
            self._step2_done = False

            self._build_ui()

            self.after(300, self._startup_emu_check)
            self.after(500, self._check_self_update)

        def _missing_component_dirs(self):
            missing = []
            for name, rel in COMPONENT_DIRS.items():
                full = os.path.join(os.getcwd(), rel)
                if not os.path.isdir(full) or not os.listdir(full):
                    missing.append(name)
            return missing

        def _startup_emu_check(self):
            missing = self._missing_component_dirs()
            check_updates = config["Settings"].get("CheckUpdatesOnStartup", "1") == "1"

            if not missing and not check_updates:
                return

            def _on_done(outdated, error):
                if error:
                    if missing:
                        self.log(f"\n[!] Could not fetch required emulator files: {error}")
                    return
                if not outdated:
                    return

                to_install = [item for item in outdated if item[0] in missing] if missing else []
                to_install_extra = [item for item in outdated if item[0] not in missing] if check_updates else []

                if to_install:
                    self.log("\n[INIT] Downloading required emulator files (first launch)...")

                    def _run():
                        for name, info, _lv in to_install:
                            self.apply_emu_update(name, info, lambda m: self.after(0, self.log, m))
                        self.after(0, lambda: self.log("[DONE] Emulator files ready."))
                        if to_install_extra:
                            self.after(0, lambda: EmuUpdateDialog(self, to_install_extra))

                    threading.Thread(target=_run, daemon=True).start()
                elif to_install_extra:
                    EmuUpdateDialog(self, to_install_extra)

            self.check_emu_updates(_on_done)

        # ── Self (app) update ────────────────────────────────────────────────
        def _check_self_update(self):
            def _run():
                try:
                    r = requests.get(SELF_UPDATE_VERSION_URL, timeout=10, headers={"User-Agent": USER_AGENT})
                    if not r.ok:
                        return
                    remote_version = r.json().get("version", "").strip()
                    if not remote_version:
                        return
                except Exception:
                    return

                if _parse_version(remote_version) <= _parse_version(VERSION):
                    return

                self.after(0, lambda: self.log(f"\n[UPDATE] New version found: {remote_version}"))

                updater_path = os.path.join(os.getcwd(), "Updater.exe")
                try:
                    self.after(0, lambda: self.log("[UPDATE] Downloading updater..."))
                    r2 = requests.get(SELF_UPDATE_EXE_URL, timeout=60, headers={"User-Agent": USER_AGENT})
                    if not r2.ok:
                        self.after(0, lambda: self.log("[UPDATE] Download failed."))
                        return
                    with open(updater_path, "wb") as f:
                        f.write(r2.content)
                    self.after(0, lambda: self.log("[UPDATE] Downloaded. Launching updater..."))
                except Exception:
                    self.after(0, lambda: self.log("[UPDATE] Download failed."))
                    return

                try:
                    subprocess.Popen([updater_path], cwd=os.getcwd())
                except Exception:
                    self.after(0, lambda: self.log("[UPDATE] Failed to launch updater."))
                    return

                self.after(500, lambda: os._exit(0))

            threading.Thread(target=_run, daemon=True).start()

        def _on_drop(self, event):
            path = event.data.strip("{}").replace("\\", "/")
            if os.path.isdir(path):
                self._select_folder(path)

        # ── Build ─────────────────────────────────────────────────────────────
        def _build_ui(self):
            self.grid_columnconfigure(0, weight=1)
            self.grid_rowconfigure(4, weight=1)

            title_label = ctk.CTkLabel(
                self, text="RUNEAutoCracker",
                font=ctk.CTkFont(size=20, weight="bold")
            )
            title_label.grid(row=0, column=0, pady=(20, 15))

            step1 = ctk.CTkFrame(self, fg_color="transparent")
            step1.grid(row=2, column=0, padx=20, pady=5, sticky="ew")
            step1.grid_columnconfigure(0, weight=1)

            self._folder_entry = ctk.CTkEntry(step1, placeholder_text="No folder selected...")
            self._folder_entry.grid(row=0, column=0, sticky="ew")
            self._folder_entry.configure(state="readonly")

            self._browse_btn = ctk.CTkButton(step1, text="Browse", width=100,
                                              command=lambda: self._select_folder())
            self._browse_btn.grid(row=0, column=1, padx=(10, 0))

            step2 = ctk.CTkFrame(self, fg_color="transparent")
            step2.grid(row=3, column=0, padx=20, pady=5, sticky="ew")
            step2.grid_columnconfigure(0, weight=1)

            self._game_entry = ctk.CTkEntry(step2, placeholder_text="Game name or AppID...")
            self._game_entry.grid(row=0, column=0, sticky="ew")
            self._game_entry.bind("<Return>", lambda e: self._search_game())

            self._search_btn = ctk.CTkButton(step2, text="Search", width=100,
                                              command=self._search_game)
            self._search_btn.grid(row=0, column=1, padx=(10, 0))

            log_frame = ctk.CTkFrame(self, corner_radius=12)
            log_frame.grid(row=4, column=0, padx=20, pady=(10, 5), sticky="nsew")
            log_frame.grid_columnconfigure(0, weight=1)
            log_frame.grid_rowconfigure(0, weight=1)

            self._log_box = ctk.CTkTextbox(log_frame, font=("Consolas", 11), wrap='word')
            self._log_box.grid(row=0, column=0, sticky="nsew", padx=8, pady=8)
            self._log_text = self._log_box._textbox
            self._log_text.config(state=tk.DISABLED)

            self._log_text.tag_config("ok",   foreground="#3fb950")
            self._log_text.tag_config("warn", foreground="#d29922")
            self._log_text.tag_config("err",  foreground="#f85149")
            self._log_text.tag_config("info", foreground="#79c0ff")
            self._log_text.tag_config("dim",  foreground="gray50")
            self._log_text.tag_config("head", foreground="#c084fc")

            bottom = ctk.CTkFrame(self, fg_color="transparent")
            bottom.grid(row=5, column=0, padx=20, pady=(0, 15), sticky="ew")
            bottom.grid_columnconfigure(0, weight=1)

            self._settings_btn = ctk.CTkButton(bottom, text="Settings", width=100,
                                                fg_color="gray40", hover_color="gray30",
                                                command=self._open_settings)
            self._settings_btn.grid(row=0, column=0, sticky="w")

            self._crack_btn = ctk.CTkButton(bottom, text="Crack", width=100,
                                             command=self._crack_game, state=tk.DISABLED)
            self._crack_btn.grid(row=0, column=1, sticky="e")

        # ── State helpers ─────────────────────────────────────────────────────
        def _set_step_active(self, card_dict=None, active=True, done=False):
            pass

        def _update_crack_button(self):
            if self._step1_done and self._step2_done:
                self._crack_btn.configure(state=tk.NORMAL)
            else:
                self._crack_btn.configure(state=tk.DISABLED)

        def set_status(self, text, color=None):
            pass

        # ── Logging ───────────────────────────────────────────────────────────
        def _clear_logs(self):
            self._log_text.config(state=tk.NORMAL)
            self._log_text.delete("1.0", tk.END)
            self._log_text.config(state=tk.DISABLED)

        _KEYWORD_TAGS = [
            (r"\[INIT\]", "head"),
            (r"\[CRACK\]", "head"),
            (r"\[UPDATE\]", "head"),
            (r"\[DONE\]", "ok"),
            (r"\[FAIL\]", "err"),
            (r"\bOK\b", "ok"),
            (r"\bFAILED\b", "err"),
            (r"Steam lookup:", "info"),
            (r"Patched:", "ok"),
            (r"Added\s*:", "ok"),
            (r"Backup:", "info"),
        ]
        _KEYWORD_RE = re.compile("|".join(f"({p})" for p, _ in _KEYWORD_TAGS))

        def log(self, msg):
            self._log_text.config(state=tk.NORMAL)

            last_end = 0
            for m in self._KEYWORD_RE.finditer(msg):
                if m.start() > last_end:
                    self._log_text.insert(tk.END, msg[last_end:m.start()])
                tag = next(t for i, (_, t) in enumerate(self._KEYWORD_TAGS) if m.group(i + 1))
                self._log_text.insert(tk.END, m.group(0), tag)
                last_end = m.end()
            if last_end < len(msg):
                self._log_text.insert(tk.END, msg[last_end:])
            self._log_text.insert(tk.END, "\n")

            self._log_text.see(tk.END)
            self._log_text.config(state=tk.DISABLED)
            self.update()

        # ── Structured log helpers (tree-style crack output) ─────────────────
        def log_init(self, identifier, path):
            self._log_text.config(state=tk.NORMAL)
            self._log_text.insert(tk.END, "[INIT]", "head")
            self._log_text.insert(tk.END, f" {identifier} @ {path}\n")
            self._log_text.insert(tk.END, "  └─ ")
            self._log_text.insert(tk.END, "Steam lookup:", "info")
            self._log_text.insert(tk.END, " Searching...")
            self._log_text.see(tk.END)
            self._log_text.config(state=tk.DISABLED)
            self.update()

        def log_lookup(self, ok, detail=""):
            self._log_text.config(state=tk.NORMAL)
            if ok:
                self._log_text.insert(tk.END, "OK", "ok")
                self._log_text.insert(tk.END, f"  ({detail})\n")
            else:
                self._log_text.insert(tk.END, "Failed.", "err")
                self._log_text.insert(tk.END, f" {detail}\n")
            self._log_text.see(tk.END)
            self._log_text.config(state=tk.DISABLED)
            self.update()

        def log_section(self, title):
            self.log(f"[CRACK] {title}")

        def log_step(self, num, total, label, ok=True, last=False, width=42):
            connector = "└─" if last else "├─"
            dots = "." * max(3, width - len(label))
            status = "OK" if ok else "FAILED"
            self.log(f"  {connector} [{num}/{total}] {label} {dots} {status}")

        def log_sub(self, text, last=False):
            connector = "└─" if last else "├─"
            self.log(f"  │    {connector} {text}")

        def log_done(self, ok=True, msg=None):
            if ok:
                self.log(f"[DONE] {msg or 'Crack applied successfully.'}")
            else:
                self.log(f"[FAIL] {msg or 'Crack failed.'}")

        # ── Game actions ──────────────────────────────────────────────────────
        def _select_folder(self, path=None):
            global folder_path
            if path is None:
                last = config["Settings"].get("last_selected_folder", "")
                initial = last if last and os.path.isdir(last) else "/"
                path = filedialog.askdirectory(initialdir=initial)

            if not path or not os.path.isdir(path):
                return

            folder_path = path
            config["Settings"]["last_selected_folder"] = os.path.dirname(folder_path)
            UpdateConfig()

            folder_name = os.path.basename(folder_path)

            self._folder_entry.configure(state="normal")
            self._folder_entry.delete(0, tk.END)
            self._folder_entry.insert(0, folder_path)
            self._folder_entry.configure(state="readonly")

            self._set_step_active(None, done=True)
            self._set_step_active(None, active=True)

            self._game_entry.delete(0, tk.END)
            self._game_entry.insert(0, folder_name)

            self._step1_done = True

            if self._step2_done:
                self._set_step_active(None, active=True)

            self._update_crack_button()

        def _search_game(self):
            global appID, gameSearchDone
            gameSearchDone = False

            self._search_btn.configure(state=tk.DISABLED)
            self._step2_done = False
            self._update_crack_button()

            query = self._game_entry.get().strip()
            if not query:
                self.log("\n[!] Please enter a game name or AppID")
                self._search_btn.configure(state=tk.NORMAL)
                return

            def _do():
                global appID
                appID = 0
                is_name_query = True
                self.log_init(query, folder_path)
                try:
                    appID = int(query)
                    is_name_query = False
                except ValueError:
                    found = search_steam_appid(query)
                    if found:
                        appID = int(found)
                    else:
                        self.log_lookup(False, "Could not find game. Try entering the AppID directly.")
                        self._search_btn.configure(state=tk.NORMAL)
                        return

                if appID != 0 and self._retrieve_game(query, is_name_query):
                    global gameSearchDone
                    gameSearchDone = True
                    self._step2_done = True
                    self._set_step_active(None, done=True)
                    if self._step1_done:
                        self._set_step_active(None, active=True)

                self._search_btn.configure(state=tk.NORMAL)
                self._update_crack_button()

            threading.Thread(target=_do, daemon=True).start()

        def _get_pics_dlc_info(self, appID) -> tuple:
            result = {}
            try:
                client = SteamClient()
                login_result = client.anonymous_login()
                if login_result != EResult.OK:
                    return False, {}

                raw = client.get_product_info(apps=[appID])
                game_info = raw["apps"][appID]

                dlc_ids = set()
                try:
                    raw_list = game_info["extended"]["listofdlc"]
                    dlc_ids |= set(int(x.strip()) for x in raw_list.split(",") if x.strip())
                except Exception:
                    pass

                if "depots" in game_info:
                    for dep, depot_info in game_info["depots"].items():
                        if isinstance(depot_info, dict) and "dlcappid" in depot_info:
                            try:
                                dlc_ids.add(int(depot_info["dlcappid"]))
                            except Exception:
                                pass

                if dlc_ids:
                    dlc_raw = client.get_product_info(apps=dlc_ids)["apps"]
                    for dlc_id in dlc_ids:
                        dlc_name = ""
                        try:
                            dlc_name = f'{dlc_raw[dlc_id]["common"]["name"]}'.strip()
                        except Exception:
                            try:
                                dlc_name = f'{dlc_raw[str(dlc_id)]["common"]["name"]}'.strip()
                            except Exception:
                                pass
                        if dlc_name:
                            result[dlc_id] = dlc_name

                client.disconnect()
                return True, result
            except Exception:
                return False, {}

        def _fetch_dlc_name(self, dlcID) -> Optional[str]:
            try:
                req = RuneRequest(
                    f"https://store.steampowered.com/api/appdetails?appids={dlcID}&filters=basic",
                    "RetrieveAppName").req
                d = req.json()[str(dlcID)]
                if "data" in d and "name" in d["data"]:
                    return d["data"]["name"]
            except Exception:
                pass
            return None

        def _fetch_primary_dlc_ids(self, appID) -> tuple:
            ids = []
            try:
                req2 = RuneRequest(
                    f"https://store.steampowered.com/dlc/{appID}/random/ajaxgetfilteredrecommendations/?query&count=10000",
                    "RetrieveDLC").req
                data2 = req2.json()
                if not data2.get("success"):
                    return False, []
                total = data2["total_count"]
                resultsIndex = 0
                for _ in range(total):
                    resultsIndex = data2["results_html"].find("data-ds-appid=\"", resultsIndex)
                    if resultsIndex == -1:
                        break
                    resultsIndex += len("data-ds-appid=\"")
                    resultsStr = ""
                    while data2["results_html"][resultsIndex] != "\"":
                        resultsStr += data2["results_html"][resultsIndex]
                        resultsIndex += 1
                    dlcID = int(resultsStr)
                    if dlcID not in ids:
                        ids.append(dlcID)
                return True, ids
            except Exception:
                return False, []

        def _fetch_appdetails_dlc_ids(self, appID) -> tuple:
            try:
                req4 = RuneRequest(
                    f"https://store.steampowered.com/api/appdetails?appids={appID}",
                    "RetrieveDLCList").req
                data4 = req4.json()[str(appID)]
                if data4.get("success") and "data" in data4:
                    return True, data4["data"].get("dlc", [])
                return False, []
            except Exception:
                return False, []

        def _retrieve_game(self, query, is_name_query) -> bool:
            global appID, gameName, dlcIDs, dlcNames
            dlcIDs = []
            dlcNames = []

            try:
                req = RuneRequest(f"https://store.steampowered.com/api/appdetails?appids={appID}&filters=basic",
                                 "RetrieveGame").req
            except Exception:
                self.log_lookup(False, "connection error")
                return False

            data = req.json()[str(appID)]
            if not data["success"]:
                self.log_lookup(False, "AppID not found")
                appID = 0
                return False

            if BYPASS_GAME_VERIFICATION != "1" and data["data"]["type"] != "game":
                self.log_lookup(False, "not a game")
                appID = 0
                return False

            gameName = data["data"]["name"]
            appID = data["data"]["steam_appid"]

            # ── Fetch all three DLC ID sources in parallel ─────────────────
            with concurrent.futures.ThreadPoolExecutor(max_workers=3) as ex:
                f_primary = ex.submit(self._fetch_primary_dlc_ids, appID)
                f_appdetails = ex.submit(self._fetch_appdetails_dlc_ids, appID)
                f_pics = ex.submit(self._get_pics_dlc_info, appID)

                primary_ok, primary_ids = f_primary.result()
                appdetails_ok, appdetails_ids = f_appdetails.result()
                pics_ok, pics_info = f_pics.result()

            if not primary_ok and not appdetails_ok and not pics_ok:
                self.log_lookup(False, "DLC request rejected")
                appID = 0
                return False

            # ── Merge into one ordered, deduped list ────────────────────────
            ordered_ids = []
            for dlcID in primary_ids:
                if dlcID not in ordered_ids:
                    ordered_ids.append(dlcID)
            for dlcID in appdetails_ids:
                if dlcID not in ordered_ids:
                    ordered_ids.append(dlcID)
            for dlcID in pics_info:
                if dlcID not in ordered_ids:
                    ordered_ids.append(dlcID)

            total = len(ordered_ids)
            dlc_word = "No DLCs found" if total == 0 else f"{total} DLC{'s' if total != 1 else ''} found"
            detail = f"AppID={appID} & {dlc_word}" if is_name_query else f"{gameName} & {dlc_word}"
            self.log_lookup(True, detail)

            if total == 0:
                return True
            fetched_names = {}
            with concurrent.futures.ThreadPoolExecutor(max_workers=10) as ex:
                future_map = {ex.submit(self._fetch_dlc_name, d): d for d in ordered_ids}
                for future in concurrent.futures.as_completed(future_map):
                    dlcID = future_map[future]
                    try:
                        fetched_names[dlcID] = future.result()
                    except Exception:
                        fetched_names[dlcID] = None

            # ── Log everything in one continuous list ───────────────────────
            for idx, dlcID in enumerate(ordered_ids):
                appName = fetched_names.get(dlcID) or pics_info.get(dlcID)
                if not appName:
                    self.log(f"     ✗ No name found for AppID {dlcID}")
                    continue
                dlcIDs.append(dlcID)
                dlcNames.append(appName)
                branch = "└─" if idx == total - 1 else "├─"
                self.log(f"     {branch} {appName} ({dlcID})")

            return True

        def _crack_game(self):
            if not self._step1_done or not self._step2_done:
                self.log("\n[!] Complete steps 1 and 2 first.")
                return

            default_mode = config["Settings"].get("DefaultMode", "ask")
            drm_method = config["Settings"].get("DRMMethod", "steamless")

            if default_mode == "steakclient" and drm_method == "steamstub":
                ModeDialog(self)
                return

            if default_mode == "regular":
                self._do_crack_regular()
            elif default_mode == "steakclient":
                self._do_crack_steakclient()
            elif default_mode == "steamclient":
                self._do_crack_steamclient()
            else:
                ModeDialog(self)

        def _do_crack_regular(self):
            self._set_buttons(False)
            threading.Thread(target=self.__crack_regular, daemon=True).start()

        def _do_crack_steakclient(self):
            self._set_buttons(False)
            threading.Thread(target=self.__crack_steakclient, daemon=True).start()

        def _set_buttons(self, enabled):
            state = tk.NORMAL if enabled else tk.DISABLED
            self._browse_btn.configure(state=state)
            self._search_btn.configure(state=state)
            if enabled:
                self._update_crack_button()
            else:
                self._crack_btn.configure(state=tk.DISABLED)

        # ── DRM removal (Steamless / SteamStub patcher) ───────────────────────
        def _get_steamstub_dll(self, is64):
            scDir = os.path.join(os.getcwd(), "rune", "Steam stub patcher")
            name = "steamstub_x64.dll" if is64 else "steamstub_x32.dll"
            return os.path.join(scDir, name)

        def _apply_steamstub(self, is64, step, total_steps, staging_root=None):
            game_exe = filedialog.askopenfilename(
                title="Select the main game executable",
                initialdir=folder_path,
                filetypes=[("Executable files", "*.exe"), ("All files", "*.*")]
            )

            if not game_exe:
                self.log_step(step, total_steps, "Patching SteamStub (winmm.dll)", ok=False, last=True)
                self.log_sub("No executable selected.", last=True)
                return None, None

            exe_dir = os.path.dirname(game_exe)
            src = self._get_steamstub_dll(is64)

            if not os.path.isfile(src):
                self.log_step(step, total_steps, "Patching SteamStub (winmm.dll)", ok=False, last=True)
                self.log_sub(f"Missing source file: {os.path.basename(src)}", last=True)
                return None, None

            if staging_root:
                rel_exe_dir = os.path.relpath(exe_dir, folder_path)
                dst_dir = os.path.join(staging_root, rel_exe_dir)
                os.makedirs(dst_dir, exist_ok=True)
            else:
                dst_dir = exe_dir

            dst = os.path.join(dst_dir, "winmm.dll")
            shutil.copyfile(src, dst)

            self.log_step(step, total_steps, "Patching SteamStub (winmm.dll)", ok=True)
            self.log_sub(os.path.basename(game_exe), last=False)
            self.log_sub(f"{os.path.basename(src)} → winmm.dll", last=True)
            return exe_dir, dst

        def _run_steamless_on_staged(self, staging_root, step, total_steps, steamlessOptions=""):
            stub_removed = []
            for root_dir, dirs, files in os.walk(staging_root):
                for fileName in list(files):
                    if not fileName.lower().endswith(".exe"):
                        continue
                    fileLocation = os.path.join(root_dir, fileName)
                    cwd_temp = os.path.join(os.getcwd(), fileName)
                    shutil.move(fileLocation, cwd_temp)
                    subprocess.call(
                        f"steamless\\Steamless.CLI.exe {steamlessOptions}\"{fileName}\"",
                        shell=True, creationflags=subprocess.CREATE_NEW_CONSOLE)
                    unpacked = cwd_temp + ".unpacked.exe"
                    if not os.path.isfile(unpacked):
                        try:
                            os.remove(cwd_temp)
                        except Exception:
                            pass
                        continue
                    stub_removed.append(fileName)
                    base_name = os.path.splitext(fileName)[0]
                    backup_name = base_name + config["Settings"]["GameEXE"]
                    shutil.move(cwd_temp, os.path.join(root_dir, backup_name))
                    shutil.move(unpacked, fileLocation)

            self.log_step(step, total_steps, "Running Steamless", ok=True)
            for idx, fname in enumerate(stub_removed):
                self.log_sub(f"{fname} ... SteamStub removed", last=(idx == len(stub_removed) - 1))
            return stub_removed

        def _stage_exes_from_folder(self, staging_root):
            for root_dir, dirs, files in os.walk(folder_path):
                rel_dir = os.path.relpath(root_dir, folder_path)
                for f in files:
                    if f.lower().endswith(".exe"):
                        staged_exe = os.path.join(staging_root, rel_dir, f)
                        os.makedirs(os.path.dirname(staged_exe), exist_ok=True)
                        shutil.copyfile(os.path.join(root_dir, f), staged_exe)

        def _run_steamless_on_folder(self, step, total_steps, steamlessOptions=""):
            stub_removed = []
            touched_files = []
            for root_dir, dirs, files in os.walk(folder_path):
                for fileName in files:
                    if not fileName.endswith(".exe"):
                        continue
                    fileLocation = root_dir + "/" + fileName
                    shutil.move(fileLocation, fileName)
                    subprocess.call(
                        f"steamless\\Steamless.CLI.exe {steamlessOptions}\"{fileName}\"",
                        shell=True, creationflags=subprocess.CREATE_NEW_CONSOLE)
                    if not os.path.isfile(fileName + ".unpacked.exe"):
                        shutil.move(fileName, fileLocation)
                        continue
                    stub_removed.append(fileName)
                    base_name = os.path.splitext(fileName)[0]
                    backup_name = base_name + config["Settings"]["GameEXE"]
                    backup_location = fileLocation.replace(fileName, backup_name)
                    shutil.move(fileName, backup_location)
                    shutil.move(fileName + ".unpacked.exe", fileLocation)
                    touched_files.append(fileLocation)
                    touched_files.append(backup_location)

            self.log_step(step, total_steps, "Running Steamless", ok=True)
            for idx, fname in enumerate(stub_removed):
                self.log_sub(f"{fname} ... SteamStub removed", last=(idx == len(stub_removed) - 1))
            return touched_files

        # ── Emulator updates (rune-emu GitHub release manifest) ───────────────
        def check_emu_updates(self, on_done):
            def _run():
                try:
                    resp = requests.get(EMU_MANIFEST_URL, timeout=15,
                                         headers={"User-Agent": USER_AGENT})
                    resp.raise_for_status()
                    manifest = resp.json()
                except Exception as e:
                    self.after(0, lambda: on_done(None, str(e)))
                    return

                outdated = []
                for name, info in manifest.get("components", {}).items():
                    if name not in COMPONENT_DIRS:
                        continue
                    local_ver = config["EmuVersions"].get(name, "0")
                    if _parse_version(info.get("version", "0")) > _parse_version(local_ver):
                        outdated.append((name, info, local_ver))
                self.after(0, lambda: on_done(outdated, None))

            threading.Thread(target=_run, daemon=True).start()

        def apply_emu_update(self, name, info, log_fn):
            target_dir = os.path.join(os.getcwd(), COMPONENT_DIRS[name])
            zip_path = os.path.join(os.getcwd(), f"_update_{name}.zip")
            label = COMPONENT_LABELS.get(name, name)
            try:
                log_fn(f"Downloading {label} ({info['version']})...")
                r = requests.get(info["url"], timeout=120, headers={"User-Agent": USER_AGENT})
                r.raise_for_status()

                digest = hashlib.sha256(r.content).hexdigest()
                if digest.lower() != info.get("sha256", "").lower():
                    log_fn(f"{label} ... FAILED  (checksum mismatch)")
                    return False

                with open(zip_path, "wb") as f:
                    f.write(r.content)

                if os.path.isdir(target_dir):
                    shutil.rmtree(target_dir)
                os.makedirs(target_dir, exist_ok=True)

                with zipfile.ZipFile(zip_path) as z:
                    z.extractall(target_dir)

                config["EmuVersions"][name] = info["version"]
                UpdateConfig()

                log_fn(f"{label} ... OK  (updated to {info['version']})")
                return True
            except Exception as e:
                log_fn(f"{label} ... FAILED  ({e})")
                return False
            finally:
                if os.path.isfile(zip_path):
                    try:
                        os.remove(zip_path)
                    except Exception:
                        pass

        # ── Crack-only staging helpers ─────────────────────────────────────────
        def _sanitize_zip_name(self, name):
            name = re.sub(r'[\\/:*?"<>|]', '', name)
            name = name.strip()
            name = re.sub(r'\s+', '.', name)
            return name or "Game"

        def _stage_add(self, staging_root, dll_location, rel_from_dll_location, src_path):
            rel_from_game_root = os.path.relpath(
                os.path.join(dll_location, rel_from_dll_location), folder_path)
            dst = os.path.join(staging_root, rel_from_game_root)
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            shutil.copyfile(src_path, dst)
            return dst

        def _get_crack_output_mode(self):
            crack_option = config["Settings"].get("CrackOption", "crack")
            crackonly_mode = (crack_option == "crackonly")
            also_zip = crack_option in ("crackonly", "both")
            staging_root = tempfile.mkdtemp(prefix="rune_crackonly_") if crackonly_mode else None
            return crackonly_mode, also_zip, staging_root

        def _zip_staging_dir(self, staging_root, step, total_steps):
            parent_dir = os.path.dirname(os.path.normpath(folder_path))
            zip_name = f"{self._sanitize_zip_name(gameName)}.Crack.Only.zip"
            zip_path = os.path.join(parent_dir, zip_name)

            added = 0
            with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as z:
                for root_dir, dirs, files in os.walk(staging_root):
                    for f in files:
                        abs_path = os.path.join(root_dir, f)
                        rel_path = os.path.relpath(abs_path, staging_root)
                        z.write(abs_path, rel_path)
                        added += 1

            self.log_step(step, total_steps, f"Building Crack Only Zip ({added} files)", ok=(added > 0), last=True)
            self.log_sub(zip_path, last=True)
            return zip_path

        def _zip_real_files(self, staged_files, step, total_steps):
            parent_dir = os.path.dirname(os.path.normpath(folder_path))
            zip_name = f"{self._sanitize_zip_name(gameName)}.Crack.Only.zip"
            zip_path = os.path.join(parent_dir, zip_name)
            added = 0
            with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as z:
                seen = set()
                for abs_path in staged_files:
                    if abs_path in seen:
                        continue
                    seen.add(abs_path)
                    if os.path.isfile(abs_path):
                        rel = os.path.relpath(abs_path, folder_path)
                        z.write(abs_path, rel)
                        added += 1
            self.log_step(step, total_steps, f"Building Crack Only Zip ({added} files)", ok=(added > 0), last=True)
            self.log_sub(zip_path, last=True)
            return zip_path

        def __crack_regular(self):
            global appID
            self.log_section("Regular Profile")

            configDir = os.path.join(os.getcwd(), "rune")
            try:
                config.read(configDir + "\\config_override.ini")
            except Exception:
                pass
            configDir = os.path.join(configDir, "emu")

            steamlessOptions = ""
            try:
                steamlessOptions = config["Developer"]["SteamlessOptions"] + " "
            except: pass

            drm_method = config["Settings"].get("DRMMethod", "steamless")
            crackonly_mode, also_zip, staging_root = self._get_crack_output_mode()

            total_steps = 4
            if also_zip:
                total_steps += 1

            # ── Step: Locate Steam API DLLs ─────────────────────────────────
            step = 0
            step += 1
            dllLocations = []
            dllBitness = {}
            apiFileVersion = "1.0.0.0"
            overwrite_notes = []
            abort = False

            for root_dir, dirs, files in os.walk(folder_path):
                apiFile = ""

                for dll_name, bak_name in (("steam_api.dll", "steam_api.rne"),
                                            ("steam_api64.dll", "steam_api64.rne")):
                    if dll_name in files:
                        if crackonly_mode:
                            apiFile = root_dir + "/" + dll_name
                            dllBitness.setdefault(root_dir, set()).add(dll_name == "steam_api64.dll")
                            try:
                                apiFileVersion = GetFileVersion(apiFile)
                            except Exception:
                                pass
                        else:
                            if bak_name in files:
                                overwrite_notes.append(f"Overwrote existing crack: {dll_name}")
                                os.remove(root_dir + "/" + dll_name)
                                shutil.move(root_dir + "/" + bak_name, root_dir + "/" + dll_name)
                            apiFile = root_dir + "/" + dll_name
                            dllBitness.setdefault(root_dir, set()).add(dll_name == "steam_api64.dll")
                            try:
                                apiFileVersion = GetFileVersion(apiFile)
                            except Exception:
                                self.log_step(step, total_steps, "Locating Steam API DLLs", ok=False, last=True)
                                self.log_sub(f"{dll_name} already cracked — aborting", last=True)
                                abort = True
                                break
                if abort:
                    break

                if apiFile != "" and root_dir not in dllLocations:
                    dllLocations.append(root_dir)

            if abort:
                self._end_crack()
                if staging_root:
                    shutil.rmtree(staging_root, ignore_errors=True)
                return

            self.log_step(step, total_steps, "Locating Steam API DLLs", ok=bool(dllLocations))
            for idx, note in enumerate(overwrite_notes):
                self.log_sub(note, last=(idx == len(overwrite_notes) - 1))

            if not dllLocations:
                self.log_done(False, "No Steam API DLL found in the selected folder.")
                self._end_crack()
                if staging_root:
                    shutil.rmtree(staging_root, ignore_errors=True)
                return

            # ── Step: DRM Removal (Steamless / SteamStub patcher) ────────────
            step += 1
            staged_files = []

            if crackonly_mode:
                for loc in dllLocations:
                    for is64_loc in dllBitness.get(loc, {True}):
                        api_name = "steam_api64.dll" if is64_loc else "steam_api.dll"
                        api_src = os.path.join(loc, api_name)
                        if os.path.isfile(api_src):
                            bak_name = os.path.splitext(api_name)[0] + config["Settings"]["GameEXE"]
                            self._stage_add(staging_root, loc, bak_name, api_src)

            if drm_method == "steamstub":
                is64 = any(True in b for b in dllBitness.values()) if dllBitness else True
                _exe_dir, winmm_dst = self._apply_steamstub(is64, step, total_steps, staging_root=staging_root)
                if also_zip and not crackonly_mode and winmm_dst:
                    staged_files.append(winmm_dst)
            else:
                if crackonly_mode:
                    self._stage_exes_from_folder(staging_root)
                    self._run_steamless_on_staged(staging_root, step, total_steps, steamlessOptions)
                else:
                    exe_touched = self._run_steamless_on_folder(step, total_steps, steamlessOptions)
                    if also_zip:
                        staged_files.extend(exe_touched)

            # ── Step: Applying Rune Emulator ─────────────────────────────────
            step += 1
            backup_notes = []
            added_files = []

            for dllCurrentLocation in dllLocations:
                wanted_api_names = {
                    "steam_api64.dll" if is64_loc else "steam_api.dll"
                    for is64_loc in dllBitness.get(dllCurrentLocation, {True})
                }

                for root_dir, dirs, files in os.walk(configDir):
                    relativeRootDir = root_dir[len(configDir) + 1:]
                    dllAbsoluteRelativeLocation = os.path.join(dllCurrentLocation, relativeRootDir)
                    if len(relativeRootDir) > 0:
                        relativeRootDir += "\\"

                    if crackonly_mode:
                        for fileName in files:
                            if fileName in ("steam_api.dll", "steam_api64.dll") and fileName not in wanted_api_names:
                                continue

                            src_path = os.path.join(root_dir, fileName)
                            dst_path = self._stage_add(staging_root, dllCurrentLocation,
                                                        os.path.join(relativeRootDir, fileName), src_path)

                            if fileName.lower() == "steam_emu.ini":
                                with open(dst_path, "r", encoding="utf-8") as file:
                                    fileContent = file.read()
                                fileContent = fileContent.replace("SteamID", str(appID))
                                fileContent = fileContent.replace("RUNE_APIVersion", apiFileVersion)
                                buf = "".join(f"{dlcIDs[i]} = {dlcNames[i]}\n" for i in range(len(dlcIDs)))
                                fileContent = fileContent.replace("RUNE_DLC", buf)
                                if dlcIDs:
                                    buf2 = "".join(f"{dlcIDs[i]}={dlcNames[i]}\n" for i in range(len(dlcIDs)))
                                    fileContent = fileContent.replace("DLCs", buf2)
                                else:
                                    fileContent = re.sub(r'^.*DLCs.*\n?', '', fileContent, flags=re.MULTILINE)
                                with open(dst_path, "w", encoding="utf-8") as file:
                                    file.write(fileContent)

                            if fileName not in added_files:
                                added_files.append(fileName)
                            staged_files.append(dst_path)
                        continue

                    for d in dirs:
                        if not os.path.isdir(os.path.join(dllAbsoluteRelativeLocation, d)):
                            os.mkdir(os.path.join(dllAbsoluteRelativeLocation, d))

                    for fileName in files:
                        if os.path.isfile(os.path.join(dllAbsoluteRelativeLocation, fileName)):
                            newName = fileName + config["Settings"]["GameEXE"]
                            if fileName in ("steam_api.dll", "steam_api64.dll"):
                                if CRACK_OPTION != "0":
                                    continue
                                newName = "steam_api.rne" if fileName == "steam_api.dll" else "steam_api64.rne"

                            if newName == "":
                                os.remove(os.path.join(dllAbsoluteRelativeLocation, fileName))
                            elif os.path.isfile(os.path.join(dllAbsoluteRelativeLocation, newName)):
                                os.remove(os.path.join(dllAbsoluteRelativeLocation, fileName))
                            else:
                                shutil.move(os.path.join(dllAbsoluteRelativeLocation, fileName),
                                            os.path.join(dllAbsoluteRelativeLocation, newName))
                                backup_notes.append(f"{fileName} → {newName}")
                                if also_zip:
                                    staged_files.append(os.path.join(dllAbsoluteRelativeLocation, newName))
                        elif fileName in ("steam_api.dll", "steam_api64.dll"):
                            continue

                        shutil.copyfile(os.path.join(root_dir, fileName),
                                        os.path.join(dllAbsoluteRelativeLocation, fileName))

                        if fileName.lower() == "steam_emu.ini":
                            with open(os.path.join(dllAbsoluteRelativeLocation, fileName), "r", encoding="utf-8") as file:
                                fileContent = file.read()
                            fileContent = fileContent.replace("SteamID", str(appID))
                            fileContent = fileContent.replace("RUNE_APIVersion", apiFileVersion)
                            buf = "".join(f"{dlcIDs[i]} = {dlcNames[i]}\n" for i in range(len(dlcIDs)))
                            fileContent = fileContent.replace("RUNE_DLC", buf)
                            if dlcIDs:
                                buf2 = "".join(f"{dlcIDs[i]}={dlcNames[i]}\n" for i in range(len(dlcIDs)))
                                fileContent = fileContent.replace("DLCs", buf2)
                            else:
                                fileContent = re.sub(r'^.*DLCs.*\n?', '', fileContent, flags=re.MULTILINE)
                            with open(os.path.join(dllAbsoluteRelativeLocation, fileName), "w", encoding="utf-8") as file:
                                file.write(fileContent)

                        if fileName not in added_files:
                            added_files.append(fileName)

                        if also_zip:
                            staged_files.append(os.path.join(dllAbsoluteRelativeLocation, fileName))

            self.log_step(step, total_steps, "Applying Rune Emulator", ok=True)
            emu_subs = [f"Backup: {note}" for note in backup_notes]
            if added_files:
                emu_subs.append(f"Added : {', '.join(added_files)}")
            for idx, s in enumerate(emu_subs):
                self.log_sub(s, last=(idx == len(emu_subs) - 1))

            # ── Step: Generating Interfaces ──────────────────────────────────
            step += 1
            if crackonly_mode:
                iface_count = 0
                for dllCurrentLocation in dllLocations:
                    for is64 in dllBitness.get(dllCurrentLocation, {True}):
                        api_name = "steam_api64.dll" if is64 else "steam_api.dll"
                        api_path = os.path.join(dllCurrentLocation, api_name)
                        if not os.path.isfile(api_path):
                            continue
                        mapping = SteamInterfaceExtractor(api_path).extract_interfaces()
                        if not mapping:
                            continue
                        rel_from_game_root = os.path.relpath(dllCurrentLocation, folder_path)
                        stage_dir = os.path.join(staging_root, rel_from_game_root)
                        for root_dir, dirs, files in os.walk(stage_dir):
                            for f in files:
                                if f.lower() == "steam_emu.ini":
                                    p = os.path.join(root_dir, f)
                                    with open(p, "r", encoding="utf-8", errors="ignore") as fh:
                                        content = fh.read()
                                    if "RUNE_Interfaces" in content:
                                        lines = [f"{k}={v}" for k, v in sorted(mapping.items())]
                                        content = content.replace("RUNE_Interfaces", "\n".join(lines))
                                        with open(p, "w", encoding="utf-8") as fh:
                                            fh.write(content)
                                        iface_count += len(mapping)
                self.log_step(step, total_steps, f"Generating Interfaces ({iface_count})",
                              ok=(iface_count > 0), last=not also_zip)
            else:
                iface_count = generate_steam_interfaces(dllLocations) if dllLocations else 0
                self.log_step(step, total_steps, f"Generating Interfaces ({iface_count})",
                              ok=(iface_count > 0), last=not also_zip)

            # ── Step: Build Crack Only zip (crackonly / both) ─────────────────
            if also_zip:
                step += 1
                if crackonly_mode:
                    self._zip_staging_dir(staging_root, step, total_steps)
                else:
                    self._zip_real_files(staged_files, step, total_steps)

            if crackonly_mode:
                shutil.rmtree(staging_root, ignore_errors=True)
                self.log_done(True, f"{gameName} crack-only created successfully.")
            else:
                self.log_done(True, f"{gameName} cracked successfully.")
            self._end_crack()

        def __crack_steakclient(self):
            self.log_section("Steakclient Profile")

            drm_method = config["Settings"].get("DRMMethod", "steamless")
            if drm_method == "steamstub":
                self.log_done(False, "Steakclient mode is unavailable while SteamStub Patcher is selected.")
                self._end_crack()
                return

            scDir = os.path.join(os.getcwd(), "rune\\steakclient")
            if not os.path.isdir(scDir):
                self.log_done(False, f"steakclient folder not found: {scDir}")
                self._end_crack()
                return

            crackonly_mode, also_zip, staging_root = self._get_crack_output_mode()

            total_steps = 5
            if also_zip:
                total_steps += 1
            step = 0

            # ── Step: Locate Steam API DLLs (x64 only — Steakclient does not
            #    support 32-bit games) ─────────────────────────────────────
            step += 1
            dll_locations = []
            for root_dir, dirs, files in os.walk(folder_path):
                if "steam_api64.dll" in files:
                    dll_locations.append((root_dir, "steam_api64.dll"))

            self.log_step(step, total_steps, "Locating Steam API DLLs", ok=bool(dll_locations))

            if not dll_locations:
                self.log_done(False, "No 64-bit Steam API DLL found in the selected folder.")
                self._end_crack()
                if staging_root:
                    shutil.rmtree(staging_root, ignore_errors=True)
                return

            # ── Step: Running Steamless ──────────────────────────────────────
            step += 1
            steamlessOptions = ""
            try:
                steamlessOptions = config["Developer"]["SteamlessOptions"] + " "
            except Exception:
                pass

            staged_files = []
            if crackonly_mode:
                self._stage_exes_from_folder(staging_root)
                self._run_steamless_on_staged(staging_root, step, total_steps, steamlessOptions)
            else:
                exe_touched = self._run_steamless_on_folder(step, total_steps, steamlessOptions)
                if also_zip:
                    staged_files.extend(exe_touched)

            # ── Step: Select executable (read-only either way) ───────────────
            step += 1
            game_exe = filedialog.askopenfilename(
                title="Select the main game EXE",
                initialdir=folder_path,
                filetypes=[("Executable files", "*.exe"), ("All files", "*.*")]
            )

            if not game_exe:
                self.log_step(step, total_steps, "Selecting Game Executable", ok=False, last=True)
                self.log_done(False, "No executable selected.")
                self._end_crack()
                if staging_root:
                    shutil.rmtree(staging_root, ignore_errors=True)
                return

            exe_dir = os.path.dirname(game_exe)
            rel_exe_dir = os.path.relpath(exe_dir, folder_path)
            self.log_step(step, total_steps, "Selecting Game Executable", ok=True)
            self.log_sub(os.path.basename(game_exe), last=True)

            # ── Step: Deploy steakclient files ───────────────────────────────
            step += 1
            steakclient_src = os.path.join(scDir, "steakclient64.dll")
            winmm_src       = os.path.join(scDir, "winmm.dll")
            steak_ini_src   = os.path.join(scDir, "steak_emu.ini")

            for src, label in [(steakclient_src, "steakclient64.dll"),
                               (winmm_src, "winmm.dll"),
                               (steak_ini_src, "steak_emu.ini")]:
                if not os.path.isfile(src):
                    self.log_step(step, total_steps, "Applying Rune Emulator", ok=False, last=True)
                    self.log_done(False, f"Missing source file: {label}")
                    self._end_crack()
                    if staging_root:
                        shutil.rmtree(staging_root, ignore_errors=True)
                    return

            source_files_map = {}
            for (root_dir, api_name) in dll_locations:
                source_files_map[root_dir] = os.path.join(root_dir, api_name)

            if crackonly_mode:
                dst_dir = os.path.join(staging_root, rel_exe_dir)
                os.makedirs(dst_dir, exist_ok=True)
            else:
                dst_dir = exe_dir

            dst_steakclient = os.path.join(dst_dir, "steakclient64.dll")
            shutil.copyfile(steakclient_src, dst_steakclient)

            dst_winmm = os.path.join(dst_dir, "winmm.dll")
            shutil.copyfile(winmm_src, dst_winmm)

            dst_ini = os.path.join(dst_dir, "steak_emu.ini")
            shutil.copyfile(steak_ini_src, dst_ini)

            if also_zip and not crackonly_mode:
                staged_files.extend([dst_steakclient, dst_winmm, dst_ini])

            try:
                with open(dst_ini, "r", encoding="utf-8") as f:
                    ini_content = f.read()
                ini_content = ini_content.replace("SteamID", str(appID))
                buf = "".join(f"{dlcIDs[i]} = {dlcNames[i]}\n" for i in range(len(dlcIDs)))
                ini_content = ini_content.replace("RUNE_DLC", buf)
                buf2 = "".join(f"{dlcIDs[i]}={dlcNames[i]}\n" for i in range(len(dlcIDs)))
                if dlcIDs:
                    ini_content = ini_content.replace("DLCs", buf2)
                else:
                    ini_content = re.sub(r'^.*DLCs.*\n?', '', ini_content, flags=re.MULTILINE)
                with open(dst_ini, "w", encoding="utf-8") as f:
                    f.write(ini_content)
            except Exception:
                pass

            self.log_step(step, total_steps, "Applying Rune Emulator", ok=True)
            self.log_sub(f"Added : winmm.dll, steakclient64.dll, steak_emu.ini", last=True)

            # ── Step: Generate interfaces (x64 API only) ──────────────────────
            step += 1
            iface_mapping = {}
            for api_path in source_files_map.values():
                if os.path.exists(api_path):
                    iface_mapping.update(SteamInterfaceExtractor(api_path).extract_interfaces())

            iface_count = 0
            if iface_mapping and os.path.isfile(dst_ini):
                try:
                    with open(dst_ini, "r", encoding="utf-8") as f:
                        ini_content = f.read()
                    if "RUNE_Interfaces" in ini_content:
                        interface_lines = [f"{k}={v}" for k, v in sorted(iface_mapping.items())]
                        ini_content = ini_content.replace("RUNE_Interfaces", "\n".join(interface_lines))
                        with open(dst_ini, "w", encoding="utf-8") as f:
                            f.write(ini_content)
                        iface_count = len(iface_mapping)
                except Exception:
                    pass

            self.log_step(step, total_steps, f"Generating Interfaces ({iface_count})",
                          ok=(iface_count > 0), last=not also_zip)

            # ── Step: Build Crack Only zip (crackonly / both) ─────────────────
            if also_zip:
                step += 1
                if crackonly_mode:
                    self._zip_staging_dir(staging_root, step, total_steps)
                else:
                    self._zip_real_files(staged_files, step, total_steps)

            if crackonly_mode:
                shutil.rmtree(staging_root, ignore_errors=True)
                self.log_done(True, f"{gameName} crack-only created successfully.")
            else:
                self.log_done(True, f"{gameName} cracked successfully.")
            self._end_crack()

        def _do_crack_steamclient(self):
            self._set_buttons(False)
            threading.Thread(target=self.__crack_steamclient, daemon=True).start()

        def _patch_shell32_string(self, file_path, is64):
            with open(file_path, "rb") as f:
                data = bytearray(f.read())
            target = b"SHELL32.dll"
            if is64:
                replacement = bytes.fromhex("52554e4536340057555300")
            else:
                replacement = bytes.fromhex("52554e4500215755532100")
            idx = data.lower().find(target.lower())
            if idx == -1:
                return False
            data[idx:idx + len(target)] = replacement
            with open(file_path, "wb") as f:
                f.write(data)
            return True

        def __crack_steamclient(self):
            self.log_section("Steamclient Profile")

            scDirBase = os.path.join(os.getcwd(), "rune", "steamclient")
            x64Dir = os.path.join(scDirBase, "x64")
            x86Dir = os.path.join(scDirBase, "x86")

            drm_method = config["Settings"].get("DRMMethod", "steamless")
            crackonly_mode, also_zip, staging_root = self._get_crack_output_mode()

            total_steps = 5
            if also_zip:
                total_steps += 1
            step = 0

            # ── Step: Locate Steam API DLLs ─────────────────────────────────
            step += 1
            dll_locations = []  # (root_dir, api_name, is64)
            for root_dir, dirs, files in os.walk(folder_path):
                if "steam_api64.dll" in files:
                    dll_locations.append((root_dir, "steam_api64.dll", True))
                elif "steam_api.dll" in files:
                    dll_locations.append((root_dir, "steam_api.dll", False))

            self.log_step(step, total_steps, "Locating Steam API DLLs", ok=bool(dll_locations))

            if not dll_locations:
                self.log_done(False, "No Steam API DLL found in the selected folder.")
                self._end_crack()
                if staging_root:
                    shutil.rmtree(staging_root, ignore_errors=True)
                return

            dllBitness = {root_dir: is64 for (root_dir, _api_name, is64) in dll_locations}

            # ── Step: DRM Removal (Steamless / SteamStub patcher) ────────────
            step += 1
            staged_files = []
            if drm_method == "steamstub":
                is64 = any(x[2] for x in dll_locations) if dll_locations else True
                if crackonly_mode:
                    self._apply_steamstub(is64, step, total_steps, staging_root=staging_root)
                else:
                    _exe_dir, winmm_dst = self._apply_steamstub(is64, step, total_steps)
                    if also_zip and winmm_dst:
                        staged_files.append(winmm_dst)
            else:
                steamlessOptions = ""
                try:
                    steamlessOptions = config["Developer"]["SteamlessOptions"] + " "
                except Exception:
                    pass
                if crackonly_mode:
                    self._stage_exes_from_folder(staging_root)
                    self._run_steamless_on_staged(staging_root, step, total_steps, steamlessOptions)
                else:
                    exe_touched = self._run_steamless_on_folder(step, total_steps, steamlessOptions)
                    if also_zip:
                        staged_files.extend(exe_touched)

            # ── Step: Backing up and patching DLLs ───────────────────────────
            step += 1
            source_files_map = {}
            supportFilesMap = {}
            apiFileVersion = "1.0.0.0"
            patch_notes = []

            for (root_dir, api_name, is64) in dll_locations:
                support_dir = x64Dir if is64 else x86Dir
                support_files = (["GameOverlayRenderer64.dll", "rune64.dll", "steamclient64.dll"] if is64
                                  else ["GameOverlayRenderer.dll", "rune.dll", "steamclient.dll"])

                missing = [f for f in support_files if not os.path.isfile(os.path.join(support_dir, f))]
                if missing:
                    patch_notes.append(f"{api_name}: missing support file(s) — {', '.join(missing)}")
                    continue

                api_path = os.path.join(root_dir, api_name)
                bak_name = os.path.splitext(api_name)[0] + config["Settings"]["GameEXE"]

                if crackonly_mode:
                    self._stage_add(staging_root, root_dir, bak_name, api_path)

                    tmp_patch = os.path.join(tempfile.gettempdir(), f"_rune_patch_{api_name}")
                    shutil.copyfile(api_path, tmp_patch)
                    try:
                        if not self._patch_shell32_string(tmp_patch, is64):
                            patch_notes.append(f"{api_name}: SHELL32.dll string not found — left unpatched")
                            continue
                        self._stage_add(staging_root, root_dir, api_name, tmp_patch)
                    finally:
                        if os.path.isfile(tmp_patch):
                            os.remove(tmp_patch)

                    patch_notes.append(f"Patched: {api_name}")

                    try:
                        apiFileVersion = GetFileVersion(api_path)
                    except Exception:
                        pass

                    for f in support_files:
                        self._stage_add(staging_root, root_dir, f, os.path.join(support_dir, f))
                    supportFilesMap[root_dir] = support_files

                    source_files_map[root_dir] = api_path
                else:
                    bak_path = os.path.join(root_dir, bak_name)

                    if os.path.isfile(bak_path):
                        patch_notes.append(f"{api_name}: overwrote existing crack")
                        os.remove(api_path)
                    else:
                        shutil.move(api_path, bak_path)

                    shutil.copyfile(bak_path, api_path)

                    if not self._patch_shell32_string(api_path, is64):
                        patch_notes.append(f"{api_name}: SHELL32.dll string not found — left unpatched")
                        continue

                    patch_notes.append(f"Patched: {api_name}")

                    try:
                        apiFileVersion = GetFileVersion(bak_path)
                    except Exception:
                        pass

                    for f in support_files:
                        dst = os.path.join(root_dir, f)
                        shutil.copyfile(os.path.join(support_dir, f), dst)
                        if also_zip:
                            staged_files.append(dst)
                    supportFilesMap[root_dir] = support_files

                    source_files_map[root_dir] = bak_path
                    if also_zip:
                        staged_files.append(api_path)
                        staged_files.append(bak_path)

            self.log_step(step, total_steps, "Backing Up & Patching DLLs", ok=bool(source_files_map))
            for idx, note in enumerate(patch_notes):
                self.log_sub(note, last=(idx == len(patch_notes) - 1))

            if not source_files_map:
                self.log_done(False, "No DLLs were successfully patched.")
                self._end_crack()
                if staging_root:
                    shutil.rmtree(staging_root, ignore_errors=True)
                return

            # ── Step: Applying Rune Emulator ─────────────────────────────────
            step += 1
            configDir = os.path.join(os.getcwd(), "rune", "emu")
            added_files = []

            for dllCurrentLocation in source_files_map:
                for root_dir, dirs, files in os.walk(configDir):
                    relativeRootDir = root_dir[len(configDir) + 1:]
                    dllAbsoluteRelativeLocation = os.path.join(dllCurrentLocation, relativeRootDir)
                    if len(relativeRootDir) > 0:
                        relativeRootDir += "\\"

                    if crackonly_mode:
                        for fileName in files:
                            if fileName in ("steam_api.dll", "steam_api64.dll"):
                                continue

                            src_path = os.path.join(root_dir, fileName)
                            dst_path = self._stage_add(staging_root, dllCurrentLocation,
                                                        os.path.join(relativeRootDir, fileName), src_path)

                            if fileName.lower() == "steam_emu.ini":
                                with open(dst_path, "r", encoding="utf-8") as file:
                                    fileContent = file.read()
                                fileContent = fileContent.replace("SteamID", str(appID))
                                fileContent = fileContent.replace("RUNE_APIVersion", apiFileVersion)
                                buf = "".join(f"{dlcIDs[i]} = {dlcNames[i]}\n" for i in range(len(dlcIDs)))
                                fileContent = fileContent.replace("RUNE_DLC", buf)
                                if dlcIDs:
                                    buf2 = "".join(f"{dlcIDs[i]}={dlcNames[i]}\n" for i in range(len(dlcIDs)))
                                    fileContent = fileContent.replace("DLCs", buf2)
                                else:
                                    fileContent = re.sub(r'^.*DLCs.*\n?', '', fileContent, flags=re.MULTILINE)
                                with open(dst_path, "w", encoding="utf-8") as file:
                                    file.write(fileContent)

                            if fileName not in added_files:
                                added_files.append(fileName)
                        continue

                    for d in dirs:
                        if not os.path.isdir(os.path.join(dllAbsoluteRelativeLocation, d)):
                            os.mkdir(os.path.join(dllAbsoluteRelativeLocation, d))

                    for fileName in files:
                        if fileName in ("steam_api.dll", "steam_api64.dll"):
                            continue

                        if os.path.isfile(os.path.join(dllAbsoluteRelativeLocation, fileName)):
                            os.remove(os.path.join(dllAbsoluteRelativeLocation, fileName))

                        shutil.copyfile(os.path.join(root_dir, fileName),
                                        os.path.join(dllAbsoluteRelativeLocation, fileName))

                        if fileName.lower() == "steam_emu.ini":
                            with open(os.path.join(dllAbsoluteRelativeLocation, fileName), "r", encoding="utf-8") as file:
                                fileContent = file.read()
                            fileContent = fileContent.replace("SteamID", str(appID))
                            fileContent = fileContent.replace("RUNE_APIVersion", apiFileVersion)
                            buf = "".join(f"{dlcIDs[i]} = {dlcNames[i]}\n" for i in range(len(dlcIDs)))
                            fileContent = fileContent.replace("RUNE_DLC", buf)
                            if dlcIDs:
                                buf2 = "".join(f"{dlcIDs[i]}={dlcNames[i]}\n" for i in range(len(dlcIDs)))
                                fileContent = fileContent.replace("DLCs", buf2)
                            else:
                                fileContent = re.sub(r'^.*DLCs.*\n?', '', fileContent, flags=re.MULTILINE)
                            with open(os.path.join(dllAbsoluteRelativeLocation, fileName), "w", encoding="utf-8") as file:
                                file.write(fileContent)

                        if fileName not in added_files:
                            added_files.append(fileName)

                        if also_zip:
                            staged_files.append(os.path.join(dllAbsoluteRelativeLocation, fileName))

            for sf_list in supportFilesMap.values():
                for f in sf_list:
                    if f not in added_files:
                        added_files.append(f)

            self.log_step(step, total_steps, "Applying Rune Emulator", ok=True)
            if added_files:
                self.log_sub(f"Added : {', '.join(added_files)}", last=True)

            # ── Step: Generate interfaces ─────────────────────────────────
            step += 1
            if crackonly_mode:
                iface_count = 0
                for dllCurrentLocation, api_path in source_files_map.items():
                    if not os.path.isfile(api_path):
                        continue
                    mapping = SteamInterfaceExtractor(api_path).extract_interfaces()
                    if not mapping:
                        continue
                    rel_from_game_root = os.path.relpath(dllCurrentLocation, folder_path)
                    stage_dir = os.path.join(staging_root, rel_from_game_root)
                    for root_dir, dirs, files in os.walk(stage_dir):
                        for f in files:
                            if f.lower() == "steam_emu.ini":
                                p = os.path.join(root_dir, f)
                                with open(p, "r", encoding="utf-8", errors="ignore") as fh:
                                    content = fh.read()
                                if "RUNE_Interfaces" in content:
                                    lines = [f"{k}={v}" for k, v in sorted(mapping.items())]
                                    content = content.replace("RUNE_Interfaces", "\n".join(lines))
                                    with open(p, "w", encoding="utf-8") as fh:
                                        fh.write(content)
                                    iface_count += len(mapping)
                self.log_step(step, total_steps, f"Generating Interfaces ({iface_count})",
                              ok=(iface_count > 0), last=not also_zip)
            else:
                iface_count = generate_steam_interfaces(list(source_files_map.keys()),
                                                         ini_filename="steam_emu.ini",
                                                         source_files=source_files_map)
                self.log_step(step, total_steps, f"Generating Interfaces ({iface_count})",
                              ok=(iface_count > 0), last=not also_zip)

            # ── Step: Build Crack Only zip (crackonly / both) ─────────────────
            if also_zip:
                step += 1
                if crackonly_mode:
                    self._zip_staging_dir(staging_root, step, total_steps)
                else:
                    self._zip_real_files(staged_files, step, total_steps)

            if crackonly_mode:
                shutil.rmtree(staging_root, ignore_errors=True)
                self.log_done(True, f"{gameName} crack-only created successfully.")
            else:
                self.log_done(True, f"{gameName} cracked successfully.")
            self._end_crack()

        def _end_crack(self):
            ReloadConfig()
            self._set_buttons(True)

        # ── Settings ──────────────────────────────────────────────────────────
        def _open_settings(self):
            SettingsDialog(self)

    # ─── MODE DIALOG ─────────────────────────────────────────────────────────────
    class ModeDialog(ctk.CTkToplevel):
        def __init__(self, master: RuneApp):
            super().__init__(master)
            self.master_app = master
            self.title("Select Crack Mode")
            self.geometry("420x320")
            self.withdraw()
            self.grab_set()

            drm_method = config["Settings"].get("DRMMethod", "steamless")
            steak_disabled = (drm_method == "steamstub")

            ctk.CTkLabel(self, text="Select Crack Mode",
                        font=ctk.CTkFont(size=16, weight="bold")).pack(pady=(20, 2))
            short = gameName[:42] + "…" if len(gameName) > 44 else gameName
            ctk.CTkLabel(self, text=short, text_color="gray60").pack(pady=(0, 15))

            row = ctk.CTkFrame(self, fg_color="transparent")
            row.pack(fill='x', padx=20)

            ctk.CTkButton(row, text="Regular", height=60,
                         command=lambda: self._pick("regular")).pack(side='left', expand=True, fill='x', padx=(0, 8))

            steak_btn = ctk.CTkButton(row, text="Steakclient (x64 only)", height=60,
                         command=lambda: self._pick("steakclient"))
            steak_btn.pack(side='left', expand=True, fill='x')
            if steak_disabled:
                steak_btn.configure(state=tk.DISABLED, fg_color="gray30", hover_color="gray30")

            ctk.CTkButton(self, text="Steamclient", height=60,
                         command=lambda: self._pick("steamclient")).pack(fill='x', padx=20, pady=(10, 0))

            ctk.CTkButton(self, text="Cancel", width=100, fg_color="gray40",
                         hover_color="gray30", command=lambda: self._pick(None)).pack(pady=20)

            self._center_on_parent()
            self.deiconify()
            self.after(10, lambda: self.focus())

        def _center_on_parent(self):
            self.update_idletasks()
            pw, ph = self.master_app.winfo_width(), self.master_app.winfo_height()
            px, py = self.master_app.winfo_x(), self.master_app.winfo_y()
            w, h = 420, 320
            x = px + (pw - w) // 2
            y = py + (ph - h) // 2
            self.geometry(f"{w}x{h}+{x}+{y}")

        def _pick(self, mode):
            self.destroy()
            if mode == "regular":
                self.master_app._do_crack_regular()
            elif mode == "steakclient":
                self.master_app._do_crack_steakclient()
            elif mode == "steamclient":
                self.master_app._do_crack_steamclient()

    # ─── SETTINGS DIALOG ─────────────────────────────────────────────────────────
    class SettingsDialog(ctk.CTkToplevel):
        def __init__(self, master):
            super().__init__(master)
            self.master_app = master
            self.title("Settings")
            self.geometry("420x660")
            self.withdraw()
            self.grab_set()

            ctk.CTkLabel(self, text="Settings",
                        font=ctk.CTkFont(size=18, weight="bold")).pack(pady=(20, 0))
            ctk.CTkLabel(self, text=f"RUNEAutoCracker v{VERSION}",
                        text_color="gray60").pack(pady=(0, 15))

            body = ctk.CTkFrame(self, fg_color="transparent")
            body.pack(fill='both', expand=True, padx=20)

            ctk.CTkLabel(body, text="SteamStub DRM Removal:", anchor="w").pack(fill='x', pady=(5, 2))
            self.drm_method_var = tk.StringVar(master=self, value=config["Settings"].get("DRMMethod", "steamless"))
            radio_frame = ctk.CTkFrame(body, fg_color="transparent")
            radio_frame.pack(fill='x', padx=10)
            ctk.CTkRadioButton(radio_frame, text="Steamless", variable=self.drm_method_var, value="steamless",
                               command=self._save_drm_method).pack(anchor='w', pady=2)
            ctk.CTkRadioButton(radio_frame, text="SteamStub patcher", variable=self.drm_method_var, value="steamstub",
                               command=self._save_drm_method).pack(anchor='w', pady=2)

            ctk.CTkLabel(body, text="Backup Suffix (EXE only):", anchor="w").pack(fill='x', pady=(15, 2))
            self.suffix_var = tk.StringVar(master=self, value=config["Settings"].get("GameEXE", ".rne"))
            ctk.CTkEntry(body, textvariable=self.suffix_var, width=120).pack(anchor='w', padx=10)
            self.suffix_var.trace_add("write", self._update_suffix)

            ctk.CTkLabel(body, text="Default Emu:", anchor="w").pack(fill='x', pady=(15, 2))
            self.default_mode_var = tk.StringVar(master=self, value=config["Settings"].get("DefaultMode", "ask"))
            mode_frame = ctk.CTkFrame(body, fg_color="transparent")
            mode_frame.pack(fill='x', padx=10)
            ctk.CTkRadioButton(mode_frame, text="Regular", variable=self.default_mode_var, value="regular",
                               command=self._save_default_mode).pack(anchor='w', pady=2)
            ctk.CTkRadioButton(mode_frame, text="Steamclient", variable=self.default_mode_var, value="steamclient",
                               command=self._save_default_mode).pack(anchor='w', pady=2)
            ctk.CTkRadioButton(mode_frame, text="Steakclient", variable=self.default_mode_var, value="steakclient",
                               command=self._save_default_mode).pack(anchor='w', pady=2)
            ctk.CTkRadioButton(mode_frame, text="Always ask", variable=self.default_mode_var, value="ask",
                               command=self._save_default_mode).pack(anchor='w', pady=2)

            ctk.CTkLabel(body, text="Crack Mode:", anchor="w").pack(fill='x', pady=(15, 2))
            self.crack_option_var = tk.StringVar(master=self, value=config["Settings"].get("CrackOption", "crack"))
            crack_frame = ctk.CTkFrame(body, fg_color="transparent")
            crack_frame.pack(fill='x', padx=10)
            ctk.CTkRadioButton(crack_frame, text="Full Crack", variable=self.crack_option_var,
                               value="crack", command=self._save_crack_option).pack(anchor='w', pady=2)
            ctk.CTkRadioButton(crack_frame, text="Crack Only", variable=self.crack_option_var,
                               value="crackonly", command=self._save_crack_option).pack(anchor='w', pady=2)
            ctk.CTkRadioButton(crack_frame, text="Full Crack + Crack Only", variable=self.crack_option_var,
                               value="both", command=self._save_crack_option).pack(anchor='w', pady=2)

            ctk.CTkLabel(body, text="Emulator Updates:", anchor="w").pack(fill='x', pady=(15, 2))
            self._update_btn = ctk.CTkButton(body, text="Check for Emulator Updates",
                                              command=self._check_updates)
            self._update_btn.pack(fill='x', padx=10, pady=(0, 6))

            self.check_startup_var = tk.BooleanVar(
                master=self, value=config["Settings"].get("CheckUpdatesOnStartup", "1") == "1")
            ctk.CTkCheckBox(body, text="Check for updates on startup",
                            variable=self.check_startup_var,
                            command=self._save_check_startup).pack(anchor='w', padx=10)

            bf = ctk.CTkFrame(self, fg_color="transparent")
            bf.pack(pady=20)
            ctk.CTkButton(bf, text="Reset Defaults", width=130, fg_color="gray40",
                         hover_color="gray30", command=self._reset).pack(side='left', padx=(0, 8))
            ctk.CTkButton(bf, text="Close", width=100, command=self.destroy).pack(side='left')

            self._center_on_parent()
            self.deiconify()
            self.after(10, lambda: self.focus())

        def _center_on_parent(self):
            self.update_idletasks()
            pw, ph = self.master_app.winfo_width(), self.master_app.winfo_height()
            px, py = self.master_app.winfo_x(), self.master_app.winfo_y()
            w, h = 420, 660
            x = px + (pw - w) // 2
            y = py + (ph - h) // 2
            self.geometry(f"{w}x{h}+{x}+{y}")

        def _save_check_startup(self):
            UpdateConfigKey("CheckUpdatesOnStartup", "1" if self.check_startup_var.get() else "0")

        def _check_updates(self):
            self._update_btn.configure(state=tk.DISABLED, text="Checking...")

            def _on_done(outdated, error):
                self._update_btn.configure(state=tk.NORMAL, text="Check for Emulator Updates")
                if error:
                    self.master_app.log(f"\n[!] Emulator update check failed: {error}")
                    return
                if not outdated:
                    self.master_app.log("\n[i] All emulator files are up to date.")
                    return
                EmuUpdateDialog(self.master_app, outdated)

            self.master_app.check_emu_updates(_on_done)

        def _save_drm_method(self):
            UpdateConfigKey("DRMMethod", self.drm_method_var.get())

        def _update_suffix(self, *_):
            UpdateConfigKey("GameEXE", self.suffix_var.get())

        def _save_default_mode(self):
            UpdateConfigKey("DefaultMode", self.default_mode_var.get())

        def _save_crack_option(self):
            UpdateConfigKey("CrackOption", self.crack_option_var.get())

        def _reset(self):
            ResetConfig()
            self.drm_method_var.set(config["Settings"].get("DRMMethod", "steamless"))
            self.suffix_var.set(config["Settings"].get("GameEXE", ".rne"))
            self.default_mode_var.set(config["Settings"].get("DefaultMode", "ask"))
            self.crack_option_var.set(config["Settings"].get("CrackOption", "crack"))

    # ─── EMULATOR UPDATE DIALOG ──────────────────────────────────────────────────
    class EmuUpdateDialog(ctk.CTkToplevel):
        def __init__(self, app, outdated):
            super().__init__(app)
            self.master_app = app
            self.outdated = outdated
            self.title("Emulator Updates")
            self.geometry("440x420")
            self.withdraw()
            self.grab_set()

            ctk.CTkLabel(self, text="Emulator Updates Available",
                        font=ctk.CTkFont(size=16, weight="bold")).pack(pady=(20, 10))

            list_frame = ctk.CTkFrame(self, fg_color="transparent")
            list_frame.pack(fill='x', padx=20)
            for name, info, local_ver in self.outdated:
                label = COMPONENT_LABELS.get(name, name)
                ctk.CTkLabel(list_frame, text=f"{label}:  {local_ver} → {info['version']}",
                             font=ctk.CTkFont(size=13), anchor="w").pack(fill='x', pady=2)

            self._log_box = ctk.CTkTextbox(self, font=("Consolas", 13), wrap='word', height=140)
            self._log_box.pack(fill='both', expand=True, padx=20, pady=(10, 10))
            self._log_text = self._log_box._textbox
            self._log_text.tag_config("ok", foreground="#3fb950")
            self._log_text.tag_config("err", foreground="#f85149")
            self._log_text.tag_config("info", foreground="#79c0ff")
            self._log_text.config(state=tk.DISABLED)

            bf = ctk.CTkFrame(self, fg_color="transparent")
            bf.pack(pady=(0, 20))
            self._update_btn = ctk.CTkButton(bf, text="Update All", width=130,
                                              command=self._update_all)
            self._update_btn.pack(side='left', padx=(0, 8))
            self._close_btn = ctk.CTkButton(bf, text="Close", width=100, fg_color="gray40",
                                             hover_color="gray30", command=self.destroy)
            self._close_btn.pack(side='left')

            self._center_on_parent()
            self.deiconify()
            self.after(10, lambda: self.focus())

        def _center_on_parent(self):
            self.update_idletasks()
            pw, ph = self.master_app.winfo_width(), self.master_app.winfo_height()
            px, py = self.master_app.winfo_x(), self.master_app.winfo_y()
            w, h = 440, 420
            x = px + (pw - w) // 2
            y = py + (ph - h) // 2
            self.geometry(f"{w}x{h}+{x}+{y}")

        def _dialog_log(self, msg):
            self._log_text.config(state=tk.NORMAL)
            if "FAILED" in msg:
                tag = "err"
            elif "OK" in msg:
                tag = "ok"
            elif msg.startswith("Downloading"):
                tag = "info"
            else:
                tag = None
            if tag:
                self._log_text.insert(tk.END, msg + "\n", tag)
            else:
                self._log_text.insert(tk.END, msg + "\n")
            self._log_text.see(tk.END)
            self._log_text.config(state=tk.DISABLED)
            self.update()

        def _update_all(self):
            self._update_btn.configure(state=tk.DISABLED)
            self._close_btn.configure(state=tk.DISABLED)

            def _run():
                for name, info, _local_ver in self.outdated:
                    self.master_app.apply_emu_update(name, info, lambda m: self.after(0, self._dialog_log, m))
                self.after(0, self._finish)

            threading.Thread(target=_run, daemon=True).start()

        def _finish(self):
            self._dialog_log("Done.")
            self._close_btn.configure(state=tk.NORMAL)

    # ─── Global helpers (needed by generate_steam_interfaces etc.) ────────────────
    _app_ref: Optional[RuneApp] = None

    def update_logs(msg):
        if _app_ref:
            _app_ref.log(msg)

    # ─── LAUNCH ──────────────────────────────────────────────────────────────────
    app = RuneApp()
    _app_ref = app
    app.mainloop()

except Exception:
    print("\n[!!!] A Python error occurred! Writing to error.log\n---")
    with open("error.log", "w", encoding="utf-8") as f:
        f.write(f"RUNEAutoCracker v{VERSION}\n---\nPython error.\n---\n\n")
        traceback.print_exc(file=f)
    traceback.print_exc()
    print("---\nSee error.log")
