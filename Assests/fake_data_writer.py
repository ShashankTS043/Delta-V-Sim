import networkx as nx
import json
import time
import numpy as np
import sys
import os
import re

# -------------------------
# Helper: time parsing / formatting
# -------------------------
def parse_time_to_seconds(t):
    """
    Parse a time string into seconds (float).
    Accepts:
      - "12.345"           -> interpreted as seconds (float)
      - "MM:SS.mmm"        -> minutes:seconds.milliseconds
      - "H:MM:SS.mmm"      -> hours:minutes:seconds.milliseconds
    Returns:
      - float seconds on success
      - None if cannot parse
    """
    if t is None:
        return None
    # If it's already a simple numeric string
    try:
        return float(str(t))
    except (ValueError, TypeError):
        pass

    # Try splitting by ":" to handle mm:ss.mmm or h:mm:ss.mmm
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
    """Format float seconds into 'M:SS.mmm' if >= 60 else 'S.mmm'"""
    if s is None:
        return "0:00.000"
    try:
        s = float(s)
    except (ValueError, TypeError):
        return "0:00.000"
    minutes = int(s // 60)
    seconds = s - minutes*60
    return f"{minutes}:{seconds:06.3f}"  # mm:ss.mmm (minutes can be 0)

# -------------------------
# 1. HIGH-FIDELITY TRACK DEFINITION
# -------------------------
import networkx as nx

def build_bahrain_track():
    """
    Creates a high-fidelity, physics-based graph of the Bahrain F1 circuit.
    This version uses visually accurate (x, y) coordinates for the visualizer.
    """
    G = nx.DiGraph() 

    # --- Node Definitions (NEW Visually Accurate Coords) ---
    G.add_node("n_t15_apex", pos=(800, 700))   # T15 Apex (Start of main straight)
    G.add_node("n_t1_brake", pos=(800, 150))   # T1 Braking Zone
    G.add_node("n_t1_apex", pos=(770, 100))    # T1 Apex
    G.add_node("n_t2_apex", pos=(700, 150))    # T2 Apex
    G.add_node("n_t3_exit", pos=(700, 200))    # T3 Exit
    G.add_node("n_t4_brake", pos=(650, 350))   # T4 Braking Zone
    G.add_node("n_t4_apex", pos=(610, 380))    # T4 Apex
    G.add_node("n_t5_entry", pos=(400, 380))   # T5/T6 Entry
    G.add_node("n_t7_apex", pos=(350, 420))    # T7 Apex
    G.add_node("n_t8_brake", pos=(300, 380))   # T8 Braking
    G.add_node("n_t8_apex", pos=(270, 350))    # T8 Apex
    G.add_node("n_t9_entry", pos=(200, 420))   # T9/T10 Entry
    G.add_node("n_t10_apex", pos=(150, 400))   # T10 Apex
    G.add_node("n_t11_brake", pos=(150, 650))  # T11 Braking
    G.add_node("n_t11_apex", pos=(180, 700))   # T11 Apex
    G.add_node("n_t12_apex", pos=(250, 750))   # T12 Apex (fast sweeper)
    G.add_node("n_t13_brake", pos=(500, 750))  # T13 Braking
    G.add_node("n_t13_apex", pos=(550, 780))   # T13 Apex
    G.add_node("n_t14_brake", pos=(750, 780))  # T14 Braking
    # T15 Apex is the same as the start of the straight

    # --- Edge Definitions (Track Segments) ---
    # (No changes to this logic, only the node names)
    
    # 1. Main Straight (T15 to T1)
    G.add_edge("n_t15_apex", "n_t1_brake", 
               length=1100, 
               radius=None, 
               x_mode_allowed=True,
               mom_detection=True,
               is_finish_line=True) # This edge IS the finish line

    # 2. T1/T2/T3 Complex
    G.add_edge("n_t1_brake", "n_t1_apex", length=110, radius=60, x_mode_allowed=False)
    G.add_edge("n_t1_apex", "n_t2_apex", length=100, radius=70, x_mode_allowed=False)
    G.add_edge("n_t2_apex", "n_t3_exit", length=100, radius=70, x_mode_allowed=False)
    
    # 3. Straight to T4
    G.add_edge("n_t3_exit", "n_t4_brake", length=250, radius=None, x_mode_allowed=False)
    
    # 4. T4
    G.add_edge("n_t4_brake", "n_t4_apex", length=120, radius=75, x_mode_allowed=False)
    
    # 5. Straight to T5
    G.add_edge("n_t4_apex", "n_t5_entry", length=300, radius=None, x_mode_allowed=True)
    
    # 6. T5/T6/T7 (Fast Sweepers)
    G.add_edge("n_t5_entry", "n_t7_apex", length=450, radius=150, x_mode_allowed=False)
    
    # 7. Short straight to T8
    G.add_edge("n_t7_apex", "n_t8_brake", length=150, radius=None, x_mode_allowed=False)
    
    # 8. T8
    G.add_edge("n_t8_brake", "n_t8_apex", length=100, radius=55, x_mode_allowed=False)
    
    # 9. T9/T10 (The Infield)
    G.add_edge("n_t8_apex", "n_t9_entry", length=200, radius=None, x_mode_allowed=False)
    G.add_edge("n_t9_entry", "n_t10_apex", length=200, radius=50, x_mode_allowed=False) # Tight
    
    # 10. Straight to T11
    G.add_edge("n_t10_apex", "n_t11_brake", length=700, radius=None, x_mode_allowed=True, mom_detection=True)
    
    # 11. T11/T12
    G.add_edge("n_t11_brake", "n_t11_apex", length=150, radius=80, x_mode_allowed=False)
    G.add_edge("n_t11_apex", "n_t12_apex", length=200, radius=160, x_mode_allowed=False) # Fast
    
    # 12. Back Straight
    G.add_edge("n_t12_apex", "n_t13_brake", length=600, radius=None, x_mode_allowed=True, mom_detection=True)
    
    # 13. T13
    G.add_edge("n_t13_brake", "n_t13_apex", length=120, radius=65, x_mode_allowed=False)
    
    # 14. T14
    G.add_edge("n_t13_apex", "n_t14_brake", length=300, radius=None, x_mode_allowed=False)
    G.add_edge("n_t14_brake", "n_t15_apex", length=150, radius=70, x_mode_allowed=False)
               
    return G

# -------------------------
# 2. IO Utilities
# -------------------------
def write_simulation_data(data, file_path="data.json"):
    with open(file_path, 'w') as f:
        json.dump(data, f, indent=2)

def read_command(file_path="commands.json"):
    if not os.path.exists(file_path):
        return None
    try:
        with open(file_path, 'r') as f:
            command_data = json.load(f)
        os.remove(file_path)
        return command_data
    except Exception as e:
        print(f"Error reading command: {e}")
        if os.path.exists(file_path):
            os.remove(file_path)
        return None

# -------------------------
# 3. Initial Data
# -------------------------
def get_initial_data(pos):
    start_pos = list(pos["n_t15_apex"])
    return {
      "race_status": {"timestamp": "0:00:00.0", "current_lap": 1, "total_laps": 57, "safety_car": "NONE"},
      "agents": [
        {
          "id": "Ocon_2026", "team": "Haas", "rank": 1, "position": start_pos, "status": "RACING",
          "lap_data": {"current_lap": 1, "last_lap_time": "0:00.000", "fastest_lap_time": "0:00.000"},
          "vehicle_state": {"battery_soc": 0.95, "aero_mode": "Z-MODE", "mom_available": False}
        },
        {
          "id": "Bearman_2026", "team": "Haas", "rank": 2, "position": [start_pos[0], start_pos[1] + 20],
          "status": "RACING",
          "lap_data": {"current_lap": 1, "last_lap_time": "0:00.000", "fastest_lap_time": "0:00.000"},
          "vehicle_state": {"battery_soc": 0.85, "aero_mode": "Z-MODE", "mom_available": True}
        }
      ]
    }

# -------------------------
# 4. Sorting key (robust)
# -------------------------
def get_sort_key(agent):
    """
    Higher lap is better; for same lap, lower last_lap_time is better.
    We return a numeric key where larger is better (for reverse=True sorting).
    """
    lap = agent.get('lap_data', {}).get('current_lap', 0)
    last_time_str = agent.get('lap_data', {}).get('last_lap_time', None)
    last_time = parse_time_to_seconds(last_time_str)
    if last_time is None:
        last_time = 9999.0
    # Make lap dominate by scaling
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

def run_fake_server(G):
    pos = nx.get_node_attributes(G, 'pos')
    data = get_initial_data(pos)

    # State variables use path_index
    agent_states = {
        "Ocon_2026": {"path_index": 0, "progress": 0.0, "speed": 0.015, "soc_drain": 0.0005},
        "Bearman_2026": {"path_index": 0, "progress": 0.0, "speed": 0.012, "soc_drain": 0.0004},
    }

    # Initialize lap_times to now so first lap deltas are reasonable
    now = time.time()
    lap_times = {"Ocon_2026": now, "Bearman_2026": now}
    start_time = now

    print("--- FAKE DATA SERVER (HI-FI MODEL) STARTED ---")

    while True:
        current_time = time.time()
        elapsed_time = current_time - start_time
        # Format timestamp as M:SS.mmm
        data['race_status']['timestamp'] = format_seconds_to_str(elapsed_time)

        # Command listener (external commands via commands.json)
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

            # Movement → progress along segment
            state['progress'] += state['speed']

            current_node_name = BAHRAIN_PATH[state['path_index']]
            next_node_index = (state['path_index'] + 1) % len(BAHRAIN_PATH)
            next_node_name = BAHRAIN_PATH[next_node_index]

            if state['progress'] >= 1.0:
                # Completed edge: check finish-line
                edge_data = G.edges[current_node_name, next_node_name]
                if edge_data.get('is_finish_line'):
                    # compute lap_time in seconds
                    lap_time = current_time - lap_times[agent_id]
                    lap_times[agent_id] = current_time
                    agent_data['lap_data']['last_lap_time'] = f"{lap_time:.3f}"
                    agent_data['lap_data']['current_lap'] += 1
                    data['race_status']['current_lap'] = agent_data['lap_data']['current_lap']

                    # Update fastest lap robustly
                    fastest_str = agent_data['lap_data'].get('fastest_lap_time', None)
                    fastest_val = parse_time_to_seconds(fastest_str)
                    # If fastest_val is None or zero or larger than new lap_time -> update
                    if (fastest_val is None) or (fastest_val == 0.0) or (lap_time < fastest_val):
                        agent_data['lap_data']['fastest_lap_time'] = f"{lap_time:.3f}"

                # advance path index and reset progress
                state['path_index'] = next_node_index
                state['progress'] = 0.0

                # recalc node names after advance
                current_node_name = BAHRAIN_PATH[state['path_index']]
                next_node_index = (state['path_index'] + 1) % len(BAHRAIN_PATH)
                next_node_name = BAHRAIN_PATH[next_node_index]

            # Interpolate position
            start_pos = np.array(pos[current_node_name])
            end_pos = np.array(pos[next_node_name])
            new_pos = start_pos + (end_pos - start_pos) * state['progress']
            agent_data['position'] = new_pos.tolist()

            # Strategic energy/aero
            edge_data = G.edges[current_node_name, next_node_name]
            if edge_data.get('x_mode_allowed'):
                agent_data['vehicle_state']['aero_mode'] = "X-MODE"
                agent_data['vehicle_state']['battery_soc'] = max(0.0, agent_data['vehicle_state']['battery_soc'] - state['soc_drain'])
            else:
                agent_data['vehicle_state']['aero_mode'] = "Z-MODE"
                agent_data['vehicle_state']['battery_soc'] = min(1.0, agent_data['vehicle_state']['battery_soc'] + state['soc_drain'] * 0.8)

        # Sort & update ranks using robust key
        data['agents'].sort(key=get_sort_key, reverse=True)
        for i, agent in enumerate(data['agents']):
            agent['rank'] = i + 1

        # Write file and sleep
        write_simulation_data(data)
        time.sleep(0.01)

# -------------------------
# 6. entrypoint
# -------------------------
if __name__ == '__main__':
    try:
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
