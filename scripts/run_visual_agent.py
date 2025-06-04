# scripts/run_visual_agent.py
import random
import time
import sys
import os
import numpy as np # For HSV color ranges
# import cv2 # cv2 is used within simple_image_analyzer, not directly here.

# Adjust sys.path to allow importing from src
# Assuming this script is in 'scripts/' and 'src/' is a sibling directory
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.insert(0, project_root)

from src.ai.agent_interface import AgentInterface
from src.utils.simple_image_analyzer import find_largest_color_area

def run_visual_agent():
    print("Initializing Visual Agent...")
    try:
        agent = AgentInterface()
        # The __init__ of AgentInterface already prints dimensions, including L and T if not 0,0
        # print(f"Agent initialized. Screen dimensions: W={agent.screen_width} H={agent.screen_height} (Left:{agent.screen_left}, Top:{agent.screen_top})")
        print("Visual agent starting in 3 seconds... Press Ctrl+C to exit.")
        print("Agent will look for RED areas and click them.")
        print("If no red area is found, it will perform a random click.")
        time.sleep(3)

        action_counter = 0

        # Define HSV color range for RED
        # OpenCV Hue values are typically 0-179 for 8-bit images.
        # Range 1 (0-10 Hue, more vibrant reds)
        lower_red1 = np.array([0, 120, 70])    # Low H, Med S, Med V
        upper_red1 = np.array([10, 255, 255])   # High H, High S, High V

        # Range 2 (170-179 Hue for OpenCV's 0-179 H range, for reds that wrap around)
        lower_red2 = np.array([170, 120, 70])  # Low H (close to 180), Med S, Med V
        upper_red2 = np.array([179, 255, 255]) # Max H (179), High S, High V

        min_detection_area = 100 # Minimum pixel area to consider a detection valid

        while True:
            action_counter += 1
            print(f"--- Cycle #{action_counter} ---")

            # agent.get_current_frame() captures the primary monitor.
            # The image data itself is an array starting from its own (0,0) which corresponds
            # to (agent.screen_left, agent.screen_top) in global screen coordinates.
            frame = agent.get_current_frame()
            if frame is None or frame.size == 0:
                print("Error: Failed to capture frame. Skipping cycle.")
                time.sleep(1)
                continue

            # print(f"Captured frame with shape: {frame.shape}") # Optional: for debugging

            # find_largest_color_area returns coordinates relative to the frame it processed.
            # In this case, relative to the primary monitor's content area.
            target_coords = find_largest_color_area(frame, lower_red1, upper_red1, min_detection_area)
            if target_coords is None: # If not found in first range, try the second
                target_coords = find_largest_color_area(frame, lower_red2, upper_red2, min_detection_area)

            if target_coords:
                # To click using agent.click with raw_pixels=True, we need absolute global screen coordinates.
                # So, add the primary monitor's top-left offset to the coordinates.
                click_x = agent.screen_left + target_coords[0]
                click_y = agent.screen_top + target_coords[1]

                print(f"Action: Red area found at ({target_coords[0]},{target_coords[1]}) relative to primary monitor. Clicking global ({click_x},{click_y}).")
                agent.click(click_x, click_y, raw_pixels=True, button='left') # Click with left button
            else:
                # Perform a random click if no red area is found
                x_pct = random.uniform(0.1, 0.9) # Avoid extreme edges
                y_pct = random.uniform(0.1, 0.9)
                print(f"Action: No red area found. Random click at ({x_pct:.2f}, {y_pct:.2f})% of primary monitor.")
                agent.click(x_pct, y_pct, raw_pixels=False, button='left')

            sleep_duration = random.uniform(0.5, 1.5) # Shorter delay for more reactivity
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
    run_visual_agent() # Ensure this function call is updated
