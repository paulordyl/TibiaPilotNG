import asyncio
import json
import queue
import threading
import websockets

class SpecterWebSocketClient:
    def __init__(self, uri: str, message_queue: queue.Queue):
        self.uri = uri
        self.message_queue = message_queue
        self.thread = None
        self.loop = None
        self._ws = None
        self._running = False

    def _run_asyncio_loop(self):
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        self.loop.run_until_complete(self._connect())

    def start(self):
        if self._running:
            return  # Already running

        self._running = True
        self.message_queue.put({"type": "status", "data": "connecting"})
        self.thread = threading.Thread(target=self._run_asyncio_loop, daemon=True)
        self.thread.start()

    def stop(self):
        if not self._running:
            return  # Already stopped

        self._running = False
        if self.loop and self._ws and self._ws.open:
            asyncio.run_coroutine_threadsafe(self._ws.close(), self.loop)
        
        if self.thread and self.thread.is_alive():
            self.thread.join()
        
        self.message_queue.put({"type": "status", "data": "disconnected"})
        # It's good practice to clean up the loop if it's no longer needed
        if self.loop and not self.loop.is_running():
            self.loop.close()
            self.loop = None


    async def _connect(self):
        while self._running:
            try:
                async with websockets.connect(self.uri) as websocket:
                    self._ws = websocket
                    self.message_queue.put({"type": "status", "data": "connected"})
                    async for message in websocket:
                        try:
                            data = json.loads(message)
                            self.message_queue.put({"type": "data", "payload": data})
                        except json.JSONDecodeError:
                            self.message_queue.put({"type": "status", "data": "json_error"})
                            # Log or handle JSON parsing error appropriately
                        except Exception as e:
                            self.message_queue.put({"type": "status", "data": f"message_processing_error: {str(e)}"})


            except websockets.exceptions.ConnectionClosed:
                if self._running: # Avoid sending connection_lost if we intended to stop
                    self.message_queue.put({"type": "status", "data": "connection_lost"})
            except ConnectionRefusedError:
                if self._running:
                    self.message_queue.put({"type": "status", "data": "connection_error_refused"})
            except Exception as e:
                if self._running:
                    self.message_queue.put({"type": "status", "data": f"connection_error: {str(e)}"})
            finally:
                self._ws = None # Ensure ws is None if not connected
                if self._running:
                    await asyncio.sleep(5)  # Wait before retrying

    def send_message(self, message: dict):
        if self._ws and self._ws.open and self.loop:
            future = asyncio.run_coroutine_threadsafe(self._ws.send(json.dumps(message)), self.loop)
            try:
                future.result(timeout=5)  # Wait for send to complete with a timeout
            except TimeoutError:
                self.message_queue.put({"type": "status", "data": "send_timeout"})
            except Exception as e: # Catch other potential errors from send
                self.message_queue.put({"type": "status", "data": f"send_error: {str(e)}"})
        else:
            self.message_queue.put({"type": "status", "data": "error_not_connected"})

    def get_message(self):
        try:
            return self.message_queue.get_nowait()
        except queue.Empty:
            return None
