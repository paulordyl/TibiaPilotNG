# SKB: A Game Bot in Rust

## Overview

SKB is a project to rewrite a Python-based game bot in Rust. The primary goals are to achieve better performance, explore potentially stealthier interaction techniques, and build a modern, robust architecture that can be extended with more advanced features, including AI capabilities.

This bot interacts with games by reading screen information (visual perception) and emulating user input, primarily via an Arduino device for hardware-level input simulation.

## Current Status (As of this document's last update)

Core systems for input, screen perception, basic game logic, and configuration management are in place. A significant feature recently implemented is the ability to read HP (Health Points) and MP (Mana Points) directly from the screen using template-based digit recognition. The bot operates using a multi-threaded architecture, with separate threads for main gameplay logic (Cavebot), player status monitoring, and healing.

## Key Features Implemented

*   **Arduino-based Input Emulation**: All keyboard and mouse inputs are sent to an Arduino device, which then acts as a USB HID device. This is intended to provide a more hardware-like input pattern.
*   **Screen Capture & Image Processing**:
    *   Capture specific screen regions or the primary screen.
    *   **Template Matching**: Locate predefined images (templates) on the screen (e.g., game objects, UI elements). Includes basic Non-Maximum Suppression.
    *   **Digit Recognition**: Read numerical values (e.g., HP, MP) from the screen by recognizing sequences of digit templates.
    *   **Caching**: Recently found template locations can be cached to improve performance.
*   **Core Gameplay Logic**:
    *   **GameContext**: A shared, thread-safe structure holding dynamic game state (player stats, bot settings) and control flags.
    *   **Cavebot**: Manages waypoint-based navigation and task execution (e.g., walking, opening doors).
    *   **PlayerMonitor**: Periodically reads player HP/MP from the screen and updates `GameContext`.
    *   **Healer**: Checks player HP in `GameContext` and triggers a healing hotkey if HP is below a configured threshold.
    *   **Tasks**: A system for defining and executing specific actions within the Cavebot (e.g., `WalkTask`, `OpenDoorTask`).
*   **Configuration Management**:
    *   Bot settings, hotkeys, Arduino configuration, and screen regions are loaded from a `config.toml` file using Serde.
*   **Multi-threaded Architecture**: Key components like Cavebot, PlayerMonitor, and Healer run in separate threads for concurrent operation.

## Module Overview (`src/`)

The project is organized into several main modules:

*   **`config`**: Handles loading and parsing of `config.toml` using Serde.
    *   `settings.rs`: Defines the configuration structs (`Config`, `ScreenRegion`, etc.).
*   **`input`**: Manages input emulation.
    *   `arduino.rs`: Handles serial communication with the Arduino device.
    *   `keyboard.rs`: Provides functions for keyboard actions (press, hotkey, write) via Arduino.
    *   `mouse.rs`: Provides functions for mouse actions (move, click, drag, scroll) via Arduino.
*   **`image_processing`**: Contains all logic related to analyzing screen captures.
    *   `cache.rs`: Implements `DetectionCache` for storing locations of found templates.
    *   `digit_recognition.rs`: Implements `recognize_digits_in_region` for reading numbers.
    *   `matching.rs`: Provides `locate_template_on_image` and `locate_all_templates_on_image` for finding templates.
    *   `templates.rs`: Implements `TemplateManager` for loading and managing image templates.
*   **`screen_capture`**: Provides functions to capture images from the screen.
    *   `capture.rs`: Implements screen and region capture utilities.
*   **`game_logic`**: Contains the bot's decision-making and operational logic.
    *   `cavebot/`: Manages waypoint navigation and task execution.
        *   `core.rs`: `Cavebot` struct and main loop.
        *   `tasks.rs`: `CavebotTask` enum and execution logic.
        *   `waypoints.rs`: `Waypoint` and `WaypointType` definitions.
    *   `context.rs`: Defines `GameContext`, `PlayerStats`, `BotSettings`.
    *   `healer.rs`: Implements the `Healer` struct and its logic.
    *   `player_monitor.rs`: Implements `PlayerMonitor` for tracking HP/MP.
*   **`error.rs`** (or in `main.rs`): Defines the project's custom `AppError` enum for unified error handling.
*   **`utils.rs`** (if present): For shared utility functions.
*   **`main.rs`**: The application entry point, initializes all modules, sets up shared contexts, and spawns threads.

## Configuration

*   Primary configuration is done via `rust_bot_ng/config.toml`. This file defines Arduino port, hotkeys, screen regions for HP/MP, and other settings.
*   Image templates (e.g., for digits, UI elements) are stored in `rust_bot_ng/templates/`.
*   For detailed instructions on setting up test assets for digit recognition, see `TESTING_DIGIT_RECOGNITION.md`.

## Building and Running (Conceptual)

1.  **Dependencies**:
    *   Rust (stable edition).
    *   OpenCV development libraries.
    *   A C++ toolchain (required by the OpenCV crate).
    *   An Arduino device flashed with compatible firmware that understands the serial commands sent by this bot.
2.  **Build**: Navigate to the SKB project root and run `cargo build --release`.
3.  **Configure**:
    *   Set up `config.toml` with your specific game settings, Arduino port, hotkeys, and screen regions.
    *   Place necessary image templates in the `templates/` directory, especially digit templates in `templates/digits/`.
4.  **Run**: Execute the compiled binary from `target/release/`.

## Next Steps & Future Work

*   **Robust Perception**:
    *   Thoroughly test and refine digit recognition with a comprehensive set of real game images.
    *   Implement more advanced OCR for reading text (e.g., player names, chat messages) if needed.
    *   Expand symbolic recognition for game icons, buffs, etc.
*   **Expanded Game Logic**:
    *   Implement more `CavebotTask` types for diverse actions (looting, targeting, spell casting).
    *   Develop a more sophisticated targeting system.
    *   Build Finite State Machines (FSMs) or Behavior Trees for more complex decision-making.
*   **AI Integration**: Explore integrating machine learning models (e.g., for visual perception, decision making) using Rust's ML ecosystem (like `tch-rs`).
*   **User Interface**: Develop a GUI for easier configuration, monitoring, and control of the bot.
*   **Refinement**: Continuous performance optimization, error handling improvements, and code refactoring.
```
