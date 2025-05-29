import tkinter as tk
import customtkinter
import re
from ...theme import MATRIX_BLACK, MATRIX_GREEN, MATRIX_GREEN_HOVER, MATRIX_GREEN_BORDER

class FoodTab(customtkinter.CTkFrame):
    def __init__(self, parent, context):
        super().__init__(parent, fg_color=MATRIX_BLACK) # Set background for the FoodTab frame itself
        self.context = context
        self.configure(fg_color=MATRIX_BLACK) # Ensure the main frame bg is black

        self.columnconfigure(0, weight=1)
        # self.columnconfigure(1, weight=1) # Only one column needed for tabFrame
        self.rowconfigure(0, weight=1)
        # self.rowconfigure(1, weight=1) # Only one row needed for tabFrame

        # tabFrame itself should also be black and can have a border if desired
        self.tabFrame = customtkinter.CTkFrame(self, fg_color=MATRIX_BLACK) # border_color=MATRIX_GREEN_BORDER, border_width=1
        self.tabFrame.grid(row=0, column=0, rowspan=2, padx=10, pady=10, sticky="nsew")
        self.tabFrame.columnconfigure(0, weight=1) # For hotkeyLabel
        self.tabFrame.columnconfigure(1, weight=1) # For hotkeyEntry and checkbutton
        # self.tabFrame.rowconfigure(0, weight=1) # For checkbutton (aligned to top of its cell)
        # self.tabFrame.rowconfigure(1, weight=1) # For hotkeyLabel and hotkeyEntry

        self.checkVar = tk.BooleanVar()
        self.checkVar.set(
            self.context.context['healing']['eatFood']['enabled'])
        self.checkbutton = customtkinter.CTkCheckBox(
            self.tabFrame, text='Enabled', variable=self.checkVar, command=self.onToggleCheckButton,
            text_color=MATRIX_GREEN, fg_color=MATRIX_GREEN, hover_color=MATRIX_GREEN_HOVER,
            border_color=MATRIX_GREEN_BORDER, checkmark_color=MATRIX_BLACK)
        self.checkbutton.grid(column=1, row=0, sticky='e', pady=(10, 0), padx=10)

        self.hotkeyLabel = customtkinter.CTkLabel(
            self.tabFrame, text='Hotkey:', text_color=MATRIX_GREEN)
        self.hotkeyLabel.grid(column=0, row=1, padx=10,
                            pady=10, sticky='nsew')

        self.hotkeyEntryVar = tk.StringVar()
        self.hotkeyEntryVar.set(self.context.context['healing']['eatFood']['hotkey'])
        self.hotkeyEntry = customtkinter.CTkEntry(self.tabFrame, textvariable=self.hotkeyEntryVar,
                                                 text_color=MATRIX_GREEN, border_color=MATRIX_GREEN_BORDER,
                                                 fg_color=MATRIX_BLACK, insertbackground=MATRIX_GREEN)
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