// Adjust this path based on actual location of the 'pkg' directory
// This path assumes xet_specter_ui/ and xet_specter_rs/ are siblings,
// and pkg is inside xet_specter_rs/frontend_logic/
// For the tool environment, this path might not resolve, but it's what the user would set up.
import init, { greet, add, run_main } from '../../xet_specter_rs/frontend_logic/pkg/frontend_logic.js'; // Note .js extension

// --- Message Interfaces ---
interface ClientMessage {
    type: string;
    payload?: any;
}

interface ServerMessage {
    type: string;
    payload?: any;
    original_type?: string;
    status?: string;
}

// --- Global WebSocket variable ---
let socket: WebSocket | null = null;
const WS_URL = "ws://127.0.0.1:9002"; // Default WebSocket server URL

// --- UI Element References ---
const wsLogOutput = document.getElementById('wsLogOutput') as HTMLPreElement;
const wsConnectButton = document.getElementById('wsConnectButton') as HTMLButtonElement;
const wsDisconnectButton = document.getElementById('wsDisconnectButton') as HTMLButtonElement;
const wsMessageInput = document.getElementById('wsMessageInput') as HTMLInputElement;
const wsSendButton = document.getElementById('wsSendButton') as HTMLButtonElement;
const getSettingsButton = document.getElementById('getSettingsButton') as HTMLButtonElement; // New button
const statusMessages = document.getElementById('statusMessages') as HTMLSpanElement;


// --- Helper Functions ---
function logWsMessage(message: string, data?: any) {
    if (wsLogOutput) {
        let logEntry = message;
        if (data) {
            logEntry += `\n${JSON.stringify(data, null, 2)}`;
        }
        wsLogOutput.textContent += logEntry + '\n\n'; // Add extra newline for readability
        wsLogOutput.scrollTop = wsLogOutput.scrollHeight; // Auto-scroll
    } else {
        console.log("WS Log: " + message, data); // Fallback if pre element not found
    }
}

function updateWsButtonStates(isConnected: boolean) {
    if (wsConnectButton) wsConnectButton.disabled = isConnected;
    if (wsDisconnectButton) wsDisconnectButton.disabled = !isConnected;
    if (wsMessageInput) wsMessageInput.disabled = !isConnected;
    if (wsSendButton) wsSendButton.disabled = !isConnected;
    if (getSettingsButton) getSettingsButton.disabled = !isConnected; // Also manage Get Settings button
}

// --- WebSocket Core Functions ---
function connectWebSocket() {
    if (socket && (socket.readyState === WebSocket.OPEN || socket.readyState === WebSocket.CONNECTING)) {
        logWsMessage("Already connected or connecting.");
        return;
    }

    logWsMessage(`Attempting to connect to ${WS_URL}...`);
    try {
        socket = new WebSocket(WS_URL);

        socket.onopen = () => {
            logWsMessage("WebSocket connection established.");
            updateWsButtonStates(true);
            if (statusMessages) statusMessages.textContent = 'WebSocket connected.';
        };

        socket.onmessage = (event) => {
            const rawData = event.data;
            logWsMessage(`Received raw: ${rawData}`);
            try {
                const serverMessage = JSON.parse(rawData as string) as ServerMessage;
                logWsMessage("Parsed ServerMessage:", serverMessage);

                switch (serverMessage.type) {
                    case "SETTINGS_RESPONSE":
                        logWsMessage("Received SETTINGS_RESPONSE. Payload:", serverMessage.payload);
                        // Optionally display these settings more prominently in the UI
                        break;
                    case "ACK":
                        logWsMessage(`Received ACK for original type: ${serverMessage.original_type}, Status: ${serverMessage.status}`);
                        break;
                    case "ERROR":
                         logWsMessage(`Received ERROR from server. Original type: ${serverMessage.original_type || 'N/A'}, Details:`, serverMessage.payload);
                        break;
                    default:
                        logWsMessage("Received unknown message type from server:", serverMessage);
                        break;
                }
            } catch (e) {
                logWsMessage("Failed to parse JSON from server:", e);
                console.error("Failed to parse JSON from server:", e);
            }
        };

        socket.onerror = (error) => {
            logWsMessage(`WebSocket error: ${error instanceof ErrorEvent ? error.message : 'Unknown error'}`);
            console.error("WebSocket error:", error);
            if (statusMessages) statusMessages.textContent = 'WebSocket error.';
        };

        socket.onclose = (event) => {
            logWsMessage(`WebSocket connection closed. Code: ${event.code}, Reason: "${event.reason || 'N/A'}"`);
            updateWsButtonStates(false);
            socket = null; // Clear the socket variable
            if (statusMessages) statusMessages.textContent = 'WebSocket disconnected.';
        };
    } catch (error) {
        logWsMessage(`Error creating WebSocket: ${error}`);
        console.error("Error creating WebSocket:", error);
        if (statusMessages) statusMessages.textContent = `Error creating WebSocket: ${error}`;
        updateWsButtonStates(false);
    }
}

function disconnectWebSocket() {
    if (socket && socket.readyState === WebSocket.OPEN) {
        logWsMessage("Disconnecting WebSocket...");
        socket.close(); // Server will handle the 'close' message if client sends it
    } else {
        logWsMessage("WebSocket not connected or already closing.");
    }
}

function sendStructuredWsMessage(message: ClientMessage) {
    if (socket && socket.readyState === WebSocket.OPEN) {
        try {
            const jsonMessage = JSON.stringify(message);
            socket.send(jsonMessage);
            logWsMessage(`Sent structured message:`, message);
        } catch (e) {
            logWsMessage("Error stringifying message:", e);
            console.error("Error stringifying message:", e);
        }
    } else {
        logWsMessage("WebSocket not connected. Cannot send structured message.");
    }
}

