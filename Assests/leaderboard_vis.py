import json
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import pandas as pd
import sys

# --- 1. DATA READER (Copied from pygame_vis.py) ---

def load_simulation_data(file_path="data.json"):
    """Tries to read the data.json file."""
    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print("Leaderboard: data.json not found. Waiting...")
        return {"agents": []} # Return a default structure
    except json.JSONDecodeError:
        print("Leaderboard: Error reading data.json. Skipping frame.")
        return {"agents": []} # File is being written, skip

# --- 2. MATPLOTLIB ANIMATION FUNCTION ---

# Create the figure and axes for the plot
fig, ax = plt.subplots()

def animate(i):
    """
    This function is called every 'interval' milliseconds.
    It reads the data, parses it with pandas, and redraws the bar chart.
    """
    
    # Load the simulation data
    data = load_simulation_data()
    agents = data.get('agents')

    if not agents:
        print("Leaderboard: No agent data to plot.")
        return

    try:
        # --- PANDAS MAGIC ---
        # Convert the complex JSON 'agents' list into a flat table (DataFrame)
        # This instantly gets data from 'vehicle_state.battery_soc'
        df = pd.json_normalize(agents)
        
        # We only care about a few columns
        df = df[['rank', 'id', 'vehicle_state.battery_soc']]
        
        # Sort by rank so #1 is at the top
        df = df.sort_values(by='rank', ascending=True)
        
        # --- PLOTTING ---
        ax.clear() # Clear the old bars
        
        # Create the horizontal bar chart
        # We plot 'id' on the y-axis and 'battery_soc' on the x-axis
        y_labels = df['id'].str.split('_').str[0] # Get 'Ocon' from 'Ocon_2026'
        x_values = df['vehicle_state.battery_soc'] * 100 # Convert 0.68 to 68
        
        bars = ax.barh(y_labels, x_values, color='cyan')
        
        # Invert y-axis so Rank 1 is at the top of the chart
        ax.invert_yaxis()
        
        # Add labels and title
        ax.set_title('Aether 2026: Live Battery SOC (%)')
        ax.set_xlabel('Battery State of Charge (%)')
        ax.set_xlim(0, 100) # Keep the X-axis fixed from 0 to 100
        
        # Add the numeric value labels to the end of each bar
        ax.bar_label(bars, fmt='%.1f%%')
        
        plt.tight_layout()

    except Exception as e:
        print(f"Error during plotting: {e}")

# --- 3. START THE ANIMATION ---

def run_leaderboard():
    print("--- LIVE LEADERBOARD (MATPLOTLIB) STARTED ---")
    print("--- This window will update every 1 second ---")
    
    # 'FuncAnimation' calls the 'animate' function every 1000 milliseconds (1 second)
    ani = animation.FuncAnimation(fig, animate, interval=1000)
    
    try:
        plt.show() # This opens the plot window
    except Exception as e:
        print(f"Matplotlib window closed or crashed: {e}")

if __name__ == '__main__':
    run_leaderboard()