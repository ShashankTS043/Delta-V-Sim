import json
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import pandas as pd
import sys
import time
import os
import glob
from json import JSONDecodeError

# -------------------------
# Robust loader: read newest snapshot file
# -------------------------
def load_simulation_data_newest_snapshot(folder=".", prefix="data_snapshot_", max_retries=8, base_delay=0.02, debug=False):
    """
    Find newest snapshot file matching prefix and attempt to load it.
    Retries on PermissionError/JSONDecodeError briefly (file being written).
    Returns parsed JSON dict or None if none available/readable.
    """
    pattern = os.path.join(folder, f"{prefix}*.json")
    raw_files = glob.glob(pattern)
    if not raw_files:
        return None

    # Safely build a list of (path, mtime) skipping files that disappear while listing.
    files_with_mtime = []
    for p in raw_files:
        try:
            m = os.path.getmtime(p)
            files_with_mtime.append((p, m))
        except (FileNotFoundError, PermissionError, OSError):
            # file vanished or inaccessible — skip it
            continue

    if not files_with_mtime:
        return None

    # sort by mtime descending and pick top candidates
    files_with_mtime.sort(key=lambda x: x[1], reverse=True)
    candidates = [p for p, _ in files_with_mtime[:3]]  # try up to 3 newest

    if debug:
        print("Snapshot candidates:", candidates)

    for candidate in candidates:
        attempt = 0
        while attempt < max_retries:
            try:
                with open(candidate, "r", encoding="utf-8") as f:
                    data = json.load(f)
                if debug:
                    print("Loaded snapshot:", candidate)
                return data
            except FileNotFoundError:
                # vanished while trying to open
                break
            except PermissionError:
                attempt += 1
                time.sleep(base_delay * (1.5 ** attempt))
                continue
            except JSONDecodeError:
                # partial write — wait and retry
                attempt += 1
                time.sleep(base_delay * (1.5 ** attempt))
                continue
            except Exception as e:
                if debug:
                    print(f"Unexpected error reading {candidate}: {e}")
                break
    return None

# -------------------------
# Leaderboard visualization (matplotlib)
# -------------------------
fig, ax = plt.subplots()

# Cache so we don't hammer the disk every frame
sim_cache = None
last_read_ts = 0.0
READ_INTERVAL = 1.0 / 5.0  # Read up to 5 times a second (throttle)

def animate(i):
    """
    Called by FuncAnimation. Uses cached simulation data and a robust loader.
    Returns an iterable of matplotlib artists.
    """
    global sim_cache, last_read_ts

    # Throttle reads to avoid busy loop
    now = time.time()
    if (now - last_read_ts) >= READ_INTERVAL:
        new_data = load_simulation_data_newest_snapshot(folder=".", prefix="data_snapshot_")
        last_read_ts = now
        if new_data is not None:
            sim_cache = new_data  # update cache only on successful read

    data = sim_cache
    if data is None:
        # Waiting for first successful read
        return []

    agents = data.get('agents', [])
    if not agents:
        return []

    try:
        # Normalize and select columns
        df = pd.json_normalize(agents)

        # Protect against missing columns:
        if 'rank' not in df.columns or 'id' not in df.columns or 'vehicle_state.battery_soc' not in df.columns:
            return []

        df = df[['rank', 'id', 'vehicle_state.tyre_life', 'vehicle_state.tyre_compound']]
        df = df.sort_values(by='rank', ascending=True)

        # Plot
        ax.clear()
        # IDs in dataset are now simple (e.g., "Ocon"), but splitting still works if underscore exists
        y_labels = df['id'].astype(str).str.split('_').str[0]
        x_values = df['vehicle_state.tyre_life'] * 100

        bars = ax.barh(y_labels, x_values)
        ax.invert_yaxis()
        ax.set_title('Aether 2026: Live Tyre Life (%)')
        ax.set_xlabel('Tyre Life Remaining (%)')
        ax.set_xlim(0, 100) # 0-100% is still correct
        # attach labels to bars — guard against unusual values
        try:
            ax.bar_label(bars, fmt='%.1f%%')
        except Exception:
            pass
        plt.tight_layout()

        # Return the drawn artists (bar patches) so FuncAnimation can blit if available
        return list(bars)

    except Exception as e:
        print(f"Error during plotting: {e}")
        return []

def run_leaderboard():
    print("--- LIVE LEADERBOARD (MATPLOTLIB) STARTED ---")
    print("--- This window will update every 1 second ---")

    # Set cache_frame_data=False to avoid unbounded caching warning
    ani = animation.FuncAnimation(fig, animate, interval=1000, cache_frame_data=False)

    try:
        plt.show()
    except Exception as e:
        print(f"Matplotlib window closed or crashed: {e}")

if __name__ == '__main__':
    run_leaderboard()