// --- WASM Initialization and Interaction ---
async function initializeWasm() {
    try {
        if (statusMessages) statusMessages.textContent = 'Loading WASM module...';
        await init(); 
        if (statusMessages) statusMessages.textContent = 'WASM module loaded. Initializing panic hook...';
        
        run_main(); 
        if (statusMessages) statusMessages.textContent = 'Panic hook initialized. UI is ready.';
        console.log("WASM module initialized and panic hook set.");
        return true;
    } catch (error) {
        console.error("Error initializing WASM module:", error);
        if (statusMessages) statusMessages.textContent = `Error initializing WASM: ${error}`;
        return false;
    }
}

function setupWasmInteractions() {
    const nameInput = document.getElementById('nameInput') as HTMLInputElement;
    const greetButton = document.getElementById('greetButton') as HTMLButtonElement;
    const greetResult = document.getElementById('greetResult') as HTMLSpanElement;

    if (greetButton && nameInput && greetResult) {
        greetButton.addEventListener('click', () => {
            const name = nameInput.value;
            if (!name) {
                greetResult.textContent = 'Please enter a name.';
                return;
            }
            try {
                const result = greet(name);
                greetResult.textContent = result;
                if (statusMessages) statusMessages.textContent = 'Greet function called.';
                
                // Report WASM action
                sendStructuredWsMessage({
                    type: "WASM_ACTION_REPORT",
                    payload: { actionName: "greet", input: { name }, output: result }
                });

            } catch (e: any) {
                console.error("Error calling greet:", e);
                greetResult.textContent = `Error: ${e.message || e}`;
                if (statusMessages) statusMessages.textContent = `Error calling greet: ${e.message || e}`;
            }
        });
    } else {
        console.error("Greet UI elements not found.");
        if (statusMessages) statusMessages.textContent = 'Error: Greet UI elements missing.';
    }

    const numAInput = document.getElementById('numA') as HTMLInputElement;
    const numBInput = document.getElementById('numB') as HTMLInputElement;
    const addButton = document.getElementById('addButton') as HTMLButtonElement;
    const addResult = document.getElementById('addResult') as HTMLSpanElement;

    if (addButton && numAInput && numBInput && addResult) {
        addButton.addEventListener('click', () => {
            const a = parseInt(numAInput.value, 10);
            const b = parseInt(numBInput.value, 10);

            if (isNaN(a) || isNaN(b)) {
                addResult.textContent = 'Please enter valid numbers.';
                return;
            }
            try {
                const result = add(a, b);
                addResult.textContent = result.toString();
                if (statusMessages) statusMessages.textContent = 'Add function called.';

                // Report WASM action
                sendStructuredWsMessage({
                    type: "WASM_ACTION_REPORT",
                    payload: { actionName: "add", input: { a, b }, output: result }
                });

            } catch (e: any) {
                console.error("Error calling add:", e);
                addResult.textContent = `Error: ${e.message || e}`;
                if (statusMessages) statusMessages.textContent = `Error calling add: ${e.message || e}`;
            }
        });
    } else {
        console.error("Add UI elements not found.");
        if (statusMessages) statusMessages.textContent = 'Error: Add UI elements missing.';
    }
}

// --- WebSocket UI Event Listeners Setup ---
function setupWebSocketInteractions() {
    if (wsConnectButton) {
        wsConnectButton.addEventListener('click', connectWebSocket);
    } else {
        console.error("WebSocket Connect button not found.");
    }

    if (wsDisconnectButton) {
        wsDisconnectButton.addEventListener('click', disconnectWebSocket);
    } else {
        console.error("WebSocket Disconnect button not found.");
    }
    
    if (wsSendButton && wsMessageInput) {
        wsSendButton.addEventListener('click', () => {
            // Example of sending a generic message; could be adapted for specific ClientMessage types
            const messageText = wsMessageInput.value;
            if (messageText.trim() === "") {
                logWsMessage("Cannot send empty text message via this button.");
                return;
            }
            // For generic text, or if you want to allow sending raw JSON strings:
            // For now, let's assume this button is for sending a "custom" type message for testing
            sendStructuredWsMessage({ type: "CUSTOM_TEXT_MESSAGE", payload: { text: messageText } });
            wsMessageInput.value = ''; // Clear input after sending
        });
        wsMessageInput.addEventListener('keypress', (event) => {
            if (event.key === 'Enter') {
                const messageText = wsMessageInput.value;
                if (messageText.trim() === "") {
                    logWsMessage("Cannot send empty text message via this input.");
                    return;
                }
                sendStructuredWsMessage({ type: "CUSTOM_TEXT_MESSAGE", payload: { text: messageText } });
                wsMessageInput.value = ''; // Clear input after sending
            }
        });
    } else {
        console.error("WebSocket Send button or Message input not found.");
    }

    if (getSettingsButton) {
        getSettingsButton.addEventListener('click', () => {
            sendStructuredWsMessage({ type: "GET_SETTINGS_REQUEST" });
        });
    } else {
        console.error("Get Settings button not found.");
    }
    // Initial button states
    updateWsButtonStates(false); 
}

// --- Main Application Setup ---
async function mainApp() {
    const wasmReady = await initializeWasm();
    if (wasmReady) {
        setupWasmInteractions();
    }
    setupWebSocketInteractions(); 
}

// Run the main application setup once the DOM is loaded
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', mainApp);
} else {
    // DOMContentLoaded has already fired
    mainApp();
}
