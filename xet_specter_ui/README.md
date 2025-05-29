# XET-SpecterHID UI (Phase 2 - TypeScript Frontend)

This directory contains the TypeScript-based frontend UI for Phase 2 of the XET-SpecterHID project. This UI is designed to:

1.  Interact with a WebAssembly (WASM) module generated from Rust code (`xet_specter_rs/frontend_logic`).
2.  Communicate with a Rust-based WebSocket server (`xet_specter_rs/server`) using structured JSON messages.

## Prerequisites

*   **Node.js and npm (or pnpm/yarn):**
    *   Required to install dependencies and compile the TypeScript code.
    *   You can download Node.js (which includes npm) from [nodejs.org](https://nodejs.org/).
*   **A modern web browser:**
    *   Required to run the `index.html` file (e.g., Chrome, Firefox, Edge, Safari).
*   **Rust WebSocket Server:**
    *   The Rust server from `xet_specter_rs/server/` must be running for WebSocket communication features to work.
*   **Compiled WASM Module:**
    *   The Rust WASM module from `xet_specter_rs/frontend_logic/` must be compiled (using `wasm-pack build --target web`). The output `pkg/` directory is expected by this UI.

## Setup

1.  **Navigate to the UI directory:**
    ```bash
    cd path/to/xet_specter_ui
    ```
2.  **Install dependencies:**
    ```bash
    npm install
    # or pnpm install / yarn install
    ```
    This will install `typescript` as defined in `package.json`.

## Build

To compile the TypeScript code (`src/main.ts`) into JavaScript (`dist/main.js`), run:

```bash
npm run build
```
This command executes `tsc` (the TypeScript compiler) using the configuration in `tsconfig.json`.

## Running the UI

1.  **Ensure Prerequisites are Met:**
    *   **Rust WebSocket Server:** Start the server from `xet_specter_rs/server/` (e.g., `cargo run`). It typically listens on `ws://127.0.0.1:9002`.
    *   **WASM Module:**
        *   Compile the `xet_specter_rs/frontend_logic` crate using `wasm-pack build --target web`.
        *   The generated `pkg/` directory must be correctly located relative to the import path in `xet_specter_ui/src/main.ts`. The default path is `../../xet_specter_rs/frontend_logic/pkg/frontend_logic.js`.
        *   **Important Note:** The automated testing environment (using `rustc 1.75.0`) encountered issues installing `wasm-pack`, so this WASM compilation step could not be completed by the automated tooling. You will need to perform this step in a compatible Rust environment (preferably latest stable Rust).

2.  **Open `index.html`:**
    *   Open the `xet_specter_ui/index.html` file directly in your web browser.
    *   For best results and to avoid potential issues with ES module loading via `file:///` URLs, it's recommended to serve the `xet_specter_ui/` directory using a simple local HTTP server. For example, from within the `xet_specter_ui/` directory:
        ```bash
        npx serve
        # or: python -m http.server
        ```
        Then navigate to the provided local server address (e.g., `http://localhost:3000` or `http://localhost:8000`).

## Features

*   **WASM Interaction:**
    *   Calls a `greet(name: string)` function from the Rust WASM module.
    *   Calls an `add(a: number, b: number)` function from the Rust WASM module.
    *   Initializes the WASM module and sets up a panic hook for better error messages from WASM.
*   **WebSocket Communication:**
    *   Connects to the Rust WebSocket server (default `ws://127.0.0.1:9002`).
    *   Displays connection status and logs messages to/from the server in a dedicated log area.
    *   **Structured JSON Messaging:**
        *   Sends a `GET_SETTINGS_REQUEST` to the server and displays the `SETTINGS_RESPONSE`.
        *   Sends `WASM_ACTION_REPORT` messages to the server after WASM functions (`greet`, `add`) are executed, detailing the action, input, and output.
        *   Handles `ACK` and `ERROR` messages from the server.
        *   Allows sending custom text messages (which are wrapped in a JSON structure for this PoC).

## Key Dependencies

*   **`typescript`**: (devDependencies) Used for compiling TypeScript to JavaScript.

The UI is structured with HTML, CSS for basic styling, and TypeScript for application logic.
```
