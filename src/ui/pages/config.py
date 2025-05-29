import pygetwindow as gw
import re
import win32gui
import customtkinter
import tkinter as tk
from ..utils import genRanStr
from tkinter import filedialog, messagebox
import json

class ConfigPage(customtkinter.CTkToplevel):
    def __init__(self, context):
        super().__init__()
        self.context = context

        self.title(genRanStr())
        self.resizable(False, False)

        self.windowsFrame = customtkinter.CTkFrame(self)
        self.windowsFrame.grid(column=0, row=0, padx=10,
                            pady=10, sticky='nsew')

        self.windowsFrame.rowconfigure(0, weight=1)
        self.windowsFrame.columnconfigure(0, weight=1)

        self.tibiaWindowLabel = customtkinter.CTkLabel(self.windowsFrame, text="Game Window:")
        self.tibiaWindowLabel.grid(row=0, column=0, sticky='w', padx=10, pady=(10, 0))

        self.windowsCombobox = customtkinter.CTkComboBox(
            self.windowsFrame, values=self.getGameWindows(), state='readonly',
            command=self.onChangeWindow)
        self.windowsCombobox.grid(row=1, column=0, sticky='ew', padx=10, pady=10)

        self.button = customtkinter.CTkButton(
            self.windowsFrame, text='Atualizar', command=self.refreshWindows,
            corner_radius=32, fg_color="transparent", border_color="#C20034",
            border_width=2, hover_color="#C20034")
        self.button.grid(row=1, column=1, padx=10, pady=10)

        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)

        self.shovelRopeFrame = customtkinter.CTkFrame(self)
        self.shovelRopeFrame.grid(column=1, row=0, padx=10,
                            pady=10, sticky='nsew')

        self.shovelHotkeyLabel = customtkinter.CTkLabel(
            self.shovelRopeFrame, text='Shovel Hotkey:')
        self.shovelHotkeyLabel.grid(column=0, row=0, padx=10,
                            pady=10, sticky='nsew')

        self.shovelHotkeyEntryVar = tk.StringVar()
        self.shovelHotkeyEntryVar.set(self.context.context['general_hotkeys']['shovel_hotkey'])
        self.shovelHotkeyEntry = customtkinter.CTkEntry(self.shovelRopeFrame, textvariable=self.shovelHotkeyEntryVar)
        self.shovelHotkeyEntry.bind('<Key>', self.onChangeShovelHotkey)
        self.shovelHotkeyEntry.grid(column=1, row=0, padx=10,
                            pady=10, sticky='nsew')
        
        self.ropeHotkeyLabel = customtkinter.CTkLabel(
            self.shovelRopeFrame, text='Rope Hotkey:')
        self.ropeHotkeyLabel.grid(column=0, row=1, padx=10,
                            pady=10, sticky='nsew')

        self.ropeHotkeyEntryVar = tk.StringVar()
        self.ropeHotkeyEntryVar.set(self.context.context['general_hotkeys']['rope_hotkey'])
        self.ropeHotkeyEntry = customtkinter.CTkEntry(self.shovelRopeFrame, textvariable=self.ropeHotkeyEntryVar)
        self.ropeHotkeyEntry.bind('<Key>', self.onChangeRopeHotkey)
        self.ropeHotkeyEntry.grid(column=1, row=1, padx=10,
                            pady=10, sticky='nsew')
        
        self.shovelRopeFrame.columnconfigure(0, weight=1)
        self.shovelRopeFrame.columnconfigure(1, weight=1)

        self.autoHurFrame = customtkinter.CTkFrame(self)
        self.autoHurFrame.grid(column=0, row=1, padx=10,
                            pady=10, sticky='nsew')
        
        self.checkVar = tk.BooleanVar()
        self.checkVar.set(
            self.context.context['auto_hur']['enabled'])
        self.checkbutton = customtkinter.CTkCheckBox(
            self.autoHurFrame, text='Enabled', variable=self.checkVar, command=self.onToggleAutoHur,
            hover_color="#870125", fg_color='#C20034')
        self.checkbutton.grid(column=0, row=0, sticky='nsew', padx=10, pady=10)

        self.checkPzVar = tk.BooleanVar()
        self.checkPzVar.set(
            self.context.context['auto_hur']['pz'])
        self.checkpzbutton = customtkinter.CTkCheckBox(
            self.autoHurFrame, text='Usar em PZ', variable=self.checkPzVar, command=self.onToggleAutoHurPz,
            hover_color="#870125", fg_color='#C20034')
        self.checkpzbutton.grid(column=1, row=0, sticky='nsew', padx=10, pady=10)

        self.autoHurSpellLabel = customtkinter.CTkLabel(
            self.autoHurFrame, text='Spell:')
        self.autoHurSpellLabel.grid(column=0, row=1, padx=10,
                            pady=10, sticky='nsew')

        self.hurSpellCombobox = customtkinter.CTkComboBox(
            self.autoHurFrame, values=['utani hur', 'utani gran hur', 'utani tempo hur', 'utamo tempo san'], state='readonly',
            command=self.setHurSpell)
        if self.context.enabledProfile is not None and self.context.enabledProfile['config']['auto_hur']['spell'] is not None:
            self.hurSpellCombobox.set(
                self.context.enabledProfile['config']['auto_hur']['spell'])
        self.hurSpellCombobox.grid(row=1, column=1, padx=10, pady=10, sticky='nsew')
        
        self.autoHurLabel = customtkinter.CTkLabel(
            self.autoHurFrame, text='AutoHur Hotkey:')
        self.autoHurLabel.grid(column=0, row=2, padx=10,
                            pady=10, sticky='nsew')

        self.autoHurHotkeyEntryVar = tk.StringVar()
        self.autoHurHotkeyEntryVar.set(self.context.context['auto_hur']['hotkey'])
        self.autoHurHotkeyEntry = customtkinter.CTkEntry(self.autoHurFrame, textvariable=self.autoHurHotkeyEntryVar)
        self.autoHurHotkeyEntry.bind('<Key>', self.onChangeAutoHurHotkey)
        self.autoHurHotkeyEntry.grid(column=1, row=2, padx=10,
                            pady=10, sticky='nsew')
        
        self.autoHurFrame.columnconfigure(0, weight=1)
        self.autoHurFrame.columnconfigure(1, weight=1)

        self.alertFrame = customtkinter.CTkFrame(self)
        self.alertFrame.grid(column=1, row=1, padx=10,
                            pady=10, sticky='nsew')
        
        self.alertCheckVar = tk.BooleanVar()
        self.alertCheckVar.set(
            self.context.context['alert']['enabled'])
        self.alertCheckButton = customtkinter.CTkCheckBox(
            self.alertFrame, text='Alert Enabled', variable=self.alertCheckVar, command=self.onToggleAlert,
            hover_color="#870125", fg_color='#C20034')
        self.alertCheckButton.grid(column=0, row=0, sticky='nsew', padx=10, pady=10)

        self.alertCaveCheckVar = tk.BooleanVar()
        self.alertCaveCheckVar.set(
            self.context.context['alert']['cave'])
        self.alertCaveButton = customtkinter.CTkCheckBox(
            self.alertFrame, text='Apenas cave ativo', variable=self.alertCaveCheckVar, command=self.onToggleAlertCave,
            hover_color="#870125", fg_color='#C20034')
        self.alertCaveButton.grid(column=1, row=0, sticky='nsew', padx=10, pady=10)

        self.alertSayPlayerCheckVar = tk.BooleanVar()
        self.alertSayPlayerCheckVar.set(
            self.context.context['alert']['sayPlayer'])
        self.alertCheckButton = customtkinter.CTkCheckBox(
            self.alertFrame, text='Enviar ? para Player', variable=self.alertSayPlayerCheckVar, command=self.onToggleAlertSayPlayer,
            hover_color="#870125", fg_color='#C20034')
        self.alertCheckButton.grid(column=0, row=1, sticky='nsew', padx=10, pady=10)
        
        self.alertFrame.columnconfigure(0, weight=1)
        self.alertFrame.columnconfigure(1, weight=1)

        self.clearStatsFrame = customtkinter.CTkFrame(self)
        self.clearStatsFrame.grid(column=0, row=2, padx=10,
                            pady=10, sticky='nsew')
        
        self.checkPoisonVar = tk.BooleanVar()
        self.checkPoisonVar.set(
            self.context.context['clear_stats']['poison'])
        self.checkPoisonButton = customtkinter.CTkCheckBox(
            self.clearStatsFrame, text='Limpar poison', variable=self.checkPoisonVar, command=self.onTogglePoison,
            hover_color="#870125", fg_color='#C20034')
        self.checkPoisonButton.grid(column=0, row=0, sticky='nsew', padx=10, pady=10)
        
        self.poisonLabel = customtkinter.CTkLabel(
            self.clearStatsFrame, text='Poison Hotkey:')
        self.poisonLabel.grid(column=0, row=1, padx=10,
                            pady=10, sticky='nsew')

        self.poisonHotkeyEntryVar = tk.StringVar()
        self.poisonHotkeyEntryVar.set(self.context.context['clear_stats']['poison_hotkey'])
        self.poisonHotkeyEntry = customtkinter.CTkEntry(self.clearStatsFrame, textvariable=self.poisonHotkeyEntryVar)
        self.poisonHotkeyEntry.bind('<Key>', self.onChangePoisonHotkey)
        self.poisonHotkeyEntry.grid(column=1, row=1, padx=10,
                            pady=10, sticky='nsew')
        
        self.clearStatsFrame.columnconfigure(0, weight=1)
        self.clearStatsFrame.columnconfigure(1, weight=1)

        self.saveConfigFrame = customtkinter.CTkFrame(self)
        self.saveConfigFrame.grid(column=1, row=2, padx=10,
                            pady=10, sticky='nsew')

        saveConfigButton = customtkinter.CTkButton(self.saveConfigFrame, text="Save Cfg", corner_radius=32,
                                        fg_color="transparent", border_color="#C20034",
                                        border_width=2, hover_color="#C20034", command=self.saveCfg)
        saveConfigButton.grid(row=0, column=0, padx=20, pady=20, sticky='nsew')

        loadConfigButton = customtkinter.CTkButton(self.saveConfigFrame, text="Load Cfg", corner_radius=32,
                                        fg_color="transparent", border_color="#C20034",
                                        border_width=2, hover_color="#C20034", command=self.loadCfg)
        loadConfigButton.grid(row=0, column=1, padx=20, pady=20, sticky='nsew')
        
        self.saveConfigFrame.columnconfigure(0, weight=1)
        self.saveConfigFrame.columnconfigure(1, weight=1)

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
        selectedWindow = self.windowsCombobox.get()
        self.context.context['window'] = gw.getWindowsWithTitle(selectedWindow)[
            0]
        
    def onChangeShovelHotkey(self, event):
        key = event.char
        key_pressed = event.keysym
        if key == '\b':
            return
        if re.match(r'^F[1-9]|1[0-2]$', key) or re.match(r'^[0-9]$', key) or re.match(r'^[a-z]$', key):
            self.shovelHotkeyEntry.delete(0, tk.END)
            self.context.setShovelHotkey(key)
        else:
            self.context.setShovelHotkey(key_pressed)
            self.shovelHotkeyEntryVar.set(key_pressed)

    def onChangeRopeHotkey(self, event):
        key = event.char
        key_pressed = event.keysym
        if key == '\b':
            return
        if re.match(r'^F[1-9]|1[0-2]$', key) or re.match(r'^[0-9]$', key) or re.match(r'^[a-z]$', key):
            self.ropeHotkeyEntry.delete(0, tk.END)
            self.context.setRopeHotkey(key)
        else:
            self.context.setRopeHotkey(key_pressed)
            self.ropeHotkeyEntryVar.set(key_pressed)

    def onChangeAutoHurHotkey(self, event):
        key = event.char
        key_pressed = event.keysym
        if key == '\b':
            return
        if re.match(r'^F[1-9]|1[0-2]$', key) or re.match(r'^[0-9]$', key) or re.match(r'^[a-z]$', key):
            self.autoHurHotkeyEntry.delete(0, tk.END)
            self.context.setAutoHurHotkey(key)
        else:
            self.context.setAutoHurHotkey(key_pressed)
            self.autoHurHotkeyEntryVar.set(key_pressed)

    def onChangePoisonHotkey(self, event):
        key = event.char
        key_pressed = event.keysym
        if key == '\b':
            return
        if re.match(r'^F[1-9]|1[0-2]$', key) or re.match(r'^[0-9]$', key) or re.match(r'^[a-z]$', key):
            self.poisonHotkeyEntry.delete(0, tk.END)
            self.context.setClearStatsPoisonHotkey(key)
        else:
            self.context.setClearStatsPoisonHotkey(key_pressed)
            self.poisonHotkeyEntryVar.set(key_pressed)

    def onToggleAutoHur(self):
        self.context.toggleAutoHur(self.checkVar.get())
        
    def onToggleAutoHurPz(self):
        self.context.toggleAutoHurPz(self.checkPzVar.get())

    def onToggleAlert(self):
        self.context.toggleAlert(self.alertCheckVar.get())
        
    def onToggleAlertCave(self):
        self.context.toggleAlertCave(self.alertCaveCheckVar.get())

    def onToggleAlertSayPlayer(self):
        self.context.toggleAlertSayPlayer(self.alertSayPlayerCheckVar.get())

    def onTogglePoison(self):
        self.context.toggleClearStatsPoison(self.checkPoisonVar.get())

    def setHurSpell(self, _):
        self.context.setAutoHurSpell(self.hurSpellCombobox.get())

    def saveCfg(self):
        file = filedialog.asksaveasfilename(
            defaultextension=".skbcfg",
            filetypes=[("SKB Cfg", "*.skbcfg"), ("Todos os arquivos", "*.*")]
        )

        if file:
            cfg = {
                'py_backpacks': self.context.context['py_backpacks'],
                'general_hotkeys': self.context.context['general_hotkeys'],
                'auto_hur': self.context.context['auto_hur'],
                'alert': self.context.context['alert'],
                'clear_stats': self.context.context['clear_stats'],
                'py_comboSpells': self.context.context['py_comboSpells'],
                'healing': self.context.context['healing']
            }
            with open(file, 'w') as f:
                json.dump(cfg, f, indent=4)
            messagebox.showinfo('Sucesso', 'Cfg salva com sucesso!')

    def loadCfg(self):
        file = filedialog.askopenfilename(
            defaultextension=".skbcfg",
            filetypes=[("SKB Cfg", "*.skbcfg"), ("Todos os arquivos", "*.*")]
        )

        if file:
            with open(file, 'r') as f:
                cfg = json.load(f)
                self.context.loadCfg(cfg)
            messagebox.showinfo('Sucesso', 'Cfg carregada com sucesso!')