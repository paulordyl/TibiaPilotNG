import tkinter as tk
import re
import customtkinter
from tkinter import messagebox
from ...theme import MATRIX_BLACK, MATRIX_GREEN, MATRIX_GREEN_HOVER, MATRIX_GREEN_BORDER

class HealthPotionCard(customtkinter.CTkFrame):
    def __init__(self, parent, context, healthPotionType, title=''):
        super().__init__(parent, fg_color=MATRIX_BLACK, border_color=MATRIX_GREEN_BORDER, border_width=1)
        self.configure(fg_color=MATRIX_BLACK)
        self.context = context
        self.healthPotionType = healthPotionType
        self.columnconfigure(0, weight=3)
        self.columnconfigure(1, weight=7)
        self.rowconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)
        self.rowconfigure(2, weight=1)
        self.rowconfigure(3, weight=1)

        self.healthPotionTitleLabel = customtkinter.CTkLabel(self, text=title, text_color=MATRIX_GREEN)
        self.healthPotionTitleLabel.grid(row=0, column=0, columnspan=2, sticky='ew', padx=10, pady=(10, 5)) # columnspan to center

        self.checkVar = tk.BooleanVar()
        self.checkVar.set(
            self.context.context['healing']['potions'][healthPotionType]['enabled'])
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

        self.hpPercentageLessThanOrEqualLabel = customtkinter.CTkLabel(
            self, text='HP % <=:', text_color=MATRIX_GREEN) # Shortened text for better fit
        self.hpPercentageLessThanOrEqualLabel.grid(
            column=0, row=4, sticky='w', padx=10, pady=5)

        self.hpLessThanOrEqualVar = tk.IntVar()
        self.hpLessThanOrEqualVar.set(self.context.context['healing']
                                    ['potions'][healthPotionType]['hpPercentageLessThanOrEqual'])
        self.hpLessThanOrEqualSlider = customtkinter.CTkSlider(self, from_=0, to=100,
                                                button_color=MATRIX_GREEN_BORDER, button_hover_color=MATRIX_GREEN_HOVER,
                                                progress_color=MATRIX_GREEN, fg_color=MATRIX_GREEN_BORDER,
                                                variable=self.hpLessThanOrEqualVar, command=self.onChangeHp)
        self.hpLessThanOrEqualSlider.grid(column=1, row=4, padx=10, pady=5, sticky='ew')

        self.hpLessThanOrEqualLabelValue = customtkinter.CTkLabel( # Renamed for clarity
            self, textvariable=self.hpLessThanOrEqualVar, text_color=MATRIX_GREEN)
        self.hpLessThanOrEqualLabelValue.grid(
            column=1, row=5, sticky='e', padx=10, pady=(0,5)) # Aligned to the right of slider

        self.manaPercentageGreaterThanOrEqualLabel = customtkinter.CTkLabel(
            self, text='Mana % >=:', text_color=MATRIX_GREEN) # Shortened text
        self.manaPercentageGreaterThanOrEqualLabel.grid(
            column=0, row=6, sticky='w', padx=10, pady=5)

        self.manaPercentageGreaterThanOrEqualVar = tk.IntVar()
        self.manaPercentageGreaterThanOrEqualVar.set(self.context.context['healing']
                                                    ['potions'][healthPotionType]['manaPercentageGreaterThanOrEqual'])
        self.manaPercentageGreaterThanOrEqualSlider = customtkinter.CTkSlider(self, from_=0, to=100,
                                                            button_color=MATRIX_GREEN_BORDER, button_hover_color=MATRIX_GREEN_HOVER,
                                                            progress_color=MATRIX_GREEN, fg_color=MATRIX_GREEN_BORDER,
                                                            variable=self.manaPercentageGreaterThanOrEqualVar, command=self.onChangeMana)
        self.manaPercentageGreaterThanOrEqualSlider.grid(
            column=1, row=6, padx=10, pady=5, sticky='ew')
        
        self.manaPercentageGreaterThanOrEqualLabelValue = customtkinter.CTkLabel( # Renamed for clarity
            self, textvariable=self.manaPercentageGreaterThanOrEqualVar, text_color=MATRIX_GREEN)
        self.manaPercentageGreaterThanOrEqualLabelValue.grid(
            column=1, row=7, sticky='e', padx=10, pady=(0,5)) # Aligned to the right of slider

    def onToggleCheckButton(self):
        self.context.toggleHealingPotionsByKey(
            self.healthPotionType, self.checkVar.get())

    def onChangeHp(self, _):
        self.context.setHealthPotionHpPercentageLessThanOrEqual(
            self.healthPotionType, self.hpLessThanOrEqualVar.get())

    def onChangeMana(self, _):
        self.context.setHealthPotionManaPercentageGreaterThanOrEqual(
            self.healthPotionType, self.manaPercentageGreaterThanOrEqualVar.get())

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