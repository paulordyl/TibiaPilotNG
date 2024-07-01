import customtkinter
from tkinter import StringVar, END
import re
from ..utils import genRanStr

class ComboSpellModal(customtkinter.CTkToplevel):
    def __init__(self, parent, spell=None, context=None, index=None, indexSecond=None):
        super().__init__(parent)
        self.context = context
        self.index = index
        self.indexSecond = indexSecond

        self.title(genRanStr())
        self.resizable(False, False)

        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)

        self.frame = customtkinter.CTkFrame(self)
        self.frame.grid(column=0, row=0, columnspan=2, padx=10,
                        pady=10, sticky='nsew')
        self.frame.rowconfigure(0, weight=1)
        self.frame.rowconfigure(1, weight=1)

        self.label = customtkinter.CTkLabel(self.frame, text="Name:")
        self.label.grid(row=0, column=0, sticky='w', padx=10, pady=(10, 0))

        self.spellsCombobox = customtkinter.CTkComboBox(
            self.frame, values=['utito tempo', 'utamo tempo', 'exori', 'exori gran', 'exori mas', 'exori min', 'exeta amp res', 'exeta res'], state='readonly',
            command=self.onChangeSpell)
        if spell is not None:
            self.spellsCombobox.set(spell['name'])
        self.spellsCombobox.grid(column=0, row=1, sticky='ew', padx=10, pady=10)

        self.hotkeyLabel = customtkinter.CTkLabel(
            self.frame, text='Hotkey:')
        self.hotkeyLabel.grid(column=0, row=2, padx=10,
                            pady=10, sticky='w')

        self.hotkeyEntryVar = StringVar()
        self.hotkeyEntryVar.set(spell['hotkey'])
        self.hotkeyEntry = customtkinter.CTkEntry(self.frame, textvariable=self.hotkeyEntryVar)
        self.hotkeyEntry.bind('<Key>', self.onChangeHotkey)
        self.hotkeyEntry.grid(column=0, row=3, padx=10,
                            pady=10, sticky='nsew')

        self.confirmButton = customtkinter.CTkButton(
            self, text='Confirm', command=self.confirm,
            corner_radius=32, fg_color="transparent", border_color="#C20034",
            border_width=2, hover_color="#C20034")
        self.confirmButton.grid(
            row=6, column=0, padx=(10, 5), pady=(5, 10), sticky='nsew')

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