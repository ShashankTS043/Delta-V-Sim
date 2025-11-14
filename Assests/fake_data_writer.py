# fake_data_writer.py
import networkx as nx
import json
import time
import numpy as np
import sys
import os
import tempfile
import glob
from datetime import datetime

# -------------------------
# Helper: time parsing / formatting
# -------------------------
def parse_time_to_seconds(t):
    if t is None:
        return None
    try:
        return float(str(t))
    except (ValueError, TypeError):
        pass
    parts = str(t).split(':')
    try:
        if len(parts) == 2:
            minutes = int(parts[0])
            seconds = float(parts[1])
            return minutes * 60.0 + seconds
        elif len(parts) == 3:
            hours = int(parts[0])
            minutes = int(parts[1])
            seconds = float(parts[2])
            return hours * 3600.0 + minutes * 60.0 + seconds
    except Exception:
        return None
    return None

def format_seconds_to_str(s):
    if s is None:
        return "0:00.000"
    try:
        s = float(s)
    except (ValueError, TypeError):
        return "0:00.000"
    minutes = int(s // 60)
    seconds = s - minutes*60
    return f"{minutes}:{seconds:06.3f}"  # mm:ss.mmm

# -------------------------
# 1. HIGH-FIDELITY TRACK DEFINITION
# -------------------------
def build_bahrain_track():
    G = nx.DiGraph()
    G.add_node("n_t15_apex", pos=(800, 700))
    G.add_node("n_t1_brake", pos=(800, 150))
    G.add_node("n_t1_apex", pos=(770, 100))
    G.add_node("n_t2_apex", pos=(700, 150))
    G.add_node("n_t3_exit", pos=(700, 200))
    G.add_node("n_t4_brake", pos=(650, 350))
    G.add_node("n_t4_apex", pos=(610, 380))
    G.add_node("n_t5_entry", pos=(400, 380))
    G.add_node("n_t7_apex", pos=(350, 420))
    G.add_node("n_t8_brake", pos=(300, 380))
    G.add_node("n_t8_apex", pos=(270, 350))
    G.add_node("n_t9_entry", pos=(200, 420))
    G.add_node("n_t10_apex", pos=(150, 400))
    G.add_node("n_t11_brake", pos=(150, 650))
    G.add_node("n_t11_apex", pos=(180, 700))
    G.add_node("n_t12_apex", pos=(250, 750))
    G.add_node("n_t13_brake", pos=(500, 750))
    G.add_node("n_t13_apex", pos=(550, 780))
    G.add_node("n_t14_brake", pos=(750, 780))

    G.add_edge("n_t15_apex", "n_t1_brake", length=1100, radius=None, x_mode_allowed=True, mom_detection=True, is_finish_line=True)
    G.add_edge("n_t1_brake", "n_t1_apex", length=110, radius=60, x_mode_allowed=False)
    G.add_edge("n_t1_apex", "n_t2_apex", length=100, radius=70, x_mode_allowed=False)
    G.add_edge("n_t2_apex", "n_t3_exit", length=100, radius=70, x_mode_allowed=False)
    G.add_edge("n_t3_exit", "n_t4_brake", length=250, radius=None, x_mode_allowed=False)
    G.add_edge("n_t4_brake", "n_t4_apex", length=120, radius=75, x_mode_allowed=False)
    G.add_edge("n_t4_apex", "n_t5_entry", length=300, radius=None, x_mode_allowed=True)
    G.add_edge("n_t5_entry", "n_t7_apex", length=450, radius=150, x_mode_allowed=False)
    G.add_edge("n_t7_apex", "n_t8_brake", length=150, radius=None, x_mode_allowed=False)
    G.add_edge("n_t8_brake", "n_t8_apex", length=100, radius=55, x_mode_allowed=False)
    G.add_edge("n_t8_apex", "n_t9_entry", length=200, radius=None, x_mode_allowed=False)
    G.add_edge("n_t9_entry", "n_t10_apex", length=200, radius=50, x_mode_allowed=False)
    G.add_edge("n_t10_apex", "n_t11_brake", length=700, radius=None, x_mode_allowed=True, mom_detection=True)
    G.add_edge("n_t11_brake", "n_t11_apex", length=150, radius=80, x_mode_allowed=False)
    G.add_edge("n_t11_apex", "n_t12_apex", length=200, radius=160, x_mode_allowed=False)
    G.add_edge("n_t12_apex", "n_t13_brake", length=600, radius=None, x_mode_allowed=True, mom_detection=True)
    G.add_edge("n_t13_brake", "n_t13_apex", length=120, radius=65, x_mode_allowed=False)
    G.add_edge("n_t13_apex", "n_t14_brake", length=300, radius=None, x_mode_allowed=False)
    G.add_edge("n_t14_brake", "n_t15_apex", length=150, radius=70, x_mode_allowed=False)
    return G

# -------------------------
# Snapshot writer (no replace)
# -------------------------
def write_simulation_data_snapshot_mode(data, folder=".", prefix="data_snapshot_", keep_last=12):
    """
    Write JSON snapshot files (timestamped) and prune older ones.
    Returns the path written or None on failure.
    """
    try:
        os.makedirs(folder, exist_ok=True)
    except Exception:
        pass

    ts = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    fname = f"{prefix}{ts}.json"
    path = os.path.join(folder, fname)

    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        print(f"Error writing snapshot file {path}: {e}")
        return None

    # prune older snapshots
    try:
        pattern = os.path.join(folder, f"{prefix}*.json")
        files = sorted(glob.glob(pattern), key=os.path.getmtime, reverse=True)
        for old in files[keep_last:]:
            try:
                os.remove(old)
            except Exception:
                pass
    except Exception:
        pass

    return os.path.abspath(path)

# -------------------------
# 2. IO Utilities (snapshot mode)
# -------------------------
def read_command(file_path="commands.json"):
    if not os.path.exists(file_path):
        return None
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            command_data = json.load(f)
        try:
            os.remove(file_path)
        except Exception:
            pass
        return command_data
    except Exception as e:
        print(f"Error reading command: {e}")
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
            except Exception:
                pass
        return None

# -------------------------
# 3. Initial Data (22 cars)
# -------------------------
def get_initial_data(pos):
    """
    Creates a full 22-car grid with 'Elite+' data fields.
    For Task 5 manual test we set:
      - Verstappen.status = "CRASHED"
      - Hamilton.status   = "PITTING"
      - Norris.vehicle_state.on_cliff = True
      - Piastri.vehicle_state.mom_active = True
    """
    start_pos = list(pos["n_t15_apex"])

    haas_drivers = ["Ocon", "Bearman"]
    other_drivers = [
        "Verstappen", "Perez", "Hamilton", "Russell", "Leclerc", "Sainz",
        "Norris", "Piastri", "Alonso", "Stroll", "Gasly", "Tsunoda",
        "Ricciardo", "Albon", "Sargeant", "Bottas", "Zhou", "Magnussen", "Hulkenberg",
        "Lawson", "Drugovich"
    ]
    all_driver_ids = haas_drivers + other_drivers

    agents_list = []
    for i, driver_id in enumerate(all_driver_ids):
        current_start_pos = [start_pos[0] + (i % 2) * 20, start_pos[1] + (i // 2) * 20]

        # base vehicle_state
        vehicle_state = {
            "battery_soc": float(np.random.uniform(0.85, 0.95)),
            "aero_mode": "Z-MODE",
            "mom_available": False,
            "fuel_remaining_mj": 3000.0,
            "tyre_compound": "medium",
            "tyre_life": 1.0,
            "on_cliff": False,
            "mom_active": False,
            "pit_stops_made": 0
        }

        # Default status
        status = "RACING"

        # TEST INJECTION FOR TASK 5:
        if driver_id == "Verstappen":
            status = "CRASHED"
        elif driver_id == "Hamilton":
            status = "PITTING"
        elif driver_id == "Norris":
            vehicle_state["on_cliff"] = True
        elif driver_id == "Piastri":
            vehicle_state["mom_active"] = True

        agents_list.append({
            "id": driver_id,
            "team": "Haas" if driver_id in haas_drivers else "AI_Team",
            "rank": i + 1,
            "position": current_start_pos,
            "status": status,
            "lap_data": {
                "current_lap": 1,
                "last_lap_time": "0:00.000",
                "fastest_lap_time": "0:00.000"
            },
            "vehicle_state": vehicle_state
        })

    return {
        "race_status": {"timestamp": "0:00:00.0", "current_lap": 1, "total_laps": 57, "safety_car": "NONE"},
        "agents": agents_list
    }


# -------------------------
# 4. Sorting key
# -------------------------
def get_sort_key(agent):
    lap = agent.get('lap_data', {}).get('current_lap', 0)
    last_time_str = agent.get('lap_data', {}).get('last_lap_time', None)
    last_time = parse_time_to_seconds(last_time_str)
    if last_time is None:
        last_time = 9999.0
    return (lap * 100000.0) - last_time

# -------------------------
# 5. Path & Server Loop
# -------------------------
BAHRAIN_PATH = [
    "n_t15_apex", "n_t1_brake", "n_t1_apex", "n_t2_apex", "n_t3_exit",
    "n_t4_brake", "n_t4_apex", "n_t5_entry", "n_t7_apex", "n_t8_brake",
    "n_t8_apex", "n_t9_entry", "n_t10_apex", "n_t11_brake", "n_t11_apex",
    "n_t12_apex", "n_t13_brake", "n_t13_apex", "n_t14_brake"
]

BASE_DRAIN_RATE = 0.008
BASE_REGEN_RATE = 0.005
SPEED_FAST = 0.020
SPEED_MEDIUM = 0.012
SPEED_SLOW = 0.008
MOM_DETECTION_DISTANCE = 75

def run_fake_server(G):
    pos = nx.get_node_attributes(G, 'pos')
    data = get_initial_data(pos)

    agent_states = {}
    lap_times = {}
    now = time.time()

    for agent in data['agents']:
        agent_id = agent['id']
        agent_states[agent_id] = {
            "path_index": 0,
            "progress": 0.0,
            "speed_factor": float(np.random.uniform(0.95, 1.05))
        }
        lap_times[agent_id] = now

    start_time = now

    print("--- FAKE DATA SERVER (SNAPSHOT MODE, 22 CARS) STARTED ---")

    while True:
        current_time = time.time()
        elapsed_time = current_time - start_time
        data['race_status']['timestamp'] = format_seconds_to_str(elapsed_time)

        command = read_command()
        if command:
            print(f"RECEIVED COMMAND: {command}")
            cmd = command.get('command')
            agent_id = command.get('agent')
            for agent_data in data['agents']:
                if agent_data['id'] == agent_id:
                    if cmd == "toggle_mom":
                        agent_data['vehicle_state']['mom_available'] = not agent_data['vehicle_state']['mom_available']
                    elif cmd == "toggle_aero":
                        v_state = agent_data['vehicle_state']
                        v_state['aero_mode'] = "X-MODE" if v_state['aero_mode'] == "Z-MODE" else "Z-MODE"

        for agent_data in data['agents']:
            agent_id = agent_data['id']
            state = agent_states[agent_id]

            current_node_name = BAHRAIN_PATH[state['path_index']]
            next_node_index = (state['path_index'] + 1) % len(BAHRAIN_PATH)
            next_node_name = BAHRAIN_PATH[next_node_index]
            edge_data = G.edges[current_node_name, next_node_name]

            current_speed = SPEED_SLOW
            radius = edge_data.get('radius')
            if radius is None:
                current_speed = SPEED_FAST
            elif radius > 100:
                current_speed = SPEED_MEDIUM

            state['progress'] += (current_speed * state['speed_factor'])

            if state['progress'] >= 1.0:
                if edge_data.get('is_finish_line'):
                    lap_time = current_time - lap_times[agent_id]
                    lap_times[agent_id] = current_time
                    agent_data['lap_data']['last_lap_time'] = format_seconds_to_str(lap_time)
                    agent_data['lap_data']['current_lap'] += 1
                    data['race_status']['current_lap'] = agent_data['lap_data']['current_lap']

                    fastest_str = agent_data['lap_data'].get('fastest_lap_time', None)
                    fastest_val = parse_time_to_seconds(fastest_str)
                    if (fastest_val is None) or (fastest_val == 0.0) or (lap_time < fastest_val):
                        agent_data['lap_data']['fastest_lap_time'] = format_seconds_to_str(lap_time)

                state['path_index'] = next_node_index
                state['progress'] = 0.0
                current_node_name = BAHRAIN_PATH[state['path_index']]
                next_node_index = (state['path_index'] + 1) % len(BAHRAIN_PATH)
                next_node_name = BAHRAIN_PATH[next_node_index]
                edge_data = G.edges[current_node_name, next_node_name]

            start_pos = np.array(pos[current_node_name])
            end_pos = np.array(pos[next_node_name])
            new_pos = start_pos + (end_pos - start_pos) * state['progress']
            agent_data['position'] = new_pos.tolist()

            v_state = agent_data['vehicle_state']
            if edge_data.get('x_mode_allowed'):
                v_state['aero_mode'] = "X-MODE"
                drain = BASE_DRAIN_RATE * (current_speed / SPEED_FAST)
                v_state['battery_soc'] = max(0.0, v_state['battery_soc'] - drain)
            else:
                v_state['aero_mode'] = "Z-MODE"
                regen = BASE_REGEN_RATE * (1.0 - (current_speed / SPEED_MEDIUM))
                v_state['battery_soc'] = min(1.0, v_state['battery_soc'] + regen)

        data['agents'].sort(key=get_sort_key, reverse=True)
        for i, agent in enumerate(data['agents']):
            agent['rank'] = i + 1

        # Write snapshot (no replace)
        written = write_simulation_data_snapshot_mode(data, folder=".", prefix="data_snapshot_", keep_last=12)
        # optional debug:
        # if written is None:
        #     print("Snapshot write failed")

        time.sleep(0.01)

# -------------------------
# 6. entrypoint
# -------------------------
if __name__ == '__main__':
    try:
        os.chdir(os.path.dirname(os.path.abspath(__file__)))

        if 'numpy' not in sys.modules: raise ImportError("NumPy not found")
        if 'networkx' not in sys.modules: raise ImportError("NetworkX not found")

        G = build_bahrain_track()
        run_fake_server(G)

    except ImportError as e:
        print(f"FATAL ERROR: {e}. Please ensure libraries are installed in your venv.")
    except KeyError as e:
        print(f"FATAL ERROR: A node key was wrong. Check your BAHRAIN_PATH. Error: {e}")
    except Exception as e:
        print(f"An unexpected error occurred in the data writer: {e}")
        print("Stopping server.")
