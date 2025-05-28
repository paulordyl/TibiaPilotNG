# XET-SpecterHID - Phase 2: Rust Core (WASM & Server)

This directory contains the Rust components for Phase 2 of the XET-SpecterHID project. It's structured as a Cargo workspace with two main crates:

1.  **`frontend_logic`**: A Rust library compiled to WebAssembly (WASM). It provides core functions that can be called from the JavaScript/TypeScript frontend.
2.  **`server`**: A Rust binary application that runs a WebSocket server. It handles communication between the web UI and potentially a backend Python application in later phases.

## Prerequisites

*   **Rust:**
    *   The code was developed and tested to compile with `rustc 1.75.0`.
    *   **Recommendation:** For easier dependency management and full compatibility with tools like `wasm-pack`, it is **strongly recommended to use the latest stable version of Rust**. Many modern crates and tools (including `wasm-pack` itself for installation via `cargo install`) have Minimum Supported Rust Versions (MSRVs) that are newer than `1.75.0`.
*   **`wasm-pack`:**
    *   Required to compile the `frontend_logic` crate to WebAssembly.
    *   Install separately: `cargo install wasm-pack`.
    *   **Note on MSRV:** If you are using an older Rust version like `1.75.0`, you might encounter issues installing recent versions of `wasm-pack` due to MSRV conflicts in its dependencies. You may need to install an older version of `wasm-pack` (e.g., `cargo install wasm-pack --version "=0.12.1"`) or, preferably, upgrade your Rust toolchain.
*   **Node.js and npm (or pnpm/yarn):**
    *   Required if you intend to build and run the corresponding `xet_specter_ui` frontend that interacts with these Rust components.

## `frontend_logic` (WASM Library)

*   **Purpose:** This crate provides functions intended to be called from JavaScript/TypeScript in the web UI. For this PoC, it includes basic functions like `greet` and `add`.
*   **Build Instructions:**
    1.  Navigate to the `frontend_logic` directory: `cd xet_specter_rs/frontend_logic`
    2.  Run `wasm-pack` to build: `wasm-pack build --target web`
    3.  The compiled WebAssembly module and JavaScript bindings will be output to the `frontend_logic/pkg/` directory. This `pkg/` directory is what the frontend UI will import.
*   **Key Dependencies:**
    *   `wasm-bindgen`: For facilitating interactions between Rust (WASM) and JavaScript.
    *   `console_error_panic_hook`: For better panic message logging in the browser console.

## `server` (WebSocket Server)

*   **Purpose:** This crate runs a WebSocket server that:
    *   Listens for incoming WebSocket connections.
    *   Handles structured JSON messages for basic interactions like:
        *   Responding to a "settings request" from the client.
        *   Acknowledging "WASM action reports" from the client.
    *   Serves as a foundational piece for more complex client-server communication.
*   **Build and Run:**
    1.  From the workspace root (`xet_specter_rs/`): `cargo run -p server`
    2.  Alternatively, navigate to the `server` directory: `cd xet_specter_rs/server && cargo run`
*   **Configuration:**
    *   The server listens on `127.0.0.1`.
    *   The default port is `9002`. This can be overridden by setting the `PORT` environment variable.
*   **Key Dependencies (Pinned for `rustc 1.75.0` compatibility):**
    *   `tokio`: Asynchronous runtime.
    *   `tokio-tungstenite`: Tokio-based WebSocket library.
    *   `tungstenite`: Core WebSocket library.
    *   `futures-util`: Utilities for working with futures.
    *   `serde`, `serde_json`: For JSON serialization and deserialization.
    *   `url`, `idna`, `native-tls`: Transitive dependencies pinned to older versions to maintain compatibility with `rustc 1.75.0`.

## Known Issues

*   **MSRV Challenges with `rustc 1.75.0`:**
    *   The provided Rust version `1.75.0` presented significant challenges in finding compatible versions for network-related dependencies (like `tokio-tungstenite`, `url`, and their ICU-related transitive dependencies) and for installing tools like `wasm-pack`.
    *   The `server` crate's dependencies have been meticulously pinned to very old versions to achieve compilation with `rustc 1.75.0`. This is not ideal for long-term development.
    *   Installation of `wasm-pack` via `cargo install` failed with `rustc 1.75.0`. Users will likely need a newer Rust toolchain to install and use `wasm-pack` effectively.
*   **WASM Compilation:** Due to the `wasm-pack` installation issues with `rustc 1.75.0` in the test environment, the WASM compilation step for `frontend_logic` was not completed during automated testing. This step must be performed by the user in a compatible Rust environment.

---

## Next Steps for Future Development

The following outlines potential areas for expanding and refining the XET-SpecterHID project:

### 1. Rust Server <-> Python Backend Integration

The Rust `server` crate needs to communicate with the existing Python backend (from Phase 1 or a refactored version).

