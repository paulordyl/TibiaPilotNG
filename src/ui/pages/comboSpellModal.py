import customtkinter
from tkinter import StringVar, END
import re
from ..utils import genRanStr
from ..theme import MATRIX_BLACK, MATRIX_GREEN, MATRIX_GREEN_HOVER, MATRIX_GREEN_BORDER

class ComboSpellModal(customtkinter.CTkToplevel):
    def __init__(self, parent, spell=None, context=None, index=None, indexSecond=None):
        super().__init__(parent)
        self.configure(fg_color=MATRIX_BLACK)
        self.context = context
        self.index = index
        self.indexSecond = indexSecond

        self.title(genRanStr())
        self.resizable(False, False)

        self.columnconfigure(0, weight=1) # Only one column needed for buttons if confirm is alone or they stack
        # self.columnconfigure(1, weight=1) # Not needed if confirm is centered or buttons stack

        frame_args = {"fg_color": MATRIX_BLACK, "border_color": MATRIX_GREEN_BORDER, "border_width": 1}
        label_args = {"text_color": MATRIX_GREEN}
        combobox_args = {"state": 'readonly', "text_color": MATRIX_GREEN, "border_color": MATRIX_GREEN_BORDER, "fg_color": MATRIX_BLACK, "button_color": MATRIX_GREEN_BORDER, "button_hover_color": MATRIX_GREEN_HOVER, "dropdown_fg_color": MATRIX_BLACK, "dropdown_hover_color": MATRIX_GREEN_HOVER, "dropdown_text_color": MATRIX_GREEN}
        entry_args = {"text_color": MATRIX_GREEN, "border_color": MATRIX_GREEN_BORDER, "fg_color": MATRIX_BLACK, "insertbackground": MATRIX_GREEN}
        button_args = {"corner_radius": 32, "fg_color": "transparent", "text_color": MATRIX_GREEN, "border_color": MATRIX_GREEN_BORDER, "border_width": 2, "hover_color": MATRIX_GREEN_HOVER}

        self.frame = customtkinter.CTkFrame(self, **frame_args)
        self.frame.grid(column=0, row=0, columnspan=2, padx=10, pady=10, sticky='nsew') # columnspan 2 if buttons side-by-side
        self.frame.columnconfigure(0, weight=1) # Allow widgets to expand

        self.nameDescLabel = customtkinter.CTkLabel(self.frame, text="Name:", **label_args) # Renamed from self.label
        self.nameDescLabel.grid(row=0, column=0, sticky='w', padx=10, pady=(10, 0))

        self.spellsCombobox = customtkinter.CTkComboBox(
            self.frame, values=['utito tempo', 'utamo tempo', 'exori', 'exori gran', 'exori mas', 'exori min', 'exeta amp res', 'exeta res'], 
            command=self.onChangeSpell, **combobox_args)
        if spell is not None:
            self.spellsCombobox.set(spell['name'])
        self.spellsCombobox.grid(column=0, row=1, sticky='ew', padx=10, pady=10)

        self.hotkeyDescLabel = customtkinter.CTkLabel(self.frame, text='Hotkey:', **label_args) # Renamed
        self.hotkeyDescLabel.grid(column=0, row=2, padx=10, pady=(10, 0), sticky='w') # pady changed

        self.hotkeyEntryVar = StringVar()
        if spell is not None: # Ensure spell is not None before accessing its hotkey
            self.hotkeyEntryVar.set(spell['hotkey'])
        self.hotkeyEntry = customtkinter.CTkEntry(self.frame, textvariable=self.hotkeyEntryVar, **entry_args)
        self.hotkeyEntry.bind('<Key>', self.onChangeHotkey)
        self.hotkeyEntry.grid(column=0, row=3, padx=10, pady=10, sticky='ew') # sticky changed

        self.confirmButton = customtkinter.CTkButton(
            self, text='Confirm', command=self.confirm, **button_args)
        # Grid confirm button below the frame, centered if no cancel button or adjust as needed
        self.confirmButton.grid(row=1, column=0, columnspan=2, padx=10, pady=(5, 10), sticky='ew') # columnspan 2 to center

    def onChangeHotkey(self, event):
      key = event.char
      key_pressed = event.keysym
      if key == '\b':
        return
      if re.match(r'^F[1-9]|1[0-2]$', key) or re.match(r'^[0-9]$', key) or re.match(r'^[a-z]$', key):
        self.hotkeyEntry.delete(0, END)
        self.context.setComboSpellHotkey(key, index=self.index, indexSecond=self.indexSecond)
      else:
        self.context.setComboSpellHotkey(key_pressed, index=self.index, indexSecond=self.indexSecond)
        self.hotkeyEntryVar.set(key_pressed)

    def onChangeSpell(self, _):
        selectedSpellName = self.spellsCombobox.get()
        self.context.setComboSpellName(selectedSpellName, index=self.index, indexSecond=self.indexSecond)

    def confirm(self):
      self.destroy()