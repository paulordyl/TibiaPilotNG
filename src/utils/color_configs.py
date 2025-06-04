# src/utils/color_configs.py
import numpy as np

# Note: OpenCV's Hue range is typically 0-179 for 8-bit images.
# Saturation and Value ranges are typically 0-255.
# These ranges might need tuning based on specific game visuals and lighting.

# Red - often requires two ranges due to Hue wrap-around
RED_HSV_RANGES = [
    (np.array([0, 120, 70]), np.array([10, 255, 255])),   # Lower Hues (more orange-red to pure red)
    (np.array([170, 120, 70]), np.array([179, 255, 255])) # Upper Hues (more magenta-red to pure red)
]

# Blue
BLUE_HSV_RANGES = [
    (np.array([100, 150, 50]), np.array([140, 255, 255])) # Example range for typical blue
]

# Green
GREEN_HSV_RANGES = [
    (np.array([35, 100, 50]), np.array([85, 255, 255]))   # Example range for typical green
]

# Yellow
YELLOW_HSV_RANGES = [
    (np.array([20, 100, 100]), np.array([30, 255, 255])) # Example range for typical yellow
]

# White (Tricky with HSV, often defined by low Saturation, high Value)
# Might also depend on lighting. This is a very broad definition.
WHITE_HSV_RANGES = [
    (np.array([0, 0, 180]), np.array([179, 30, 255]))    # Low S, High V
]

# Black (Also tricky, low Value)
BLACK_HSV_RANGES = [
    (np.array([0, 0, 0]), np.array([179, 255, 50]))     # Low V
]

# Example of a more specific game-related color, if known
# e.g. "HealthPotionRed" if it's a very specific shade
# GAME_HEALTH_POTION_RED_HSV_RANGES = [
#     (np.array([170, 150, 100]), np.array([179, 255, 220]))
# ]


# Dictionary to easily access color ranges by name
TARGET_COLORS = {
    "red": RED_HSV_RANGES,
    "blue": BLUE_HSV_RANGES,
    "green": GREEN_HSV_RANGES,
    "yellow": YELLOW_HSV_RANGES,
    "white": WHITE_HSV_RANGES,
    "black": BLACK_HSV_RANGES,
    # "health_potion": GAME_HEALTH_POTION_RED_HSV_RANGES, # Example
}

if __name__ == '__main__':
    # Simple test to print out the configurations
    print("Defined Color Configurations:")
    for color_name, hsv_ranges in TARGET_COLORS.items():
        print(f"Color: {color_name}")
        for i, (lower, upper) in enumerate(hsv_ranges):
            print(f"  Range {i+1}: Lower={lower}, Upper={upper}")

    # Example accessing a specific color's ranges
    print("\nExample for Red:")
    # Use .get for safer access in case "red" key was mistyped or removed
    red_ranges_example = TARGET_COLORS.get("red", [])
    for i, (lr, ur) in enumerate(red_ranges_example):
        print(f"  Range {i+1}: Lower={lr}, Upper={ur}")
