import pygetwindow as gw
import re
import win32gui
import customtkinter
import tkinter as tk
from ..utils import genRanStr
from ..theme import MATRIX_BLACK, MATRIX_GREEN, MATRIX_GREEN_HOVER, MATRIX_GREEN_BORDER, MATRIX_GREEN_DISABLED
from tkinter import filedialog, messagebox
import json

class ConfigPage(customtkinter.CTkToplevel):
    def __init__(self, context, ws_client): # Added ws_client
        super().__init__()
        self.configure(fg_color=MATRIX_BLACK)
        # self.context = context # REMOVED: No longer directly using context for initial population
        self.ws_client = ws_client # Stored ws_client

        if self.ws_client:
            self.ws_client.send_message({"command": "config_get_initial_settings"})

        self.title(genRanStr())
        self.resizable(False, False)

        self.windowsFrame = customtkinter.CTkFrame(self, fg_color=MATRIX_BLACK, border_color=MATRIX_GREEN_BORDER, border_width=1)
        self.windowsFrame.grid(column=0, row=0, padx=10,
                            pady=10, sticky='nsew')

        self.windowsFrame.rowconfigure(0, weight=1)
        self.windowsFrame.columnconfigure(0, weight=1)

        self.tibiaWindowLabel = customtkinter.CTkLabel(self.windowsFrame, text="Game Window:", text_color=MATRIX_GREEN)
        self.tibiaWindowLabel.grid(row=0, column=0, sticky='w', padx=10, pady=(10, 0))

        self.windowsCombobox = customtkinter.CTkComboBox(
            self.windowsFrame, values=self.getGameWindows(), state='readonly',
            command=self.onChangeWindow, text_color=MATRIX_GREEN, border_color=MATRIX_GREEN_BORDER,
            fg_color=MATRIX_BLACK, button_color=MATRIX_GREEN_BORDER, button_hover_color=MATRIX_GREEN_HOVER,
            dropdown_fg_color=MATRIX_BLACK, dropdown_hover_color=MATRIX_GREEN_HOVER, dropdown_text_color=MATRIX_GREEN)
        self.windowsCombobox.grid(row=1, column=0, sticky='ew', padx=10, pady=10)

        self.button = customtkinter.CTkButton(
            self.windowsFrame, text='Atualizar', command=self.refreshWindows,
            corner_radius=32, fg_color="transparent", text_color=MATRIX_GREEN,
            border_color=MATRIX_GREEN_BORDER, border_width=2, hover_color=MATRIX_GREEN_HOVER)
        self.button.grid(row=1, column=1, padx=10, pady=10)

        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)

        self.shovelRopeFrame = customtkinter.CTkFrame(self, fg_color=MATRIX_BLACK, border_color=MATRIX_GREEN_BORDER, border_width=1)
        self.shovelRopeFrame.grid(column=1, row=0, padx=10,
                            pady=10, sticky='nsew')

        self.shovelHotkeyLabel = customtkinter.CTkLabel(
            self.shovelRopeFrame, text='Shovel Hotkey:', text_color=MATRIX_GREEN)
        self.shovelHotkeyLabel.grid(column=0, row=0, padx=10,
                            pady=10, sticky='nsew')

        self.shovelHotkeyEntryVar = tk.StringVar()
        # self.shovelHotkeyEntryVar.set(self.context.context['general_hotkeys']['shovel_hotkey']) # REMOVED
        self.shovelHotkeyEntry = customtkinter.CTkEntry(self.shovelRopeFrame, textvariable=self.shovelHotkeyEntryVar,
                                                        text_color=MATRIX_GREEN, border_color=MATRIX_GREEN_BORDER,
                                                        fg_color=MATRIX_BLACK, insertbackground=MATRIX_GREEN)
        self.shovelHotkeyEntry.bind('<Key>', self.onChangeShovelHotkey)
        self.shovelHotkeyEntry.grid(column=1, row=0, padx=10,
                            pady=10, sticky='nsew')
        
        self.ropeHotkeyLabel = customtkinter.CTkLabel(
            self.shovelRopeFrame, text='Rope Hotkey:', text_color=MATRIX_GREEN)
        self.ropeHotkeyLabel.grid(column=0, row=1, padx=10,
                            pady=10, sticky='nsew')

        self.ropeHotkeyEntryVar = tk.StringVar()
        # self.ropeHotkeyEntryVar.set(self.context.context['general_hotkeys']['rope_hotkey']) # REMOVED
        self.ropeHotkeyEntry = customtkinter.CTkEntry(self.shovelRopeFrame, textvariable=self.ropeHotkeyEntryVar,
                                                      text_color=MATRIX_GREEN, border_color=MATRIX_GREEN_BORDER,
                                                      fg_color=MATRIX_BLACK, insertbackground=MATRIX_GREEN)
        self.ropeHotkeyEntry.bind('<Key>', self.onChangeRopeHotkey)
        self.ropeHotkeyEntry.grid(column=1, row=1, padx=10,
                            pady=10, sticky='nsew')
        
        self.shovelRopeFrame.columnconfigure(0, weight=1)
        self.shovelRopeFrame.columnconfigure(1, weight=1)

        self.autoHurFrame = customtkinter.CTkFrame(self, fg_color=MATRIX_BLACK, border_color=MATRIX_GREEN_BORDER, border_width=1)
        self.autoHurFrame.grid(column=0, row=1, padx=10,
                            pady=10, sticky='nsew')
        
        self.checkVar = tk.BooleanVar()
        # self.checkVar.set(self.context.context['auto_hur']['enabled']) # REMOVED
        self.checkbutton = customtkinter.CTkCheckBox(
            self.autoHurFrame, text='Enabled', variable=self.checkVar, command=self.onToggleAutoHur,
            text_color=MATRIX_GREEN, fg_color=MATRIX_GREEN, hover_color=MATRIX_GREEN_HOVER,
            border_color=MATRIX_GREEN_BORDER, checkmark_color=MATRIX_BLACK)
        self.checkbutton.grid(column=0, row=0, sticky='nsew', padx=10, pady=10)

        self.checkPzVar = tk.BooleanVar()
        # self.checkPzVar.set(self.context.context['auto_hur']['pz']) # REMOVED
        self.checkpzbutton = customtkinter.CTkCheckBox(
            self.autoHurFrame, text='Usar em PZ', variable=self.checkPzVar, command=self.onToggleAutoHurPz,
            text_color=MATRIX_GREEN, fg_color=MATRIX_GREEN, hover_color=MATRIX_GREEN_HOVER,
            border_color=MATRIX_GREEN_BORDER, checkmark_color=MATRIX_BLACK)
        self.checkpzbutton.grid(column=1, row=0, sticky='nsew', padx=10, pady=10)

        self.autoHurSpellLabel = customtkinter.CTkLabel(
            self.autoHurFrame, text='Spell:', text_color=MATRIX_GREEN)
        self.autoHurSpellLabel.grid(column=0, row=1, padx=10,
                            pady=10, sticky='nsew')

        self.hurSpellCombobox = customtkinter.CTkComboBox(
            self.autoHurFrame, values=['utani hur', 'utani gran hur', 'utani tempo hur', 'utamo tempo san'], state='readonly',
            command=self.setHurSpell, text_color=MATRIX_GREEN, border_color=MATRIX_GREEN_BORDER,
            fg_color=MATRIX_BLACK, button_color=MATRIX_GREEN_BORDER, button_hover_color=MATRIX_GREEN_HOVER,
            dropdown_fg_color=MATRIX_BLACK, dropdown_hover_color=MATRIX_GREEN_HOVER, dropdown_text_color=MATRIX_GREEN)
        # if self.context.enabledProfile is not None and self.context.enabledProfile['config']['auto_hur']['spell'] is not None: # REMOVED
            # self.hurSpellCombobox.set(self.context.enabledProfile['config']['auto_hur']['spell']) # REMOVED
        self.hurSpellCombobox.grid(row=1, column=1, padx=10, pady=10, sticky='nsew')
        
        self.autoHurLabel = customtkinter.CTkLabel(
            self.autoHurFrame, text='AutoHur Hotkey:', text_color=MATRIX_GREEN)
        self.autoHurLabel.grid(column=0, row=2, padx=10,
                            pady=10, sticky='nsew')

        self.autoHurHotkeyEntryVar = tk.StringVar()
        # self.autoHurHotkeyEntryVar.set(self.context.context['auto_hur']['hotkey']) # REMOVED
        self.autoHurHotkeyEntry = customtkinter.CTkEntry(self.autoHurFrame, textvariable=self.autoHurHotkeyEntryVar,
                                                         text_color=MATRIX_GREEN, border_color=MATRIX_GREEN_BORDER,
                                                         fg_color=MATRIX_BLACK, insertbackground=MATRIX_GREEN)
        self.autoHurHotkeyEntry.bind('<Key>', self.onChangeAutoHurHotkey)
        self.autoHurHotkeyEntry.grid(column=1, row=2, padx=10,
                            pady=10, sticky='nsew')
        
        self.autoHurFrame.columnconfigure(0, weight=1)
        self.autoHurFrame.columnconfigure(1, weight=1)

        self.alertFrame = customtkinter.CTkFrame(self, fg_color=MATRIX_BLACK, border_color=MATRIX_GREEN_BORDER, border_width=1)
        self.alertFrame.grid(column=1, row=1, padx=10,
                            pady=10, sticky='nsew')
        
        self.alertCheckVar = tk.BooleanVar()
        # self.alertCheckVar.set(self.context.context['alert']['enabled']) # REMOVED
        self.alertCheckButton = customtkinter.CTkCheckBox( # This is the first alertCheckButton
            self.alertFrame, text='Alert Enabled', variable=self.alertCheckVar, command=self.onToggleAlert,
            text_color=MATRIX_GREEN, fg_color=MATRIX_GREEN, hover_color=MATRIX_GREEN_HOVER,
            border_color=MATRIX_GREEN_BORDER, checkmark_color=MATRIX_BLACK)
        self.alertCheckButton.grid(column=0, row=0, sticky='nsew', padx=10, pady=10)

        self.alertCaveCheckVar = tk.BooleanVar()
        # self.alertCaveCheckVar.set(self.context.context['alert']['cave']) # REMOVED
        self.alertCaveButton = customtkinter.CTkCheckBox(
            self.alertFrame, text='Apenas cave ativo', variable=self.alertCaveCheckVar, command=self.onToggleAlertCave,
            text_color=MATRIX_GREEN, fg_color=MATRIX_GREEN, hover_color=MATRIX_GREEN_HOVER,
            border_color=MATRIX_GREEN_BORDER, checkmark_color=MATRIX_BLACK)
        self.alertCaveButton.grid(column=1, row=0, sticky='nsew', padx=10, pady=10)

        self.alertSayPlayerCheckVar = tk.BooleanVar()
        # self.alertSayPlayerCheckVar.set(self.context.context['alert']['sayPlayer']) # REMOVED
        # Renaming the second alertCheckButton to alertSayPlayerCheckButton for clarity if it was a new widget
        # However, the original code reuses self.alertCheckButton. I will assume it means to style the *second instance*
        # of a checkbox that was assigned to self.alertCheckButton
        self.alertSayPlayerCheckButton = customtkinter.CTkCheckBox( # This is the widget for "Enviar ? para Player"
            self.alertFrame, text='Enviar ? para Player', variable=self.alertSayPlayerCheckVar, command=self.onToggleAlertSayPlayer,
            text_color=MATRIX_GREEN, fg_color=MATRIX_GREEN, hover_color=MATRIX_GREEN_HOVER,
            border_color=MATRIX_GREEN_BORDER, checkmark_color=MATRIX_BLACK)
        self.alertSayPlayerCheckButton.grid(column=0, row=1, sticky='nsew', padx=10, pady=10)
        
        self.alertFrame.columnconfigure(0, weight=1)
        self.alertFrame.columnconfigure(1, weight=1)

        self.clearStatsFrame = customtkinter.CTkFrame(self, fg_color=MATRIX_BLACK, border_color=MATRIX_GREEN_BORDER, border_width=1)
        self.clearStatsFrame.grid(column=0, row=2, padx=10,
                            pady=10, sticky='nsew')
        
        self.checkPoisonVar = tk.BooleanVar()
        # self.checkPoisonVar.set(self.context.context['clear_stats']['poison']) # REMOVED
        self.checkPoisonButton = customtkinter.CTkCheckBox(
            self.clearStatsFrame, text='Limpar poison', variable=self.checkPoisonVar, command=self.onTogglePoison,
            text_color=MATRIX_GREEN, fg_color=MATRIX_GREEN, hover_color=MATRIX_GREEN_HOVER,
            border_color=MATRIX_GREEN_BORDER, checkmark_color=MATRIX_BLACK)
        self.checkPoisonButton.grid(column=0, row=0, sticky='nsew', padx=10, pady=10)
        
        self.poisonLabel = customtkinter.CTkLabel(
            self.clearStatsFrame, text='Poison Hotkey:', text_color=MATRIX_GREEN)
        self.poisonLabel.grid(column=0, row=1, padx=10,
                            pady=10, sticky='nsew')

        self.poisonHotkeyEntryVar = tk.StringVar()
        # self.poisonHotkeyEntryVar.set(self.context.context['clear_stats']['poison_hotkey']) # REMOVED
        self.poisonHotkeyEntry = customtkinter.CTkEntry(self.clearStatsFrame, textvariable=self.poisonHotkeyEntryVar,
                                                        text_color=MATRIX_GREEN, border_color=MATRIX_GREEN_BORDER,
                                                        fg_color=MATRIX_BLACK, insertbackground=MATRIX_GREEN)
        self.poisonHotkeyEntry.bind('<Key>', self.onChangePoisonHotkey)
        self.poisonHotkeyEntry.grid(column=1, row=1, padx=10,
                            pady=10, sticky='nsew')
        
        self.clearStatsFrame.columnconfigure(0, weight=1)
        self.clearStatsFrame.columnconfigure(1, weight=1)

        self.saveConfigFrame = customtkinter.CTkFrame(self, fg_color=MATRIX_BLACK, border_color=MATRIX_GREEN_BORDER, border_width=1)
        self.saveConfigFrame.grid(column=1, row=2, padx=10,
                            pady=10, sticky='nsew')

        saveConfigButton = customtkinter.CTkButton(self.saveConfigFrame, text="Save Cfg", corner_radius=32,
                                        fg_color="transparent", text_color=MATRIX_GREEN,
                                        border_color=MATRIX_GREEN_BORDER, border_width=2,
                                        hover_color=MATRIX_GREEN_HOVER, command=self.saveCfg)
        saveConfigButton.grid(row=0, column=0, padx=20, pady=20, sticky='nsew')

        loadConfigButton = customtkinter.CTkButton(self.saveConfigFrame, text="Load Cfg", corner_radius=32,
                                        fg_color="transparent", text_color=MATRIX_GREEN,
                                        border_color=MATRIX_GREEN_BORDER, border_width=2,
                                        hover_color=MATRIX_GREEN_HOVER, command=self.loadCfg)
        loadConfigButton.grid(row=0, column=1, padx=20, pady=20, sticky='nsew')
        
        self.saveConfigFrame.columnconfigure(0, weight=1)
        self.saveConfigFrame.columnconfigure(1, weight=1)

    def load_configuration_from_data(self, config_data: dict):
        if not isinstance(config_data, dict):
            print("Error: config_data is not a dictionary") # Or handle more gracefully
            return

        # General Hotkeys
        general_hotkeys = config_data.get('general_hotkeys', {})
        self.shovelHotkeyEntryVar.set(general_hotkeys.get('shovel_hotkey', ''))
        self.ropeHotkeyEntryVar.set(general_hotkeys.get('rope_hotkey', ''))

        # Auto Hur
        auto_hur = config_data.get('auto_hur', {})
        self.checkVar.set(auto_hur.get('enabled', False))
        self.checkPzVar.set(auto_hur.get('pz', False))
        current_hur_spell = auto_hur.get('spell', '')
        if current_hur_spell in self.hurSpellCombobox.cget("values"): # Ensure value is valid for combobox
            self.hurSpellCombobox.set(current_hur_spell)
        elif len(self.hurSpellCombobox.cget("values")) > 0: # Set to first if current is invalid/empty
             self.hurSpellCombobox.set(self.hurSpellCombobox.cget("values")[0])
        self.autoHurHotkeyEntryVar.set(auto_hur.get('hotkey', ''))

        # Alert
        alert = config_data.get('alert', {})
        self.alertCheckVar.set(alert.get('enabled', False))
        self.alertCaveCheckVar.set(alert.get('cave', False))
        self.alertSayPlayerCheckVar.set(alert.get('sayPlayer', False))

        # Clear Stats
        clear_stats = config_data.get('clear_stats', {})
        self.checkPoisonVar.set(clear_stats.get('poison', False))
        self.poisonHotkeyEntryVar.set(clear_stats.get('poison_hotkey', ''))
        
        # Window Title (Game Window)
        window_title = config_data.get('window_title', '')
        # We need to ensure the window_title is in the list of available windows first
        # For now, just setting it. If it's not in values, ComboBox might not show it.
        # Or, refresh windows list and then set if title is in the new list.
        # self.refreshWindows() # This might trigger onChangeWindow if not careful
        current_windows = self.windowsCombobox.cget("values")
        if window_title and window_title in current_windows:
            self.windowsCombobox.set(window_title)
        elif window_title and not current_windows: # If list is empty, add it
            self.windowsCombobox.configure(values=[window_title])
            self.windowsCombobox.set(window_title)
        elif window_title: # If list is not empty but title not in it, append and set
            self.windowsCombobox.configure(values=current_windows + [window_title])
            self.windowsCombobox.set(window_title)
        # If window_title is empty or not in list, it will default to current or first

    def getGameWindows(self):
        def enum_windows_callback(hwnd, results):
            if win32gui.IsWindowVisible(hwnd):
                window_title = win32gui.GetWindowText(hwnd)
                if re.search(r"Windowed", window_title, re.IGNORECASE):
                    results.append(window_title)
        results = []
        win32gui.EnumWindows(enum_windows_callback, results)
        return results

    def refreshWindows(self):
        self.windowsCombobox['values'] = self.getGameWindows()

    def onChangeWindow(self, _):
        title = self.windowsCombobox.get()
        if self.ws_client: 
            self.ws_client.send_message({"command": "config_set_game_window", "payload": {"window_title": title}})
        
    def onChangeShovelHotkey(self, event):
        key = event.char
        key_pressed = event.keysym
        key_to_send = key_pressed
        if key == '\b':
            return
        if re.match(r'^F[1-9]|1[0-2]$', key) or re.match(r'^[0-9]$', key) or re.match(r'^[a-z]$', key):
            self.shovelHotkeyEntry.delete(0, tk.END)
            key_to_send = key
        
        if self.ws_client: 
            self.ws_client.send_message({"command": "config_set_hotkey", "payload": {"hotkey_type": "shovel", "key": key_to_send}})
        self.shovelHotkeyEntryVar.set(key_to_send)


    def onChangeRopeHotkey(self, event):
        key = event.char
        key_pressed = event.keysym
        key_to_send = key_pressed
        if key == '\b':
            return
        if re.match(r'^F[1-9]|1[0-2]$', key) or re.match(r'^[0-9]$', key) or re.match(r'^[a-z]$', key):
            self.ropeHotkeyEntry.delete(0, tk.END)
            key_to_send = key

        if self.ws_client: 
            self.ws_client.send_message({"command": "config_set_hotkey", "payload": {"hotkey_type": "rope", "key": key_to_send}})
        self.ropeHotkeyEntryVar.set(key_to_send)

    def onChangeAutoHurHotkey(self, event):
        key = event.char
        key_pressed = event.keysym
        key_to_send = key_pressed
        if key == '\b':
            return
        if re.match(r'^F[1-9]|1[0-2]$', key) or re.match(r'^[0-9]$', key) or re.match(r'^[a-z]$', key):
            self.autoHurHotkeyEntry.delete(0, tk.END)
            key_to_send = key

        if self.ws_client: 
            self.ws_client.send_message({"command": "config_set_hotkey", "payload": {"hotkey_type": "auto_hur", "key": key_to_send}})
        self.autoHurHotkeyEntryVar.set(key_to_send)

    def onChangePoisonHotkey(self, event):
        key = event.char
        key_pressed = event.keysym
        key_to_send = key_pressed
        if key == '\b':
            return
        if re.match(r'^F[1-9]|1[0-2]$', key) or re.match(r'^[0-9]$', key) or re.match(r'^[a-z]$', key):
            self.poisonHotkeyEntry.delete(0, tk.END)
            key_to_send = key
            
        if self.ws_client: 
            self.ws_client.send_message({"command": "config_set_hotkey", "payload": {"hotkey_type": "poison", "key": key_to_send}})
        self.poisonHotkeyEntryVar.set(key_to_send)

    def onToggleAutoHur(self):
        enabled = self.checkVar.get()
        if self.ws_client: 
            self.ws_client.send_message({"command": "config_toggle_feature", "payload": {"feature_name": "auto_hur_enabled", "enabled": enabled}})
        
    def onToggleAutoHurPz(self):
        enabled = self.checkPzVar.get()
        if self.ws_client: 
            self.ws_client.send_message({"command": "config_toggle_feature", "payload": {"feature_name": "auto_hur_pz", "enabled": enabled}})

    def onToggleAlert(self):
        enabled = self.alertCheckVar.get()
        if self.ws_client: 
            self.ws_client.send_message({"command": "config_toggle_feature", "payload": {"feature_name": "alert_enabled", "enabled": enabled}})
        
    def onToggleAlertCave(self):
        enabled = self.alertCaveCheckVar.get()
        if self.ws_client: 
            self.ws_client.send_message({"command": "config_toggle_feature", "payload": {"feature_name": "alert_cave", "enabled": enabled}})

    def onToggleAlertSayPlayer(self):
        enabled = self.alertSayPlayerCheckVar.get()
        if self.ws_client: 
            self.ws_client.send_message({"command": "config_toggle_feature", "payload": {"feature_name": "alert_say_player", "enabled": enabled}})

    def onTogglePoison(self):
        enabled = self.checkPoisonVar.get()
        if self.ws_client: 
            self.ws_client.send_message({"command": "config_toggle_feature", "payload": {"feature_name": "clear_stats_poison", "enabled": enabled}})

    def setHurSpell(self, _):
        spell_name = self.hurSpellCombobox.get()
        if self.ws_client: 
            self.ws_client.send_message({"command": "config_set_auto_hur_spell", "payload": {"spell_name": spell_name}})

    def saveCfg(self):
        cfg_payload = {
            "window_title": self.windowsCombobox.get(),
            "general_hotkeys": {
                "shovel_hotkey": self.shovelHotkeyEntryVar.get(),
                "rope_hotkey": self.ropeHotkeyEntryVar.get()
            },
            "auto_hur": {
                "enabled": self.checkVar.get(),
                "pz": self.checkPzVar.get(),
                "spell": self.hurSpellCombobox.get(),
                "hotkey": self.autoHurHotkeyEntryVar.get()
            },
            "alert": {
                "enabled": self.alertCheckVar.get(),
                "cave": self.alertCaveCheckVar.get(),
                "sayPlayer": self.alertSayPlayerCheckVar.get()
            },
            "clear_stats": {
                "poison": self.checkPoisonVar.get(),
                "poison_hotkey": self.poisonHotkeyEntryVar.get()
            }
        }
        if self.ws_client:
            self.ws_client.send_message({"command": "config_save_settings", "payload": cfg_payload})
            messagebox.showinfo('Sucesso', 'Configurações enviadas para o backend!')
        else:
            messagebox.showerror('Erro', 'Cliente WebSocket não disponível.')

    def _collect_config_data_from_ui(self) -> dict:
        cfg_payload = {
            "window_title": self.windowsCombobox.get(),
            "general_hotkeys": {
                "shovel_hotkey": self.shovelHotkeyEntryVar.get(),
                "rope_hotkey": self.ropeHotkeyEntryVar.get()
            },
            "auto_hur": {
                "enabled": self.checkVar.get(),
                "pz": self.checkPzVar.get(),
                "spell": self.hurSpellCombobox.get(),
                "hotkey": self.autoHurHotkeyEntryVar.get()
            },
            "alert": {
                "enabled": self.alertCheckVar.get(),
                "cave": self.alertCaveCheckVar.get(),
                "sayPlayer": self.alertSayPlayerCheckVar.get()
            },
            "clear_stats": {
                "poison": self.checkPoisonVar.get(),
                "poison_hotkey": self.poisonHotkeyEntryVar.get()
            }
        }
        return cfg_payload

    def loadCfg(self):
        file = filedialog.askopenfilename(
            defaultextension=".skbcfg",
            filetypes=[("SKB Cfg", "*.skbcfg"), ("Todos os arquivos", "*.*")]
        )

        if file:
            with open(file, 'r') as f:
                cfg = json.load(f)
                # Instead of self.context.loadCfg(cfg), send a message to backend to load and return it
                # This assumes the backend has a command to process this file content
                # For a direct load without backend processing of the file itself:
                # self.load_configuration_from_data(cfg) 
                # messagebox.showinfo('Sucesso', 'Cfg carregada com sucesso localmente!')
                
                # To use WebSocket for loading:
                if self.ws_client:
                    # The backend needs to be able to read this cfg and then send a "config_load_settings" response
                    # This is a placeholder for how it *could* work if backend handles file content
                    # For now, let's assume cfg is the data structure itself
                    self.ws_client.send_message({"command": "config_load_settings_from_ui", "payload": cfg})
                    messagebox.showinfo('Info', 'Load request sent to backend. Waiting for update...')
                else: # Fallback if ws_client is not available (though it should be)
                    self.load_configuration_from_data(cfg)
                    messagebox.showinfo('Sucesso', 'Cfg carregada com sucesso localmente (no WS)!')

            # No longer directly update context, wait for backend to send new config
            # self.context.loadCfg(cfg) 
            # messagebox.showinfo('Sucesso', 'Cfg carregada com sucesso!')