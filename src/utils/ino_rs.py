import ctypes
import base64
import os # For path joining

class ArduinoCommError(Exception):
    """Custom exception for ArduinoComm errors."""
    pass

class ArduinoComm:
    def __init__(self, port: str, library_path: str = './libarduino_comm.so'):
        """
        Initializes the Arduino communication interface by loading the Rust shared library
        and initializing the serial connection.

        Args:
            port (str): The serial port name (e.g., "COM33", "/dev/ttyACM0").
            library_path (str): Path to the compiled Rust shared library.
                                Defaults to './libarduino_comm.so'.
        """
        try:
            # Determine absolute path to library for more robust loading
            # Assumes the library might be relative to this file's directory or project root.
            # For now, let's try a common convention: place library in project root or a 'lib' folder.
            # This path might need to be made more configurable or discoverable in a real app.
            if not os.path.isabs(library_path):
                # Try relative to project root (assuming utils is one level down)
                base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                abs_library_path = os.path.join(base_dir, library_path.lstrip('./'))
                if not os.path.exists(abs_library_path) and library_path.startswith('./'):
                    # Fallback: try relative to current file (if library is in src/utils/)
                     abs_library_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), library_path.lstrip('./'))

            else:
                abs_library_path = library_path
            
            if not os.path.exists(abs_library_path):
                raise ArduinoCommError(f"Shared library not found at resolved path: {abs_library_path}. Original path: {library_path}")

            self.lib = ctypes.CDLL(abs_library_path)
        except OSError as e:
            raise ArduinoCommError(f"Failed to load ArduinoComm shared library from {abs_library_path}: {e}")

        self._setup_ffi_signatures()

        self.port_handle = self.lib.init_serial(port.encode('utf-8'))
        if not self.port_handle:
            raise ArduinoCommError(f"Failed to initialize serial port '{port}' via Rust FFI.")
        
        self.closed = False

    def _setup_ffi_signatures(self):
        """Sets up the FFI argtypes and restypes for the Rust functions."""
        # init_serial(port_name: *const c_char) -> *mut SerialHandle
        self.lib.init_serial.argtypes = [ctypes.c_char_p]
        self.lib.init_serial.restype = ctypes.c_void_p  # Opaque handle

        # send_command(ptr: *mut SerialHandle, b64_msg: *const c_char)
        self.lib.send_command.argtypes = [ctypes.c_void_p, ctypes.c_char_p]
        self.lib.send_command.restype = None # Assuming Rust returns nothing or handles errors internally

        # close_serial(ptr: *mut SerialHandle)
        self.lib.close_serial.argtypes = [ctypes.c_void_p]
        self.lib.close_serial.restype = None

    def send(self, raw_command_data: str):
        """
        Encodes a raw command string to base64, appends a newline, 
        and sends it to the Arduino via the Rust FFI.

        Args:
            raw_command_data (str): The raw command string (e.g., "keyDown,65").
        """
        if self.closed or not self.port_handle:
            raise ArduinoCommError("Serial port is not initialized or has been closed.")

        command_bytes = raw_command_data.encode('utf-8')
        command_base64 = base64.b64encode(command_bytes)
        # Append newline as the original ino.py did to the base64 string before final encoding
        # The Rust FFI `send_command` expects a C string (char*), so send bytes.
        final_command_string_for_rust = command_base64.decode('utf-8') + '\n'
        
        self.lib.send_command(self.port_handle, final_command_string_for_rust.encode('utf-8'))
        # Original ino.py had a sleep(0.01) after write. If this is still needed,
        # the Rust send_command should handle it, or we add it here.
        # For now, assuming Rust handles necessary delays.

    def close(self):
        """Closes the serial connection via the Rust FFI."""
        if not self.closed and self.port_handle:
            try:
                if hasattr(self.lib, 'close_serial'): # Check if function exists before calling
                    self.lib.close_serial(self.port_handle)
            finally: # Ensure Python side state is updated even if Rust call fails
                self.port_handle = None 
                self.closed = True
        elif self.closed:
            # Optionally log or silently ignore if already closed
            pass


    def __del__(self):
        """Ensures the serial port is closed when the object is garbage collected."""
        self.close()

# Example usage (for testing this file directly, if needed):
# if __name__ == '__main__':
#     try:
#         # Adjust port and library path as necessary for your system
#         # Ensure libarduino_comm.so (or .dll/.dylib) is compiled and in the specified path
#         comm = ArduinoComm("COM3_TEST", library_path='./libarduino_comm.so') 
#         print(f"Successfully initialized Arduino on COM3_TEST with handle {comm.port_handle}")
#         comm.send("testCommand,123")
#         print("Sent 'testCommand,123'")
#         comm.close()
#         print("Closed Arduino connection.")
#     except ArduinoCommError as e:
#         print(f"Error: {e}")
