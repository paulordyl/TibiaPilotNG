import mss
import mss.tools
import numpy as np
# from PIL import Image # Optional, for alternative saving or PIL Image object return

def capture_full_screen(filename: str = None) -> np.ndarray:
    """
    Captures the primary monitor.

    Args:
        filename (str, optional): If provided, saves the screenshot to this path as PNG.

    Returns:
        np.ndarray: The screenshot as an RGB NumPy array.
    """
    with mss.mss() as sct:
        # monitor[0] is all monitors, monitor[1] is primary
        monitor = sct.monitors[1]

        # Grab data from the primary monitor
        sct_img = sct.grab(monitor)

        # Convert to NumPy array. MSS sct_img is a BGRA format.
        img = np.array(sct_img)

        # Convert BGRA to RGB:
        # Slice off alpha channel (BGRA -> BGR) then reverse BGR to RGB
        img_rgb = img[:, :, :3][:, :, ::-1]

        if filename:
            # Use mss.tools.to_png for saving.
            # sct_img.rgb is bytes in RGB order, sct_img.bgra is bytes in BGRA order.
            # to_png expects RGB data.
            mss.tools.to_png(sct_img.rgb, sct_img.size, output=filename)

        return img_rgb

def capture_window_by_title(window_title: str, filename: str = None) -> np.ndarray:
    """
    Captures a specific window identified by its title.
    NOTE: This function is a placeholder and is not fully implemented due to
    OS-specific complexities in robustly finding window coordinates.

    Args:
        window_title (str): The title of the window to capture.
        filename (str, optional): If provided, saves the screenshot to this path.

    Returns:
        np.ndarray: The screenshot of the window as an RGB NumPy array.

    Raises:
        NotImplementedError: This function is not yet implemented.
    """
    # Implementation would require OS-specific libraries:
    # On Windows:
    #   import win32gui
    #   hwnd = win32gui.FindWindow(None, window_title)
    #   if hwnd:
    #       left, top, right, bottom = win32gui.GetWindowRect(hwnd)
    #       width = right - left
    #       height = bottom - top
    #       bbox = (left, top, width, height)
    #       return capture_region(bbox, filename)
    #   else:
    #       raise ValueError(f"Window with title '{window_title}' not found.")
    #
    # On Linux (example using xdotool - would need to parse output):
    #   import subprocess
    #   try:
    #       # Get window ID
    #       cmd_id = f"xdotool search --onlyvisible --name '{window_title}'"
    #       proc_id = subprocess.run(cmd_id, shell=True, check=True, capture_output=True, text=True)
    #       window_id = proc_id.stdout.strip().split('\n')[0]
    #       if not window_id:
    #           raise ValueError(f"Window with title '{window_title}' not found.")
    #       # Get window geometry
    #       cmd_geom = f"xdotool getwindowgeometry {window_id}"
    #       proc_geom = subprocess.run(cmd_geom, shell=True, check=True, capture_output=True, text=True)
    #       # Parse proc_geom.stdout to get Position (X,Y) and Geometry (WxH)
    #       # Example parsing (highly dependent on xdotool output format):
    #       # position_line = [l for l in proc_geom.stdout.split('\n') if "Position:" in l][0]
    #       # geometry_line = [l for l in proc_geom.stdout.split('\n') if "Geometry:" in l][0]
    #       # pos_x, pos_y = map(int, position_line.split(":")[1].strip().split(','))
    #       # width, height = map(int, geometry_line.split(":")[1].strip().split('x'))
    #       # bbox = (pos_x, pos_y, width, height)
    #       # return capture_region(bbox, filename)
    #   except Exception as e:
    #       # print(f"Error capturing window on Linux: {e}")
    #       raise NotImplementedError(f"Linux window capture via xdotool failed or window not found: {e}")
    #
    # On macOS:
    #   # Would involve AppleScript via osascript or pyobjc
    #
    raise NotImplementedError("Window-specific capture is not yet implemented across platforms.")

def capture_region(bbox: tuple[int, int, int, int], filename: str = None) -> np.ndarray:
    """
    Captures a specific region of the screen.

    Args:
        bbox (tuple[int, int, int, int]): (left, top, width, height) of the region.
        filename (str, optional): If provided, saves the screenshot to this path as PNG.

    Returns:
        np.ndarray: The screenshot of the region as an RGB NumPy array.
    """
    if not (isinstance(bbox, tuple) and len(bbox) == 4 and all(isinstance(n, int) for n in bbox)):
        raise ValueError("bbox must be a tuple of 4 integers: (left, top, width, height)")

    monitor_description = {
        "left": bbox[0],
        "top": bbox[1],
        "width": bbox[2],
        "height": bbox[3],
        "mon": 1 # Assuming the region is on the primary monitor
    }
    with mss.mss() as sct:
        sct_img = sct.grab(monitor_description)
        img = np.array(sct_img)
        # Convert BGRA to RGB
        img_rgb = img[:, :, :3][:, :, ::-1]

        if filename:
            mss.tools.to_png(sct_img.rgb, sct_img.size, output=filename)

        return img_rgb
