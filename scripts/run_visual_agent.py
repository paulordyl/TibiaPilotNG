# scripts/run_visual_agent.py
import random
import time
import sys
import os
import numpy as np # For HSV color ranges (still needed for TARGET_COLORS)
# import cv2 # cv2 is used within simple_image_analyzer, not directly here.

# Adjust sys.path to allow importing from src
# Assuming this script is in 'scripts/' and 'src/' is a sibling directory
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.insert(0, project_root)

from src.ai.agent_interface import AgentInterface
from src.utils.simple_image_analyzer import find_largest_object_by_hsv # UPDATED
from src.utils.color_configs import TARGET_COLORS # ADDED

def run_visual_agent():
    print("Initializing Visual Agent...")
    try:
        agent = AgentInterface()
        # AgentInterface __init__ already prints screen dimensions if not default.
        # print(f"Agent initialized. Screen dimensions: W={agent.screen_width} H={agent.screen_height} (Left:{agent.screen_left}, Top:{agent.screen_top})")

        target_color_name = "red"  # Easily change this to "blue", "green", etc.
        hsv_ranges_for_target = TARGET_COLORS.get(target_color_name.lower())

        if hsv_ranges_for_target is None:
            print(f"Error: Color '{target_color_name}' not found in TARGET_COLORS. Exiting.")
            return

        print(f"Visual agent starting in 3 seconds... Press Ctrl+C to exit.")
        print(f"Agent will look for {target_color_name.upper()} areas and click them.")
        print(f"If no {target_color_name.upper()} area is found, it will perform a random click.")
        time.sleep(3)

        action_counter = 0
        min_detection_area = 100 # Minimum pixel area to consider a detection valid

        while True:
            action_counter += 1
            print(f"--- Cycle #{action_counter} ---")

            frame = agent.get_current_frame()
            if frame is None or frame.size == 0:
                print("Error: Failed to capture frame. Skipping cycle.")
                time.sleep(1)
                continue

            # print(f"Captured frame with shape: {frame.shape}") # Optional: for debugging

            # Use the new generalized function and color configs
            target_coords = find_largest_object_by_hsv(frame, hsv_ranges_for_target, min_detection_area)

            if target_coords:
                click_x = agent.screen_left + target_coords[0]
                click_y = agent.screen_top + target_coords[1]

                print(f"Action: {target_color_name.capitalize()} area found at ({target_coords[0]},{target_coords[1]}) relative to primary monitor. Clicking global ({click_x},{click_y}).")
                agent.click(click_x, click_y, raw_pixels=True, button='left')
            else:
                x_pct = random.uniform(0.1, 0.9)
                y_pct = random.uniform(0.1, 0.9)
                print(f"Action: No {target_color_name.upper()} area found. Random click at ({x_pct:.2f}, {y_pct:.2f})% of primary monitor.")
                agent.click(x_pct, y_pct, raw_pixels=False, button='left')

            sleep_duration = random.uniform(0.5, 1.5)
            print(f"Sleeping for {sleep_duration:.2f} seconds...")
            time.sleep(sleep_duration)

    except KeyboardInterrupt:
        print("\nVisual agent stopped by user.")
    except ImportError as e:
        print(f"Error: Failed to import necessary modules. Make sure src is in PYTHONPATH.")
        print(f"Details: {e}")
        print(f"Current sys.path: {sys.path}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == '__main__':
    run_visual_agent()
