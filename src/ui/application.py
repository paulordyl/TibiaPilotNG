import customtkinter
from tkinter import BooleanVar
import queue
import json # Though likely handled in client, good for future use
from .websocket_client import SpecterWebSocketClient
from .pages.config import ConfigPage
from .pages.comboSpells import ComboSpellsPage
from .pages.inventory import InventoryPage
from .pages.cavebot.cavebotPage import CavebotPage
from .pages.healing.healingPage import HealingPage
from .utils import genRanStr

class Application(customtkinter.CTk):
    def __init__(self, context):
        super().__init__()
        
        customtkinter.set_appearance_mode("dark")

        self.context = context
        self.title(genRanStr())
        self.resizable(False, False)

        self.configPage = None
        self.inventoryPage = None
        self.cavebotPage = None
        self.healingPage = None
        self.comboPage = None
        self.canvasWindow = None

        configurationBtn = customtkinter.CTkButton(self, text="Configuration", corner_radius=32,
                                        fg_color="transparent", border_color="#C20034",
                                        border_width=2, hover_color="#C20034",
                                        command=self.configurationWindow)
        configurationBtn.grid(row=0, column=0, padx=20, pady=20)

        inventoryBtn = customtkinter.CTkButton(self, text="Inventory", corner_radius=32,
                                        fg_color="transparent", border_color="#C20034",
                                        border_width=2, hover_color="#C20034",
                                        command=self.inventoryWindow)
        inventoryBtn.grid(row=0, column=1, padx=20, pady=20)

        cavebotBtn = customtkinter.CTkButton(self, text="Cave", corner_radius=32,
                                        fg_color="transparent", border_color="#C20034",
                                        border_width=2, hover_color="#C20034",
                                        command=self.caveWindow)
        cavebotBtn.grid(row=0, column=2, padx=20, pady=20)

        healingBtn = customtkinter.CTkButton(self, text="Healing", corner_radius=32,
                                        fg_color="transparent", border_color="#C20034",
                                        border_width=2, hover_color="#C20034",
                                        command=self.healingWindow)
        healingBtn.grid(row=1, column=0, padx=20, pady=20)

        comboBtn = customtkinter.CTkButton(self, text="Combo Spells", corner_radius=32,
                                        fg_color="transparent", border_color="#C20034",
                                        border_width=2, hover_color="#C20034",
                                        command=self.comboWindow)
        comboBtn.grid(row=1, column=1, padx=20, pady=20)

        self.enabledVar = BooleanVar()
        self.checkbutton = customtkinter.CTkCheckBox(
            self, text='Enabled', variable=self.enabledVar, command=self.onToggleEnabledButton,
            hover_color="#870125", fg_color='#C20034')
        self.checkbutton.grid(column=2, row=1, padx=20, pady=20, sticky='w')

        # WebSocket Client Initialization
        self.ws_message_queue = queue.Queue()
        self.ws_client = SpecterWebSocketClient(uri="ws://localhost:8765", message_queue=self.ws_message_queue)
        self.ws_client.start()

        self.ws_status_label = customtkinter.CTkLabel(self, text="WS Status: Connecting...")
        self.ws_status_label.grid(row=2, column=0, columnspan=3, padx=20, pady=10, sticky="ew")

        # Python Version UI
        self.python_version_label = customtkinter.CTkLabel(self, text="Python Version: N/A")
        self.python_version_label.grid(row=3, column=0, columnspan=2, padx=20, pady=(5,0), sticky="w")
        self.get_python_version_button = customtkinter.CTkButton(self, text="Get Python Version", command=self._get_python_version)
        self.get_python_version_button.grid(row=3, column=2, padx=20, pady=(5,0), sticky="e")

        # Backend Status UI
        self.backend_status_label = customtkinter.CTkLabel(self, text="Backend Status: N/A")
        self.backend_status_label.grid(row=4, column=0, columnspan=2, padx=20, pady=(5,10), sticky="w")
        self.get_backend_status_button = customtkinter.CTkButton(self, text="Get Backend Status", command=self._get_backend_status)
        self.get_backend_status_button.grid(row=4, column=2, padx=20, pady=(5,10), sticky="e")

        self._poll_ws_queue()

        # Handle graceful shutdown
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

    def _poll_ws_queue(self):
        msg = self.ws_client.get_message()
        if msg is not None:
            msg_type = msg.get("type")
            if msg_type == "status":
                self.ws_status_label.configure(text=f"WS Status: {msg.get('data')}")
            elif msg_type == "response":
                command = msg.get("command")
                payload = msg.get("payload")
                if command == "get_python_version" and payload:
                    version = payload.get("version", "Error")
                    self.python_version_label.configure(text=f"Python Version: {version}")
                elif command == "get_backend_status" and payload:
                    status = payload.get("status", "Error")
                    self.backend_status_label.configure(text=f"Backend Status: {status}")
        self.after(100, self._poll_ws_queue) # Poll every 100ms

    def _get_python_version(self):
        self.ws_client.send_message({"command": "get_python_version"})

    def _get_backend_status(self):
        self.ws_client.send_message({"command": "get_backend_status"})

    def on_closing(self):
        if self.ws_client:
            self.ws_client.stop()
        self.destroy()

    def configurationWindow(self):
        if self.configPage is None or not self.configPage.winfo_exists():
            self.configPage = ConfigPage(self.context)
        else:
            self.configPage.focus()

    def inventoryWindow(self):
        if self.inventoryPage is None or not self.inventoryPage.winfo_exists():
            self.inventoryPage = InventoryPage(self.context)
        else:
            self.inventoryPage.focus()

    def caveWindow(self):
        if self.cavebotPage is None or not self.cavebotPage.winfo_exists():
            self.cavebotPage = CavebotPage(self.context)
        else:
            self.cavebotPage.focus()

    def healingWindow(self):
        if self.healingPage is None or not self.healingPage.winfo_exists():
            self.healingPage = HealingPage(self.context)
        else:
            self.healingPage.focus()

    def comboWindow(self):
        if self.comboPage is None or not self.comboPage.winfo_exists():
            self.comboPage = ComboSpellsPage(self.context)
        else:
            self.comboPage.focus()

    def onToggleEnabledButton(self):
        is_enabled = self.enabledVar.get()
        self.ws_client.send_message({"command": "set_enabled", "payload": is_enabled})
        # Optional: Log or update status, for now, the checkbox state is the primary feedback
        # print(f"UI: Sent 'set_enabled' command with payload: {is_enabled}")