*   **Communication Channel Options:**
    *   **Recommended (Initial): Subprocess with JSON over stdin/stdout:**
        *   The Rust server would spawn the Python script as a child process.
        *   Communication would occur by sending newline-delimited JSON strings over the Python process's stdin and reading from its stdout.
        *   **Pros:** Relatively simple to implement, cross-platform, no network port conflicts.
        *   **Cons:** Can be less performant for very high-throughput data; error handling for subprocess needs care.
    *   **Local Network Socket (TCP or Unix Domain Socket):**
        *   Both Rust server and Python backend connect to a pre-defined local socket.
        *   JSON or another protocol (e.g., custom binary) can be used over the socket.
        *   **Pros:** Decouples processes, potentially higher performance than stdin/stdout.
        *   **Cons:** Requires port/socket management, slightly more complex setup.
    *   **ZeroMQ (0MQ):**
        *   A message queuing library that supports various patterns (req-reply, pub-sub).
        *   **Pros:** Robust, flexible, good for inter-process communication, supports various languages.
        *   **Cons:** Adds an external dependency, steeper learning curve.
    *   **gRPC:**
        *   A high-performance, language-agnostic RPC framework.
        *   **Pros:** Strongly-typed contracts (Protobuf), efficient binary protocol, supports streaming.
        *   **Cons:** More complex setup, code generation step, might be overkill for initial needs.

*   **Defined Message Types (JSON example):**

    *   **Sync Settings:**
        *   `UI -> Rust -> Python`: `{ "type": "UPDATE_SETTINGS", "payload": { ...settings... } }`
        *   `Python -> Rust -> UI`: `{ "type": "SETTINGS_UPDATED", "payload": { ...settings... } }`
        *   `UI -> Rust -> Python` (on connect): `{ "type": "REQUEST_FULL_SETTINGS" }`
        *   `Python -> Rust -> UI`: `{ "type": "FULL_SETTINGS_RESPONSE", "payload": { ...all_settings... } }`

    *   **Streaming Logs:**
        *   `Python -> Rust -> UI`: `{ "type": "LOG_MESSAGE", "payload": { "level": "INFO", "message": "...", "source": "python_backend" } }`

    *   **Commands (Control XET-SpecterHID Core):**
        *   `UI -> Rust -> Python`: `{ "type": "COMMAND_START_BOT" }`
        *   `UI -> Rust -> Python`: `{ "type": "COMMAND_STOP_BOT" }`
        *   `Python -> Rust -> UI (ACK)`: `{ "type": "COMMAND_ACK", "original_command": "COMMAND_START_BOT", "status": "SUCCESS" / "FAILED", "error_message": "..." }`

    *   **Status Updates:**
        *   `Python -> Rust -> UI`: `{ "type": "STATUS_UPDATE", "payload": { "bot_status": "RUNNING" / "IDLE" / "ERROR", "current_action": "..." } }`

    *   **Error Reporting:**
        *   `Python -> Rust -> UI`: `{ "type": "ERROR_REPORT", "payload": { "source": "python_backend", "message": "...", "details": "..." } }`

### 2. UI Enhancements (`xet_specter_ui`)

*   **Display Real Settings:** Fetch settings from the Rust server (which in turn gets them from Python) and display them. Allow editing and sending updates.
*   **Live Log Viewer:** Display logs streamed from the Python backend via the Rust server in the "WebSocket Log" area or a dedicated log view.
*   **Interactive Configuration:** If applicable, allow configuration of parameters like vision ROI or input emulator settings through the UI.
*   **Visual Feedback:** Provide clear visual indicators for bot status (e.g., running, idle, error), WebSocket connection status, etc.
*   **Componentization:** Refactor UI code into more manageable components (e.g., using classes or simple functions for different UI sections).

### 3. WASM Module Expansion (`frontend_logic`)

*   **Shared Data Structures:** If complex data structures are exchanged between Python, Rust, and the UI, define them in Rust and use `serde` with `wasm-bindgen` to make them available in JS/TS. This ensures consistency.
*   **Client-Side Logic:** Consider moving some non-trivial client-side validation or data processing logic into WASM if performance or code-sharing with Rust is beneficial.

### 4. Error Handling & Robustness

*   **Rust Server:** Improve error handling in `handle_connection`, especially for I/O and JSON parsing/serialization. Implement more specific error types.
*   **UI:** Provide clearer error messages to the user for WebSocket connection issues, WASM loading failures, and server errors.
*   **Python Backend Communication:** Implement robust error handling and recovery mechanisms for the chosen communication channel (e.g., retries, handling broken pipes/sockets).

### 5. Build & Packaging

*   **Scripts:** Create scripts (`Makefile`, `package.json` scripts, `justfile`, etc.) to automate common tasks like building the WASM, building the UI, starting the server, and starting the Python backend.
*   **Desktop Application (Optional):** For easier distribution and to avoid browser security limitations (like direct hardware access if ever needed), consider packaging the UI and Rust server into a desktop application using a framework like [Tauri](https://tauri.app/). Tauri allows using web frontend technologies with a Rust backend.

### 6. Addressing MSRV/Tooling (High Priority)

*   **Upgrade Rust Toolchain:** Strongly recommend upgrading the development environment to use the **latest stable Rust version**. This will:
    *   Resolve the MSRV issues encountered with `wasm-pack` installation.
    *   Allow using up-to-date versions of dependencies like `tokio-tungstenite`, `url`, etc., which often include important bug fixes, performance improvements, and new features.
    *   Simplify dependency management significantly.
*   Once Rust is updated, revisit the pinned dependencies in `xet_specter_rs/server/Cargo.toml` and update them to more recent, stable versions.

This outline provides a roadmap for further development, focusing on integrating the components and enhancing functionality.
