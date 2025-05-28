use wasm_bindgen::prelude::*;

// Setup for console_error_panic_hook
extern crate console_error_panic_hook;
use std::panic;

#[wasm_bindgen]
pub fn greet(name: &str) -> String {
    format!("Hello, {} from Rust+WASM!", name)
}

#[wasm_bindgen]
pub fn add(a: i32, b: i32) -> i32 {
    a + b
}

#[wasm_bindgen(start)]
pub fn run_main() -> Result<(), JsValue> { // Renamed to avoid conflict if there's a main in JS
    // Set the panic hook for better debugging in the browser console.
    // This should be called once at startup.
    panic::set_hook(Box::new(console_error_panic_hook::hook));
    Ok(())
}

// Basic tests
#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_greet() {
        assert_eq!(greet("Rust"), "Hello, Rust from Rust+WASM!");
    }

    #[test]
    fn test_add() {
        assert_eq!(add(2, 3), 5);
    }
}
