import pygame
import sys
import json
import networkx as nx
import os

# --- 1. PYGAME & FONT INITIALIZATION ---
pygame.init()
pygame.font.init()

# --- 2. SCREEN & COLOR DEFINITIONS ---
SCREEN_WIDTH = 1200  # Adjusted for new map layout
SCREEN_HEIGHT = 700
SCREEN = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Aether F1 2026 Simulator (VISUALIZER) - High-Fidelity Track")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 25, 25)
BLUE = (0, 100, 255)
YELLOW = (255, 255, 0)
GREEN = (0, 255, 50)
GREY = (100, 100, 100)
CYAN = (0, 255, 255)
DARK_BLUE = (0, 0, 150)
TRACK_COLOR = (200, 200, 200)

# Agent Visuals
AGENT_RADIUS = 8
AGENT_COLORS = {
    'Ocon_2026': BLUE,
    'Bearman_2026': RED,
    'AI_Agent_3': (150, 0, 200) # Purple for AI
}

# Fonts
try:
    FONT_HUD = pygame.font.Font(None, 24)
    FONT_BUTTON = pygame.font.Font(None, 22)
    FONT_AGENT = pygame.font.Font(None, 20)
except Exception:
    FONT_HUD = pygame.font.SysFont('Arial', 22)
    FONT_BUTTON = pygame.font.SysFont('Arial', 20)
    FONT_AGENT = pygame.font.SysFont('Arial', 18)

# --- 3. GOD-MODE BUTTON DEFINITIONS ---
BUTTON_COLOR = (50, 50, 50)
BUTTON_TEXT_COLOR = (255, 255, 255)
MOM_BUTTON_RECT = pygame.Rect(940, 50, 250, 40)
AERO_BUTTON_RECT = pygame.Rect(940, 100, 250, 40)

# --- 4. NEW HIGH-FIDELITY TRACK DEFINITION ---
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

# --- 5. JSON FILE I/O (COMMUNICATION) ---
# (These functions are unchanged)
def load_simulation_data(file_path="data.json"):
    """Tries to read the data.json file."""
    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {"race_status": {}, "agents": []}
    except json.JSONDecodeError:
        return {"race_status": {}, "agents": []}

def write_command(command, agent_id, file_path="commands.json"):
    """Writes a command to the commands.json file for the backend to read."""
    command_data = {"command": command, "agent": agent_id}
    try:
        with open(file_path, 'w') as f:
            json.dump(command_data, f)
    except Exception as e:
        print(f"Error writing command file: {e}")

# --- 6. DRAWING FUNCTIONS ---
# (These functions are unchanged. They are smart enough to read the new graph.)

def draw_track(graph, pos_dict):
    """Draws the track graph (edges and nodes)."""
    # Draw Edges
    for u, v, data in graph.edges(data=True):
        color = YELLOW if data.get('x_mode_allowed') else TRACK_COLOR
        pygame.draw.line(SCREEN, color, pos_dict[u], pos_dict[v], 5)
    
    # Draw Nodes (Waypoints)
    for node_id, coordinates in pos_dict.items():
        pygame.draw.circle(SCREEN, DARK_BLUE, coordinates, 10)
        # Optional: Draw node names (can get cluttered, but good for debug)
        # text = FONT_AGENT.render(str(node_id), True, WHITE)
        # SCREEN.blit(text, (coordinates[0] + 12, coordinates[1] + 12))

