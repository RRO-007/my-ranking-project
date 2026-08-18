import os
import time
import subprocess

WATCH_DIR = os.path.dirname(os.path.abspath(__file__))
CHECK_INTERVAL = 3  # Check for changes every 3 seconds

def get_latest_mtime(folder):
    max_mtime = 0
    for root, dirs, files in os.walk(folder):
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
    # Inspect untracked and modified files prior to staging
    status = subprocess.run(["git", "status", "--porcelain"], cwd=WATCH_DIR, capture_output=True, text=True)
    raw_lines = [line.strip() for line in status.stdout.strip().splitlines() if line.strip()]
    
    if raw_lines:
        print("\n[Auto-Sync] Saved changes detected!")
        print("[Auto-Sync] Syncing the following file(s):")
        for line in raw_lines:
            # Extract status code and file path
            parts = line.split(maxsplit=1)
            file_path = parts[1] if len(parts) > 1 else line
            print(f"  • {file_path}")
            
        subprocess.run(["git", "add", "."], cwd=WATCH_DIR)
        
        file_count = len(raw_lines)
        commit_msg = f"auto: sync {file_count} updated file(s) from local workspace"
        subprocess.run(["git", "commit", "-m", commit_msg], cwd=WATCH_DIR)
        
        result = subprocess.run(["git", "push"], cwd=WATCH_DIR)
        if result.returncode == 0:
            print("[Auto-Sync] Successfully pushed all listed files to GitHub!\n")
        else:
            print("[Auto-Sync] Push failed. Verify your remote repository setup.\n")
    else:
        print("\n[Auto-Sync] File save event detected, but no net file modifications found.")

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
        print("\nAuto-sync monitor stopped.")