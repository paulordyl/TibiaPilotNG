import tkinter as tk
import re
import customtkinter
from tkinter import messagebox

class ManaPotionCard(customtkinter.CTkFrame):
    def __init__(self, parent, context, healthPotionType, title=''):
        super().__init__(parent)
        self.context = context
        self.healthPotionType = healthPotionType
        self.columnconfigure(0, weight=3)
        self.columnconfigure(1, weight=7)
        self.rowconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)
        self.rowconfigure(2, weight=1)
        self.rowconfigure(3, weight=1)

        self.healthPotionTitleLabel = customtkinter.CTkLabel(self, text=title)
        self.healthPotionTitleLabel.grid(row=0, column=0, sticky='w', padx=10, pady=(10, 0))

        self.checkVar = tk.BooleanVar()
        self.checkVar.set(self.context.context['healing']
                        ['potions'][healthPotionType]['enabled'])
        self.checkbutton = customtkinter.CTkCheckBox(
            self, text='Enabled', variable=self.checkVar, command=self.onToggleCheckButton,
            hover_color="#870125", fg_color='#C20034')
        self.checkbutton.grid(column=1, row=1, sticky='e')

        self.hotkeyLabel = customtkinter.CTkLabel(
            self, text='Hotkey:')
        self.hotkeyLabel.grid(column=0, row=2, padx=10,
                            pady=10, sticky='nsew')

        self.hotkeyEntryVar = tk.StringVar()
        self.hotkeyEntryVar.set(self.context.context['healing']
                                ['potions'][healthPotionType]['hotkey'])
        self.hotkeyEntry = customtkinter.CTkEntry(self, textvariable=self.hotkeyEntryVar)
        self.hotkeyEntry.bind('<Key>', self.onChangeHotkey)
        self.hotkeyEntry.grid(column=1, row=2, padx=10,
                            pady=10, sticky='nsew')
        
        self.slotLabel = customtkinter.CTkLabel(
            self, text='Slot:')
        self.slotLabel.grid(column=0, row=3, padx=10,
                            pady=10, sticky='nsew')

        self.slotEntryVar = tk.StringVar()
        self.slotEntryVar.set(self.context.context['healing']
                                ['potions'][healthPotionType]['slot'])
        self.slotEntry = customtkinter.CTkEntry(self, textvariable=self.slotEntryVar, validate='key',
                                        validatecommand=(self.register(self.validateNumber), "%P"))
        self.slotEntry.bind('<KeyRelease>', self.onChangeNumber)
        self.slotEntry.grid(column=1, row=3, padx=10,
                            pady=10, sticky='nsew')

        self.manaPercentageLessThenOrEqualLabel = customtkinter.CTkLabel(
            self, text='Mana % less than or equal:')
        self.manaPercentageLessThenOrEqualLabel.grid(
            column=0, row=4, sticky='nsew', padx=(10, 0))

        self.manaPercentageLessThenOrEqualVar = tk.IntVar()
        self.manaPercentageLessThenOrEqualVar.set(self.context.context['healing']
                                                ['potions'][healthPotionType]['manaPercentageLessThanOrEqual'])
        self.manaPercentageLessThenOrEqualSlider = customtkinter.CTkSlider(self, from_=0, to=100,
                                                            button_color='#C20034', button_hover_color='#870125',
                                                            variable=self.manaPercentageLessThenOrEqualVar, command=self.onChangeMana)
        self.manaPercentageLessThenOrEqualSlider.grid(
            column=1, row=4, sticky='ew')
        
        self.manaPercentageLessThenOrEqualLabel = customtkinter.CTkLabel(
            self, textvariable=self.manaPercentageLessThenOrEqualVar)
        self.manaPercentageLessThenOrEqualLabel.grid(
            column=1, row=5, sticky='nsew')

    def onToggleCheckButton(self):
        self.context.toggleHealingPotionsByKey(
            self.healthPotionType, self.checkVar.get())

    def onChangeMana(self, _):
        self.context.setHealthPotionManaPercentageLessThanOrEqual(
            self.healthPotionType, self.manaPercentageLessThenOrEqualVar.get())

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