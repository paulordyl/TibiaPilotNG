# scripts/run_random_agent.py
import random
import time
import sys
import os

# Adjust sys.path to allow importing from src
# Assuming this script is in 'scripts/' and 'src/' is a sibling directory
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.insert(0, project_root)

from src.ai.agent_interface import AgentInterface

def run_random_agent():
    """
    Runs a simple agent that performs random actions using AgentInterface.
    """
    print("Initializing Random Agent...")
    try:
        agent = AgentInterface()
        print(f"Agent initialized. Screen dimensions: W={agent.screen_width} H={agent.screen_height} L={agent.screen_left} T={agent.screen_top}")
        print("Starting random actions in 3 seconds... Press Ctrl+C to exit.")
        time.sleep(3)

        action_counter = 0
        while True:
            action_counter += 1
            print(f"--- Action #{action_counter} ---")

            # 1. Get screen observation (optional to use the frame for this random agent)
            # frame = agent.get_current_frame()
            # print(f"Captured frame with shape: {frame.shape}") # Can be verbose

            # 2. Random Action Selection
            action_type = random.choice(['click', 'type', 'press_key', 'drag'])

            if action_type == 'click':
                x_pct = random.uniform(0.05, 0.95) # Avoid extreme edges
                y_pct = random.uniform(0.05, 0.95)
                button_type = random.choice(['left', 'right'])
                print(f"Action: Clicking {button_type} at ({x_pct:.2f}, {y_pct:.2f})% of primary monitor")
                agent.click(x_pct, y_pct, raw_pixels=False, button=button_type)

            elif action_type == 'type':
                random_text = "".join(random.choices("abcdefghijklmnopqrstuvwxyz ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789", k=random.randint(5, 15)))
                print(f"Action: Typing '{random_text}'")
                agent.type_string(random_text)
                # Optionally follow with an enter press sometimes
                if random.random() < 0.3: # 30% chance to press enter after typing
                    time.sleep(random.uniform(0.1, 0.3)) # Small pause
                    print("Action: Pressing Enter")
                    agent.press_key('enter')

            elif action_type == 'drag':
                x1_pct = random.uniform(0.05, 0.95)
                y1_pct = random.uniform(0.05, 0.95)
                x2_pct = random.uniform(0.05, 0.95)
                y2_pct = random.uniform(0.05, 0.95)
                print(f"Action: Dragging from ({x1_pct:.2f},{y1_pct:.2f})% to ({x2_pct:.2f},{y2_pct:.2f})% of primary monitor")
                agent.drag(x1_pct, y1_pct, x2_pct, y2_pct, raw_pixels=False)

            elif action_type == 'press_key':
                # More diverse set of keys
                keys_to_choose = ['space', 'esc', 'f1', 'f5', 'tab', 'a', 's', 'd', 'w', 'up', 'down', 'left', 'right', 'enter', 'shift']
                key_to_press = random.choice(keys_to_choose)
                print(f"Action: Pressing key '{key_to_press}'")
                agent.press_key(key_to_press)

            # 3. Pause between actions
            sleep_duration = random.uniform(1.0, 3.0) # Adjusted for slightly longer pauses
            print(f"Sleeping for {sleep_duration:.2f} seconds...")
            time.sleep(sleep_duration)

    except KeyboardInterrupt:
        print("\nRandom agent stopped by user.")
    except ImportError as e:
        print(f"Error: Failed to import necessary modules. Make sure src is in PYTHONPATH.")
        print(f"Details: {e}")
        print(f"Current sys.path: {sys.path}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == '__main__':
    run_random_agent()
