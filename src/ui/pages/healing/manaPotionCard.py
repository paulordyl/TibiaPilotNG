import tkinter as tk
import re
import customtkinter
from tkinter import messagebox
from ...theme import MATRIX_BLACK, MATRIX_GREEN, MATRIX_GREEN_HOVER, MATRIX_GREEN_BORDER

class ManaPotionCard(customtkinter.CTkFrame):
    def __init__(self, parent, context, healthPotionType, title=''): # healthPotionType is a misnomer from original code, represents potion_type key
        super().__init__(parent, fg_color=MATRIX_BLACK, border_color=MATRIX_GREEN_BORDER, border_width=1)
        self.configure(fg_color=MATRIX_BLACK)
        self.context = context
        self.healthPotionType = healthPotionType # This variable name is kept as is from original code
        self.columnconfigure(0, weight=3)
        self.columnconfigure(1, weight=7)
        self.rowconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)
        self.rowconfigure(2, weight=1)
        self.rowconfigure(3, weight=1)

        self.potionTitleLabel = customtkinter.CTkLabel(self, text=title, text_color=MATRIX_GREEN) # Renamed for clarity from healthPotionTitleLabel
        self.potionTitleLabel.grid(row=0, column=0, columnspan=2, sticky='ew', padx=10, pady=(10, 5))

        self.checkVar = tk.BooleanVar()
        self.checkVar.set(self.context.context['healing']
                        ['potions'][healthPotionType]['enabled'])
        self.checkbutton = customtkinter.CTkCheckBox(
            self, text='Enabled', variable=self.checkVar, command=self.onToggleCheckButton,
            text_color=MATRIX_GREEN, fg_color=MATRIX_GREEN, hover_color=MATRIX_GREEN_HOVER,
            border_color=MATRIX_GREEN_BORDER, checkmark_color=MATRIX_BLACK)
        self.checkbutton.grid(column=1, row=1, sticky='e', padx=10, pady=5)

        self.hotkeyLabel = customtkinter.CTkLabel(
            self, text='Hotkey:', text_color=MATRIX_GREEN)
        self.hotkeyLabel.grid(column=0, row=2, padx=10,
                            pady=5, sticky='w')

        self.hotkeyEntryVar = tk.StringVar()
        self.hotkeyEntryVar.set(self.context.context['healing']
                                ['potions'][healthPotionType]['hotkey'])
        self.hotkeyEntry = customtkinter.CTkEntry(self, textvariable=self.hotkeyEntryVar,
                                                 text_color=MATRIX_GREEN, border_color=MATRIX_GREEN_BORDER,
                                                 fg_color=MATRIX_BLACK, insertbackground=MATRIX_GREEN)
        self.hotkeyEntry.bind('<Key>', self.onChangeHotkey)
        self.hotkeyEntry.grid(column=1, row=2, padx=10,
                            pady=5, sticky='ew')
        
        self.slotLabel = customtkinter.CTkLabel(
            self, text='Slot:', text_color=MATRIX_GREEN)
        self.slotLabel.grid(column=0, row=3, padx=10,
                            pady=5, sticky='w')

        self.slotEntryVar = tk.StringVar()
        self.slotEntryVar.set(self.context.context['healing']
                                ['potions'][healthPotionType]['slot'])
        self.slotEntry = customtkinter.CTkEntry(self, textvariable=self.slotEntryVar, validate='key',
                                        validatecommand=(self.register(self.validateNumber), "%P"),
                                        text_color=MATRIX_GREEN, border_color=MATRIX_GREEN_BORDER,
                                        fg_color=MATRIX_BLACK, insertbackground=MATRIX_GREEN)
        self.slotEntry.bind('<KeyRelease>', self.onChangeNumber)
        self.slotEntry.grid(column=1, row=3, padx=10,
                            pady=5, sticky='ew')

        self.manaPercentageLessThanOrEqualDescLabel = customtkinter.CTkLabel( # Renamed for clarity
            self, text='Mana % <=:', text_color=MATRIX_GREEN) # Shortened text
        self.manaPercentageLessThanOrEqualDescLabel.grid(
            column=0, row=4, sticky='w', padx=10, pady=5)

        self.manaPercentageLessThanOrEqualVar = tk.IntVar() # Corrected original typo 'LessThen' to 'LessThan'
        self.manaPercentageLessThanOrEqualVar.set(self.context.context['healing']
                                                ['potions'][healthPotionType]['manaPercentageLessThanOrEqual'])
        self.manaPercentageLessThanOrEqualSlider = customtkinter.CTkSlider(self, from_=0, to=100,
                                                            button_color=MATRIX_GREEN_BORDER, button_hover_color=MATRIX_GREEN_HOVER,
                                                            progress_color=MATRIX_GREEN, fg_color=MATRIX_GREEN_BORDER,
                                                            variable=self.manaPercentageLessThanOrEqualVar, command=self.onChangeMana)
        self.manaPercentageLessThanOrEqualSlider.grid(
            column=1, row=4, padx=10, pady=5, sticky='ew')
        
        self.manaPercentageLessThanOrEqualValueLabel = customtkinter.CTkLabel( # Renamed for clarity
            self, textvariable=self.manaPercentageLessThanOrEqualVar, text_color=MATRIX_GREEN)
        self.manaPercentageLessThanOrEqualValueLabel.grid(
            column=1, row=5, sticky='e', padx=10, pady=(0,5)) # Aligned to the right of slider
        self.manaPercentageLessThanOrEqualValueLabel = customtkinter.CTkLabel( # Renamed for clarity
            self, textvariable=self.manaPercentageLessThanOrEqualVar, text_color=MATRIX_GREEN)
        self.manaPercentageLessThanOrEqualValueLabel.grid( # Corrected original reference to LessThen
            column=1, row=5, sticky='e', padx=10, pady=(0,5)) # Aligned to the right of slider

    def onToggleCheckButton(self):
        self.context.toggleHealingPotionsByKey( # Context method name kept as is
            self.healthPotionType, self.checkVar.get())

    def onChangeMana(self, _):
        self.context.setManaPotionManaPercentageLessThanOrEqual( # Assuming a specific context method for mana potion exists or should exist
            self.healthPotionType, self.manaPercentageLessThanOrEqualVar.get())

    def onChangeHotkey(self, event):
        key = event.char
        key_pressed = event.keysym
        if key == '\b':
            return
        if re.match(r'^F[1-9]|1[0-2]$', key) or re.match(r'^[0-9]$', key) or re.match(r'^[a-z]$', key):
            self.hotkeyEntry.delete(0, tk.END)
            self.context.setHealthPotionHotkeyByKey(self.healthPotionType, key)
        else:
            self.context.setHealthPotionHotkeyByKey(self.healthPotionType, key_pressed)
            self.hotkeyEntryVar.set(key_pressed)

    def onChangeNumber(self, event):
        value = self.slotEntry.get()
        if value.isdigit() and int(value) > 0:
            self.context.setHealthPotionSlotByKey(self.healthPotionType, int(value))

    def validateNumber(self, value: int) -> bool:
        if value == '':
            return True
        if value.isdigit() and int(value) > 0:
            return True
        messagebox.showerror(
            'Error', "Digite um número válido maior que zero.")
        return False