def draw_agents(agents_data):
    """Draws all agents and their status indicators."""
    for agent in agents_data:
        try:
            agent_id = agent.get('id', 'Unknown')
            x = int(agent['position'][0])
            y = int(agent['position'][1])
            color = AGENT_COLORS.get(agent_id, GREY)

            v_state = agent['vehicle_state']
            
            # 1. Draw the Agent Dot
            pygame.draw.circle(SCREEN, color, (x, y), AGENT_RADIUS)
            
            # 2. X-Mode Indicator (Low Drag)
            if v_state.get('aero_mode') == "X-MODE":
                pygame.draw.circle(SCREEN, GREEN, (x, y), AGENT_RADIUS + 3, 2)
                
            # 3. MOM Indicator (Overtake Available)
            if v_state.get('mom_available'):
                mom_color = RED if (pygame.time.get_ticks() // 200) % 2 else WHITE
                pygame.draw.circle(SCREEN, mom_color, (x, y), AGENT_RADIUS + 1, 1)

            # 4. Draw Name & Battery SOC
            name_text = FONT_AGENT.render(agent_id.split('_')[0], True, WHITE)
            SCREEN.blit(name_text, (x + AGENT_RADIUS + 2, y - AGENT_RADIUS))
            
            soc_text = FONT_AGENT.render(f"SOC: {v_state.get('battery_soc', 0):.0%}", True, WHITE)
            SCREEN.blit(soc_text, (x + AGENT_RADIUS + 2, y + AGENT_RADIUS - 8))
        
        except (IndexError, TypeError, KeyError):
            pass # Skip drawing corrupted agent data

def draw_status_hud(sim_data):
    """Draws the main leaderboard and race status HUD."""
    font = FONT_HUD
    x_pos = 10 # HUD on the left
    y_offset = 20
    
    # 1. Global Race Status
    r_status = sim_data.get('race_status', {})
    status_lines = [
        f"AETHER 2026 (HI-FI MODEL)",
        f"TIME: {r_status.get('timestamp', '0:00:00.0')}",
        f"LAP: {r_status.get('current_lap', 0)} / {r_status.get('total_laps', 0)}",
        f"SAFETY CAR: {r_status.get('safety_car', 'NONE')}"
    ]
    for line in status_lines:
        SCREEN.blit(font.render(line, True, CYAN), (x_pos, y_offset))
        y_offset += 25
    
    # 2. Agent Leaderboard
    y_offset += 20
    SCREEN.blit(font.render("--- LIVE 2026 LEADERBOARD ---", True, CYAN), (x_pos, y_offset))
    y_offset += 30
    header_text = font.render("R | ID       | Last Lap   | SOC | AERO | MOM", True, GREY)
    SCREEN.blit(header_text, (x_pos, y_offset))
    y_offset += 25

    agents = sim_data.get('agents', [])
    agents.sort(key=lambda a: a.get('rank', 99))
    
    for agent in agents:
        try:
            v_state = agent['vehicle_state']
            l_data = agent['lap_data']
            aero = v_state.get('aero_mode', 'N/A').replace("-MODE", "")
            mom = 'YES' if v_state.get('mom_available') else 'NO'
            rank = agent.get('rank', '-')
            agent_id = agent.get('id', 'N/A').split('_')[0]
            last_lap = l_data.get('last_lap_time', '0:00.000')
            soc = v_state.get('battery_soc', 0)
            
            line = f"{rank:<2} | {agent_id:<8} | {last_lap:<10} | {soc:<4.0%} | {aero:<4} | {mom:<3}"
            text_color = GREEN if rank == 1 else WHITE
            SCREEN.blit(font.render(line, True, text_color), (x_pos, y_offset))
            y_offset += 25
        except Exception:
            pass # Skip drawing this agent if data is malformed

def draw_god_mode_buttons():
    """Draws the interactive buttons."""
    pygame.draw.rect(SCREEN, BUTTON_COLOR, MOM_BUTTON_RECT)
    mom_text = FONT_BUTTON.render("TOGGLE MOM [BEARMAN]", True, BUTTON_TEXT_COLOR)
    SCREEN.blit(mom_text, (MOM_BUTTON_RECT.x + 10, MOM_BUTTON_RECT.y + 10))

    pygame.draw.rect(SCREEN, BUTTON_COLOR, AERO_BUTTON_RECT)
    aero_text = FONT_BUTTON.render("TOGGLE AERO [OCON]", True, BUTTON_TEXT_COLOR)
    SCREEN.blit(aero_text, (AERO_BUTTON_RECT.x + 10, AERO_BUTTON_RECT.y + 10))


# --- 7. MAIN GAME LOOP ---

def run_demo():
    running = True
    clock = pygame.time.Clock() 
    
    # Load track graph and positions ONE time
    track_graph = build_bahrain_track()
    track_positions = nx.get_node_attributes(track_graph, 'pos')

    while running:
        # --- EVENT HANDLING (Input) ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                if MOM_BUTTON_RECT.collidepoint(event.pos):
                    print("CLICK: TOGGLE MOM [BEARMAN]")
                    write_command(command="toggle_mom", agent_id="Bearman_2026")
                    
                if AERO_BUTTON_RECT.collidepoint(event.pos):
                    print("CLICK: TOGGLE AERO [OCON]")
                    write_command(command="toggle_aero", agent_id="Ocon_2026")

        # --- DATA LOADING (State Update) ---
        sim_data = load_simulation_data()
        agents_data = sim_data.get('agents', [])

        # --- DRAWING (Render) ---
        SCREEN.fill(BLACK)
        draw_track(track_graph, track_positions)
        draw_status_hud(sim_data)
        draw_god_mode_buttons()
        draw_agents(agents_data) 
        pygame.display.flip()
        
        clock.tick(60) # Cap at 60 FPS

    pygame.quit()
    sys.exit()

if __name__ == '__main__':
    run_demo()