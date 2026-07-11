import os
import sys
import time
import shutil
import zipfile
import tempfile
import subprocess
import urllib.request
import urllib.error

REPO = "Mush-iii/RUNEAutoCracker"
EXE_NAME = "RUNEAutoCracker.exe"
ZIP_NAME = "RUNEAutoCracker.zip"
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) RUNEAutoCracker-Updater"
ZIP_URL = f"https://github.com/Mush-iii/RUNEAutoCracker/releases/latest/download/RUNEAutoCracker.zip"


def download_file(url, dest_path):
    opener = urllib.request.build_opener(urllib.request.HTTPRedirectHandler)
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with opener.open(req, timeout=120) as resp, open(dest_path, "wb") as out:
        total = int(resp.headers.get("Content-Length", 0))
        downloaded = 0
        while True:
            chunk = resp.read(65536)
            if not chunk:
                break
            out.write(chunk)
            downloaded += len(chunk)
            if total:
                pct = downloaded * 100 // total
                print(f"\r  {pct}%  ({downloaded}/{total} bytes)", end="", flush=True)
    print()


def replace_exe(new_exe_path, target_exe_path):
    backup_path = target_exe_path + ".old"
    if os.path.isfile(backup_path):
        try:
            os.remove(backup_path)
        except Exception:
            pass
    last_err = None
    for attempt in range(10):
        try:
            if os.path.isfile(target_exe_path):
                os.rename(target_exe_path, backup_path)
            shutil.move(new_exe_path, target_exe_path)
            last_err = None
            break
        except Exception as e:
            last_err = e
            print(f"  file locked, retrying... ({attempt + 1}/10)")
            time.sleep(1)
    if last_err:
        raise last_err
    try:
        os.remove(backup_path)
    except Exception:
        print("Note: could not delete .old backup (locked); leaving it behind.")


def self_delete():
    """Spawn a detached helper that waits for this process to exit, then
    deletes the updater exe (and itself)."""
    if not getattr(sys, "frozen", False):
        return
    self_path = os.path.abspath(sys.executable)
    bat_path = os.path.join(tempfile.gettempdir(), "rune_updater_cleanup.bat")
    bat_contents = (
        "@echo off\r\n"
        ":retry\r\n"
        f"del /f /q \"{self_path}\" >nul 2>&1\r\n"
        f"if exist \"{self_path}\" (\r\n"
        "  timeout /t 1 /nobreak >nul\r\n"
        "  goto retry\r\n"
        ")\r\n"
        "del /f /q \"%~f0\"\r\n"
    )
    with open(bat_path, "w") as f:
        f.write(bat_contents)
    subprocess.Popen(
        ["cmd", "/c", bat_path],
        creationflags=subprocess.CREATE_NO_WINDOW,
        close_fds=True,
    )


def main():
    self_dir = os.getcwd()
    if getattr(sys, "frozen", False):
        self_dir = os.path.dirname(sys.executable)
    elif "__file__" in globals():
        self_dir = os.path.dirname(os.path.abspath(__file__))

    target_exe_path = os.path.join(self_dir, EXE_NAME)
    print(f"Target exe path: {target_exe_path}")

    work_dir = tempfile.mkdtemp(prefix="rune_update_")
    try:
        zip_path = os.path.join(work_dir, ZIP_NAME)
        print(f"Downloading: {ZIP_URL}")
        download_file(ZIP_URL, zip_path)

        print("Download complete. Extracting...")
        with zipfile.ZipFile(zip_path) as z:
            z.extractall(work_dir)
        os.remove(zip_path)

        found_exe = None
        for root, _dirs, files in os.walk(work_dir):
            for f in files:
                if f.lower() == EXE_NAME.lower():
                    found_exe = os.path.join(root, f)
                    break
            if found_exe:
                break

        if not found_exe:
            raise RuntimeError(f"{EXE_NAME} not found inside {ZIP_NAME}")

        print("Replacing executable...")
        replace_exe(found_exe, target_exe_path)
        print("Executable replaced.")

        print("Relaunching app...")
        subprocess.Popen(
            [target_exe_path],
            cwd=self_dir,
            creationflags=subprocess.CREATE_NO_WINDOW,
        )
        print("Update complete.")

        self_delete()
    except Exception as e:
        print(f"Update failed: {e}")
    finally:
        shutil.rmtree(work_dir, ignore_errors=True)


if __name__ == "__main__":
    main()
    sys.exit(0)
