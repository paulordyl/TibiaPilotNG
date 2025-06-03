# import ctypes # No longer needed
# import base64 # No longer needed for send, Rust side handles it
# import os # No longer needed for library path

# Attempt to import the PyO3 module.
# This assumes `skb_core` is installed in the Python environment
# (e.g., via `maturin develop` or `pip install .` from the skb_core directory)
# and that the library name in skb_core/Cargo.toml's [lib] section
# makes `rust_utils_module` available under `skb_core`.
try:
    from skb_core import rust_utils_module
except ImportError as e:
    # Provide a more informative error message if the module can't be found.
    # This helps users diagnose if skb_core isn't compiled or installed correctly.
    raise ImportError(
        "Failed to import 'rust_utils_module' from 'skb_core'. "
        "Ensure the skb_core Rust library is compiled and installed in your Python environment. "
        f"Original error: {e}"
    )

class ArduinoCommError(Exception):
    """Custom exception for ArduinoComm errors."""
    pass

class ArduinoComm:
    def __init__(self, port: str, baud_rate: int):
        """
        Initializes the Arduino communication interface by calling the PyO3 function
        from the skb_core Rust library.

        Args:
            port (str): The serial port name (e.g., "COM33", "/dev/ttyACM0").
            baud_rate (int): The baud rate for the serial connection.
        """
        self.port = port
        self.baud_rate = baud_rate
        self.closed = True # Start as closed, successful init will open it

        try:
            rust_utils_module.arduino_init(self.port, self.baud_rate)
            self.closed = False # Mark as open if init succeeds
        except Exception as e: # Catching a broad exception as PyO3 errors can vary
            raise ArduinoCommError(f"Failed to initialize Arduino on port '{self.port}' with baud rate {self.baud_rate}: {e}")

    def send(self, raw_command_data: str):
        """
        Sends a raw command string to the Arduino via the PyO3 Rust function.
        Base64 encoding and newline addition are handled by the Rust side.

        Args:
            raw_command_data (str): The raw command string (e.g., "keyDown,65").
        """
        if self.closed:
            raise ArduinoCommError("Serial port is not initialized or has been closed.")

        try:
            rust_utils_module.arduino_send_command(raw_command_data)
        except Exception as e:
            raise ArduinoCommError(f"Failed to send command '{raw_command_data}': {e}")

    def close(self):
        """Closes the serial connection via the PyO3 Rust function."""
        if not self.closed:
            try:
                rust_utils_module.arduino_close()
            except Exception as e:
                # Log or handle error during close, but still mark as closed
                # For example, print(f"Error during Arduino close: {e}")
                # Depending on desired behavior, this might not need to raise ArduinoCommError
                # if the primary goal is to ensure the Python state reflects 'closed'.
                pass
            finally:
                self.closed = True
        # If already closed, do nothing.

    def __del__(self):
        """Ensures the serial port is closed when the object is garbage collected."""
        # This will call self.close(), which now calls the PyO3 function.
        # It's important that rust_utils_module.arduino_close() is safe to call
        # even if the connection was already closed or never opened from Python's perspective,
        # or if AppContext in Rust is gone (though __del__ timing is tricky).
        # The Rust `arduino_close` is designed to be idempotent.
        if not self.closed:
            try:
                self.close()
            except Exception:
                # Suppress errors during __del__ as it can cause issues if an error occurs
                # while the interpreter is shutting down or an object is being finalized.
                pass

# Example usage (for testing this file directly, if needed):
# if __name__ == '__main__':
#     # This example requires skb_core to be compiled and importable,
#     # and a real or mock Arduino on the specified port.
#     TEST_PORT = "COM_TEST"  # Replace with your actual or test port
#     TEST_BAUD_RATE = 9600
#     try:
#         print(f"Attempting to initialize Arduino on {TEST_PORT} at {TEST_BAUD_RATE} baud...")
#         comm = ArduinoComm(port=TEST_PORT, baud_rate=TEST_BAUD_RATE)
#         print(f"Successfully initialized Arduino on {TEST_PORT}")
#
#         print("Sending 'testCommand,123'...")
#         comm.send("testCommand,123")
#         print("Sent 'testCommand,123'")
#
#         print("Closing Arduino connection...")
#         comm.close()
#         print("Closed Arduino connection.")
#
#         print("\nTesting re-initialization (should be possible):")
#         comm2 = ArduinoComm(port=TEST_PORT, baud_rate=TEST_BAUD_RATE)
#         print(f"Successfully re-initialized Arduino on {TEST_PORT}")
#         comm2.send("anotherCommand,456")
#         print("Sent 'anotherCommand,456'")
#         comm2.close()
#         print("Closed second Arduino connection.")
#
#     except ArduinoCommError as e:
#         print(f"Arduino Communication Error: {e}")
#     except ImportError as e:
#         print(f"Import Error: {e}")
#     except Exception as e:
#         print(f"An unexpected error occurred: {e}")
