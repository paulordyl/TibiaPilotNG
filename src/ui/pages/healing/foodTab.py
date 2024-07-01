import tkinter as tk
import customtkinter
import re

class FoodTab(customtkinter.CTkFrame):
    def __init__(self, parent, context):
        super().__init__(parent)
        self.context = context
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self.rowconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

        self.tabFrame = customtkinter.CTkFrame(self)
        self.tabFrame.grid(row=0, column=0, rowspan=2, padx=10, pady=10, sticky="nsew")
        self.tabFrame.rowconfigure(0, weight=1)
        self.tabFrame.columnconfigure(0, weight=1)

        self.checkVar = tk.BooleanVar()
        self.checkVar.set(
            self.context.context['healing']['eatFood']['enabled'])
        self.checkbutton = customtkinter.CTkCheckBox(
            self.tabFrame, text='Enabled', variable=self.checkVar, command=self.onToggleCheckButton,
            hover_color="#870125", fg_color='#C20034')
        self.checkbutton.grid(column=1, row=0, sticky='e', pady=(10, 0))

        self.hotkeyLabel = customtkinter.CTkLabel(
            self.tabFrame, text='Hotkey:')
        self.hotkeyLabel.grid(column=0, row=1, padx=10,
                            pady=10, sticky='nsew')

        self.hotkeyEntryVar = tk.StringVar()
        self.hotkeyEntryVar.set(self.context.context['healing']['eatFood']['hotkey'])
        self.hotkeyEntry = customtkinter.CTkEntry(self.tabFrame, textvariable=self.hotkeyEntryVar)
        self.hotkeyEntry.bind('<Key>', self.onChangeHotkey)
        self.hotkeyEntry.grid(column=1, row=1, padx=10,
                            pady=10, sticky='nsew')

    def onToggleCheckButton(self):
        self.context.toggleFoodByKey(self.checkVar.get())

    def onChangeHotkey(self, event):
        key = event.char
        key_pressed = event.keysym
        if key == '\b':
            return
        if re.match(r'^F[1-9]|1[0-2]$', key) or re.match(r'^[0-9]$', key) or re.match(r'^[a-z]$', key):
            self.hotkeyEntry.delete(0, tk.END)
            self.context.setFoodHotkey(key)
        else:
            self.context.setFoodHotkey(key_pressed)
            self.hotkeyEntryVar.set(key_pressed)