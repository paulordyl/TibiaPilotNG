import re
import tkinter as tk
import customtkinter
from ...theme import MATRIX_BLACK, MATRIX_GREEN, MATRIX_GREEN_HOVER, MATRIX_GREEN_BORDER

class ManaFoodCard(customtkinter.CTkFrame):
    def __init__(self, parent, context):
        super().__init__(parent, fg_color=MATRIX_BLACK, border_color=MATRIX_GREEN_BORDER, border_width=1)
        self.configure(fg_color=MATRIX_BLACK)
        self.context = context
        self.columnconfigure(0, weight=3)
        self.columnconfigure(1, weight=7)
        self.rowconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)
        self.rowconfigure(2, weight=1)
        self.rowconfigure(3, weight=1)

        self.titleLabel = customtkinter.CTkLabel(self, text="Mana food", text_color=MATRIX_GREEN) # Renamed from manaFoodLabel
        self.titleLabel.grid(row=0, column=0, columnspan=2, sticky='ew', padx=10, pady=(10, 5))

        self.checkVar = tk.BooleanVar()
        self.checkVar.set(
            self.context.context['healing']['highPriority']['manaFood']['enabled'])
        self.checkbutton = customtkinter.CTkCheckBox(
            self, text='Enabled', variable=self.checkVar, command=self.onToggleCheckButton,
            text_color=MATRIX_GREEN, fg_color=MATRIX_GREEN, hover_color=MATRIX_GREEN_HOVER,
            border_color=MATRIX_GREEN_BORDER, checkmark_color=MATRIX_BLACK)
        self.checkbutton.grid(column=1, row=1, sticky='e', padx=10, pady=5)

        self.hotkeyDescLabel = customtkinter.CTkLabel( # Renamed from hotkeyLabel
            self, text='Hotkey:', text_color=MATRIX_GREEN)
        self.hotkeyDescLabel.grid(column=0, row=2, padx=10,
                            pady=5, sticky='w')

        self.hotkeyEntryVar = tk.StringVar()
        self.hotkeyEntryVar.set(self.context.context['healing']
                                    ['highPriority']['manaFood']['hotkey'])
        self.hotkeyEntry = customtkinter.CTkEntry(self, textvariable=self.hotkeyEntryVar,
                                                 text_color=MATRIX_GREEN, border_color=MATRIX_GREEN_BORDER,
                                                 fg_color=MATRIX_BLACK, insertbackground=MATRIX_GREEN)
        self.hotkeyEntry.bind('<Key>', self.onChangeHotkey)
        self.hotkeyEntry.grid(column=1, row=2, padx=10,
                            pady=5, sticky='ew')

        self.manaPercentageLessThanOrEqualDescLabel = customtkinter.CTkLabel( # Renamed for clarity
            self, text='Mana % <=:', text_color=MATRIX_GREEN) # Shortened text, original said "HP %"
        self.manaPercentageLessThanOrEqualDescLabel.grid(
            column=0, row=3, sticky='w', padx=10, pady=5)

        self.manaPercentageLessThanOrEqualVar = tk.IntVar()
        self.manaPercentageLessThanOrEqualVar.set(
            self.context.context['healing']['highPriority']['manaFood']['manaPercentageLessThanOrEqual'])
        self.manaPercentageLessThanOrEqualSlider = customtkinter.CTkSlider(self, from_=10, to=100,
                                                        button_color=MATRIX_GREEN_BORDER, button_hover_color=MATRIX_GREEN_HOVER,
                                                        progress_color=MATRIX_GREEN, fg_color=MATRIX_GREEN_BORDER,
                                                        variable=self.manaPercentageLessThanOrEqualVar, command=self.onChangeMana)
        self.manaPercentageLessThanOrEqualSlider.grid(
            column=1, row=3, sticky='ew', padx=10, pady=5)
        
        self.manaPercentageLessThanOrEqualValueLabel = customtkinter.CTkLabel( # Renamed for clarity
            self, textvariable=self.manaPercentageLessThanOrEqualVar, text_color=MATRIX_GREEN)
        self.manaPercentageLessThanOrEqualValueLabel.grid(
            column=1, row=4, sticky='e', padx=10, pady=(0,5))

    def onToggleCheckButton(self):
        self.context.toggleHealingHighPriorityByKey(
            'manaFood', self.checkVar.get())

    def onChangeMana(self, _):
        self.context.setManaFoodHpPercentageLessThanOrEqual(
            self.manaPercentageLessThanOrEqualVar.get())
        
    def onChangeHotkey(self, event):
        key = event.char
        key_pressed = event.keysym
        if key == '\b':
            return
        if re.match(r'^F[1-9]|1[0-2]$', key) or re.match(r'^[0-9]$', key) or re.match(r'^[a-z]$', key):
            self.hotkeyEntry.delete(0, tk.END)
            self.context.setHotkeyHealingHighPriorityByKey('manaFood', key)
        else:
            self.context.setHotkeyHealingHighPriorityByKey('manaFood', key_pressed)
            self.hotkeyEntryVar.set(key_pressed)
