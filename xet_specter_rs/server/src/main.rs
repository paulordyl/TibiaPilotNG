use tokio::net::{TcpListener, TcpStream};
use tokio_tungstenite::{accept_async, tungstenite::protocol::Message};
use futures_util::{StreamExt, SinkExt};
use std::net::SocketAddr;
use std::error::Error;
use std::env;

// Serde imports
use serde::{Deserialize, Serialize};
use serde_json; // For from_str and to_string
// Optional: use serde_json::json; // if using the json! macro for creating values

// Define message structures
#[derive(Serialize, Deserialize, Debug)]
struct ClientMessage {
    r#type: String, // r# to allow "type" as a field name
    payload: Option<serde_json::Value>, // Flexible payload
}

#[derive(Serialize, Deserialize, Debug)]
struct ServerMessage {
    r#type: String,
    payload: Option<serde_json::Value>,
    original_type: Option<String>, // For ACKs
    status: Option<String>,      // For ACKs
}

#[tokio::main]
async fn main() -> Result<(), Box<dyn Error>> {
    let port = env::var("PORT").unwrap_or_else(|_| "9002".to_string());
    let addr = format!("127.0.0.1:{}", port);

    let listener = TcpListener::bind(&addr).await?;
    println!("WebSocket server listening on: ws://{}", addr);

    while let Ok((stream, client_addr)) = listener.accept().await {
        println!("Incoming TCP connection from: {}", client_addr);
        tokio::spawn(handle_connection(stream, client_addr));
    }
    Ok(())
}

async fn handle_connection(stream: TcpStream, client_addr: SocketAddr) {
    let ws_stream_result = accept_async(stream).await;

    match ws_stream_result {
        Ok(mut ws_stream) => {
            println!("WebSocket connection established: {}", client_addr);

            while let Some(msg_result) = ws_stream.next().await {
                match msg_result {
                    Ok(msg) => {
                        match msg {
                            Message::Text(text_content) => {
                                println!("Received raw text from {}: {}", client_addr, text_content);
                                
                                match serde_json::from_str::<ClientMessage>(&text_content) {
                                    Ok(client_message) => {
                                        println!("Parsed ClientMessage from {}: {:?}", client_addr, client_message);
                                        
                                        let response_message_str = match client_message.r#type.as_str() {
                                            "GET_SETTINGS_REQUEST" => {
                                                let settings_payload = serde_json::json!({
                                                    "obs_host": "localhost",
                                                    "capture_delay": 100,
                                                    "server_version": "0.1.0-alpha-rust"
                                                });
                                                let server_response = ServerMessage {
                                                    r#type: "SETTINGS_RESPONSE".to_string(),
                                                    payload: Some(settings_payload),
                                                    original_type: None,
                                                    status: None,
                                                };
                                                serde_json::to_string(&server_response).ok()
                                            }
                                            "WASM_ACTION_REPORT" => {
                                                println!("Received WASM_ACTION_REPORT payload from {}: {:?}", client_addr, client_message.payload);
                                                let server_response = ServerMessage {
                                                    r#type: "ACK".to_string(),
                                                    payload: None,
                                                    original_type: Some("WASM_ACTION_REPORT".to_string()),
                                                    status: Some("SUCCESS".to_string()),
                                                };
                                                serde_json::to_string(&server_response).ok()
                                            }
                                            _ => {
                                                println!("Unknown message type from {}: {}", client_addr, client_message.r#type);
                                                let error_response = ServerMessage {
                                                    r#type: "ERROR".to_string(),
                                                    payload: Some(serde_json::json!({"message": "Unknown message type received"})),
                                                    original_type: Some(client_message.r#type),
                                                    status: Some("FAILED".to_string()),
                                                };
                                                serde_json::to_string(&error_response).ok()
                                            }
                                        };

                                        if let Some(response_str) = response_message_str {
                                            if ws_stream.send(Message::Text(response_str)).await.is_err() {
                                                eprintln!("Error sending response to {}. Closing connection.", client_addr);
                                                break;
                                            }
                                        }
                                    }
                                    Err(e) => {
                                        eprintln!("Failed to parse JSON from {}: {}. Raw: {}", client_addr, e, text_content);
                                        let error_response = ServerMessage {
                                            r#type: "ERROR".to_string(),
                                            payload: Some(serde_json::json!({"message": "Invalid JSON format", "details": e.to_string()})),
                                            original_type: None,
                                            status: Some("FAILED".to_string()),
                                        };
                                        if let Ok(response_str) = serde_json::to_string(&error_response) {
                                            if ws_stream.send(Message::Text(response_str)).await.is_err() {
                                                eprintln!("Error sending parse error response to {}. Closing connection.", client_addr);
                                                break;
                                            }
                                        }
                                    }
                                }
                            }
                            Message::Binary(bin_data) => {
                                println!("Received binary data ({} bytes) from {}. Ignoring.", client_addr, bin_data.len());
                                // No specific binary handling for now, could echo or process if needed
                            }
                            Message::Ping(ping_data) => {
                                if ws_stream.send(Message::Pong(ping_data)).await.is_err() {
                                    eprintln!("Error sending Pong to {}. Closing connection.", client_addr);
                                    break;
                                }
                            }
                            Message::Pong(_) => {
                                // println!("Received Pong from {}.", client_addr);
                            }
                            Message::Close(close_frame) => {
                                println!("Client {} sent close frame: {:?}", client_addr, close_frame);
                                break;
                            }
                        }
                    }
                    Err(e) => {
                        eprintln!("Error processing message from {}: {}", client_addr, e);
                        break;
                    }
                }
            }
            println!("Terminating WebSocket connection with {}.", client_addr);
            if let Err(e) = ws_stream.close(None).await {
                 eprintln!("Error during explicit close with {}: {}. Connection might already be closed or closing.", client_addr, e);
            }
        }
        Err(e) => {
            eprintln!("Error during WebSocket handshake with {}: {}", client_addr, e);
        }
    }
}

#[cfg(test)]
mod tests {
    #[test]
    fn basic_assertion() {
        assert_eq!(2 + 2, 4);
    }
}
