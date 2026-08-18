import os
import time
import subprocess

WATCH_DIR = os.path.dirname(os.path.abspath(__file__))
CHECK_INTERVAL = 3  # Check for changes every 3 seconds

def get_latest_mtime(folder):
    max_mtime = 0
    for root, dirs, files in os.walk(folder):
        # Ignore git tracking folder
        if '.git' in dirs:
            dirs.remove('.git')
        for file in files:
            filepath = os.path.join(root, file)
            try:
                mtime = os.path.getmtime(filepath)
                if mtime > max_mtime:
                    max_mtime = mtime
            except OSError:
                pass
    return max_mtime

def push_changes_to_github():
    print("\n[Auto-Sync] Saved changes detected! Syncing to GitHub...")
    subprocess.run(["git", "add", "."], cwd=WATCH_DIR)
    
    # Check if there are changes staged
    status = subprocess.run(["git", "status", "--porcelain"], cwd=WATCH_DIR, capture_output=True, text=True)
    if status.stdout.strip():
        subprocess.run(["git", "commit", "-m", "auto: update file from local editor"], cwd=WATCH_DIR)
        result = subprocess.run(["git", "push"], cwd=WATCH_DIR)
        if result.returncode == 0:
            print("[Auto-Sync] Successfully updated GitHub repository!\n")
        else:
            print("[Auto-Sync] Push failed. Make sure your GitHub remote is set up.\n")
    else:
        print("[Auto-Sync] No net changes detected.\n")

if __name__ == "__main__":
    print(f"Monitoring '{WATCH_DIR}' for file saves. Press Ctrl+C to stop.")
    last_mtime = get_latest_mtime(WATCH_DIR)
    
    try:
        while True:
            time.sleep(CHECK_INTERVAL)
            current_mtime = get_latest_mtime(WATCH_DIR)
            if current_mtime > last_mtime:
                last_mtime = current_mtime
                push_changes_to_github()
    except KeyboardInterrupt:
        print("\nAuto-sync stopped.")