# XET-SpecterHID - Proof of Concept (Phase 1)

This project is a Proof of Concept for XET-SpecterHID, a system designed for symbiotic interaction with applications/games through visual capture and emulated input.

## PoC Objectives:
*   Capture screen content via OBS Studio.
*   Perform basic visual analysis on the captured frames using OpenCV.
*   Emulate simple user input based on the visual analysis.

## Project Structure:
*   `obs/obs_connector.py`: Handles connection and frame capture from OBS Studio.
*   `vision/screen_parser.py`: Processes image frames for visual cues.
*   `input/emulator.py`: Simulates user input.
*   `core/controller.py`: Orchestrates the capture-analysis-action loop.
*   `config/settings.toml`: Configuration parameters.
*   `main.py`: Main script to run the system.

## Dependencies
The project requires Python 3.8 or newer. The following external Python libraries are needed:

*   **`obs-websocket-py`**: For interacting with the OBS WebSocket API.
*   **`Pillow`**: For image manipulation.
*   **`opencv-python`**: For image processing and analysis.
*   **`numpy`**: Required by OpenCV for numerical operations.
*   **`pyautogui`**: For emulating keyboard input.
*   **`toml`**: For reading the configuration file.

## Setup

1.  **Install Python**:
    *   Ensure you have Python 3.8 or a more recent version installed. You can download it from [python.org](https://www.python.org/).

2.  **Install Dependencies**:
    *   It's recommended to use a virtual environment:
        ```bash
        python -m venv venv
        source venv/bin/activate  # On Windows: venv\Scripts\activate
        ```
    *   You can install the dependencies using pip:
        ```bash
        pip install obs-websocket-py Pillow opencv-python numpy pyautogui toml
        ```
    *   Alternatively, if a `requirements.txt` file is provided in the future, you can use:
        ```bash
        pip install -r requirements.txt
        ```

3.  **Configure OBS Studio**:
    *   **Install OBS Studio**: Download and install OBS Studio from [obsproject.com](https://obsproject.com/).
    *   **Enable WebSocket Server**:
        *   In OBS Studio, go to `Tools` -> `WebSocket Server Settings`.
        *   Check "Enable WebSocket server".
        *   Note the "Server Port" (default is `4455`).
        *   You can set a "Server Password" if you wish for added security.
    *   **Ensure a Source is Active**: Make sure you have a capture source active in OBS (e.g., "Display Capture" to capture your entire screen, or "Window Capture" for a specific application). `OBSConnector` will try to auto-detect a suitable source but works best if one is explicitly available and visible.

4.  **Prepare `config/settings.toml`**:
    *   A configuration file named `settings.toml` is located in the `XET-SpecterHID/config/` directory.
    *   If this file is missing, running `python main.py` or `python core/controller.py` might create a default one with placeholder values.
    *   **Key settings to review and update**:
        *   `[obs]`:
            *   `host`: Set to the IP address where OBS is running (usually `localhost`).
            *   `port`: Must match the "Server Port" in OBS WebSocket settings (e.g., `4455`).
            *   `password`: If you set a password in OBS WebSocket settings, enter it here (e.g., `"your_obs_password"`). If no password, ensure it's commented out or an empty string depending on `OBSConnector`'s expectation (current implementation handles `None` if password key is missing or value is null/empty string in TOML if `obswebsocket` library supports it, otherwise it might need to be explicitly not present or `password = ""`). The current `OBSConnector` passes `None` if the key is missing or the value is null.
            *   `source_name` (optional): You can specify the exact name of an OBS source (e.g., `"Display Capture"`) if you want to bypass auto-detection.
        *   `[vision]`:
            *   `roi_x`, `roi_y`, `roi_width`, `roi_height`: Define the Region of Interest on the screen to be analyzed. `width = -1` or `height = -1` usually means full width/height from the `x,y` coordinate. Defaults are (0,0,-1,-1) for full screen.
            *   `target_hsv_lower`, `target_hsv_upper`: HSV (Hue, Saturation, Value) range for the color to detect. The default is `[35, 100, 100]` to `[85, 255, 255]`, which targets a bright green color. You can use an online HSV color picker to find values for other colors.
            *   `detection_threshold_pixels`: Minimum number of pixels of the target color within the ROI to trigger a "detected" status.
        *   `[input_emulator]`:
            *   `action_on_detection`: The command for the input to simulate when the target color is detected (e.g., `"press_space"`, `"press_enter"`). See `input/emulator.py` for available actions.
            *   `min_delay_ms`, `max_delay_ms`: Range for random delay (in milliseconds) before an input action is executed, to make it appear more human-like.
        *   `[capture]`:
            *   `delay_ms`: The delay in milliseconds between each screen capture and analysis cycle (e.g., `250` for 4 captures per second).

## Running the PoC

1.  **Navigate to the project directory**:
    ```bash
    cd path/to/XET-SpecterHID
    ```
2.  **Activate virtual environment** (if used):
    ```bash
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```
3.  **Run the main script**:
    ```bash
    python main.py
    ```
4.  **Expected Output**:
    *   You will see console logs indicating:
        *   System startup.
        *   Connection attempts to OBS.
        *   Frame capture and analysis results (e.g., "target_color_detected" or "target_color_not_detected").
        *   Input emulation actions if the target color is detected.
    *   Ensure OBS Studio is running and the WebSocket server is enabled as configured.

## Manual Test Scenarios

Here are some basic scenarios to test the PoC's functionality:

1.  **Test Scenario 1: Basic Color Detection and Input**
    *   **Preparation**:
        *   In `config/settings.toml`, ensure `[vision]` settings target a common color (e.g., the default bright green: `target_hsv_lower = [35, 100, 100]`, `target_hsv_upper = [85, 255, 255]`).
        *   Set `[input_emulator]` `action_on_detection` to `"press_space"`.
        *   Ensure your OBS is capturing your screen or a specific window that will show the color.
    *   **Execution**:
        *   Run `python main.py`.
        *   Open a text editor or any application that accepts spacebar input and ensure it's the active window.
        *   On the screen area monitored by OBS, display a large patch of the target color (e.g., open an image editor and fill a large area with bright green, or open a webpage with a green background).
    *   **Expected Outcome**:
        *   The console logs should show "target_color_detected".
        *   The `InputEmulator` should simulate a spacebar press, which should appear in your active text editor.

2.  **Test Scenario 2: No Detection**
    *   **Preparation**: Same as Scenario 1.
    *   **Execution**:
        *   Run `python main.py`.
        *   Ensure the target color is NOT visible in the OBS capture area.
    *   **Expected Outcome**:
        *   The console logs should show "target_color_not_detected" (or similar).
        *   No input action should be simulated.

3.  **Test Scenario 3: ROI Testing**
    *   **Preparation**:
        *   In `config/settings.toml`, configure a specific Region of Interest (ROI) in the `[vision]` section that does not cover the full screen. For example: `roi_x = 100`, `roi_y = 100`, `roi_width = 500`, `roi_height = 500`.
        *   Keep other settings as in Scenario 1.
    *   **Execution**:
        *   Run `python main.py`.
        *   Display the target color patch:
            *   First, entirely *inside* the defined ROI.
            *   Second, entirely *outside* the defined ROI.
            *   Third, partially overlapping the ROI.
    *   **Expected Outcome**:
        *   Input (e.g., spacebar press) should only be triggered when a sufficient amount of the target color is detected *within* the defined ROI. Observe console logs for pixel counts and detection status.

## Troubleshooting
*   **"Failed to connect to OBS WebSocket"**: Ensure OBS is running, WebSocket server is enabled (Tools -> WebSocket Server Settings), and host/port/password in `settings.toml` match OBS settings. Check firewall rules if OBS is on a different machine.
*   **"Could not automatically determine a source to capture"**: Make sure a video source (like 'Display Capture' or 'Window Capture') is active and visible in your current OBS scene. You can also explicitly set `source_name` in `config/settings.toml` under the `[obs]` section.
*   **Input not working**: `pyautogui` might require accessibility permissions on some operating systems (e.g., macOS). Ensure the window where you expect input is active/focused. Avoid running in headless server environments unless a virtual display is configured.
*   **Incorrect color detection**: HSV values can be tricky. Use an online HSV color picker tool to fine-tune `target_hsv_lower` and `target_hsv_upper` for your specific color and lighting conditions. Adjust `detection_threshold_pixels` based on the size of the target object in your view.
```
