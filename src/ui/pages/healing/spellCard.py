import re
import tkinter as tk
import customtkinter
from ...theme import MATRIX_BLACK, MATRIX_GREEN, MATRIX_GREEN_HOVER, MATRIX_GREEN_BORDER


class SpellCard(customtkinter.CTkFrame):
    def __init__(self, parent, context, healingType, title=''):
        super().__init__(parent, fg_color=MATRIX_BLACK, border_color=MATRIX_GREEN_BORDER, border_width=1)
        self.configure(fg_color=MATRIX_BLACK)
        self.context = context
        self.text = title
        self.healingType = healingType
        self.columnconfigure(0, weight=3)
        self.columnconfigure(1, weight=7)
        self.rowconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)
        self.rowconfigure(2, weight=1)
        self.rowconfigure(3, weight=1)

        self.titleLabel = customtkinter.CTkLabel(self, text=title, text_color=MATRIX_GREEN) # Renamed from manaFoodLabel for clarity
        self.titleLabel.grid(row=0, column=0, columnspan=2, sticky='ew', padx=10, pady=(10, 5))

        self.checkVar = tk.BooleanVar()
        self.checkVar.set(self.context.context['healing']
                        ['spells'][healingType]['enabled'])
        self.checkbutton = customtkinter.CTkCheckBox(
            self, text='Enabled', variable=self.checkVar, command=self.onToggleCheckButton,
            text_color=MATRIX_GREEN, fg_color=MATRIX_GREEN, hover_color=MATRIX_GREEN_HOVER,
            border_color=MATRIX_GREEN_BORDER, checkmark_color=MATRIX_BLACK)
        self.checkbutton.grid(column=1, row=1, sticky='e', padx=10, pady=5)

        self.spellsDescLabel = customtkinter.CTkLabel( # Renamed from spellsLabel for clarity
            self, text='Spell:', text_color=MATRIX_GREEN)
        self.spellsDescLabel.grid(column=0, row=2, sticky='w', padx=10, pady=5)

        self.spellsCombobox = customtkinter.CTkComboBox(
            self, values=['exura infir ico', 'exura ico', 'exura med ico', 'exura gran ico'], state='readonly',
            command=self.onChangeSpell, text_color=MATRIX_GREEN, border_color=MATRIX_GREEN_BORDER,
            fg_color=MATRIX_BLACK, button_color=MATRIX_GREEN_BORDER, button_hover_color=MATRIX_GREEN_HOVER,
            dropdown_fg_color=MATRIX_BLACK, dropdown_hover_color=MATRIX_GREEN_HOVER, dropdown_text_color=MATRIX_GREEN)
        if self.context.enabledProfile is not None and self.context.enabledProfile['config']['healing']['spells'][healingType]['spell'] is not None:
            self.spellsCombobox.set(
                self.context.enabledProfile['config']['healing']['spells'][healingType]['spell'])
        self.spellsCombobox.grid(column=1, row=2, sticky='ew', padx=10, pady=5)

        self.hotkeyDescLabel = customtkinter.CTkLabel( # Renamed from hotkeyLabel for clarity
            self, text='Hotkey:', text_color=MATRIX_GREEN)
        self.hotkeyDescLabel.grid(column=0, row=3, padx=10,
                            pady=5, sticky='w')

        self.hotkeyEntryVar = tk.StringVar()
        self.hotkeyEntryVar.set(self.context.context['healing']
                                ['spells'][healingType]['hotkey'])
        self.hotkeyEntry = customtkinter.CTkEntry(self, textvariable=self.hotkeyEntryVar,
                                                 text_color=MATRIX_GREEN, border_color=MATRIX_GREEN_BORDER,
                                                 fg_color=MATRIX_BLACK, insertbackground=MATRIX_GREEN)
        self.hotkeyEntry.bind('<Key>', self.onChangeHotkey)
        self.hotkeyEntry.grid(column=1, row=3, padx=10,
                            pady=5, sticky='ew')

        self.hpPercentageLessThanOrEqualDescLabel = customtkinter.CTkLabel( # Renamed for clarity
            self, text='HP % <=:', text_color=MATRIX_GREEN) # Shortened
        self.hpPercentageLessThanOrEqualDescLabel.grid(
            column=0, row=4, sticky='w', padx=10, pady=5)

        self.hpLessThanOrEqualVar = tk.IntVar()
        self.hpLessThanOrEqualVar.set(self.context.context['healing']
                                    ['spells'][healingType]['hpPercentageLessThanOrEqual'])
        self.hpLessThanOrEqualSlider = customtkinter.CTkSlider(self, from_=0, to=100,
                                                button_color=MATRIX_GREEN_BORDER, button_hover_color=MATRIX_GREEN_HOVER,
                                                progress_color=MATRIX_GREEN, fg_color=MATRIX_GREEN_BORDER,
                                                variable=self.hpLessThanOrEqualVar, command=self.onChangeHp)
        self.hpLessThanOrEqualSlider.grid(column=1, row=4, padx=10, pady=5, sticky='ew')

        self.hpLessThanOrEqualValueLabel = customtkinter.CTkLabel( # Renamed for clarity
            self, textvariable=self.hpLessThanOrEqualVar, text_color=MATRIX_GREEN)
        self.hpLessThanOrEqualValueLabel.grid(
            column=1, row=5, sticky='e', padx=10, pady=(0,5))

        self.manaPercentageGreaterThanOrEqualDescLabel = customtkinter.CTkLabel( # Renamed for clarity
            self, text='Mana % >=:', text_color=MATRIX_GREEN) # Shortened
        self.manaPercentageGreaterThanOrEqualDescLabel.grid(
            column=0, row=6, sticky='w', padx=10, pady=5)

        self.manaPercentageGreaterThanOrEqualVar = tk.IntVar()
        self.manaPercentageGreaterThanOrEqualVar.set(self.context.context['healing']
                                                    ['spells'][healingType]['manaPercentageGreaterThanOrEqual'])
        self.manaPercentageGreaterThanOrEqualSlider = customtkinter.CTkSlider(self, from_=0, to=100,
                                                            button_color=MATRIX_GREEN_BORDER, button_hover_color=MATRIX_GREEN_HOVER,
                                                            progress_color=MATRIX_GREEN, fg_color=MATRIX_GREEN_BORDER,
                                                            variable=self.manaPercentageGreaterThanOrEqualVar, command=self.onChangeMana)
        self.manaPercentageGreaterThanOrEqualSlider.grid(
            column=1, row=6, padx=10, pady=5, sticky='ew')
        
        self.manaPercentageGreaterThanOrEqualValueLabel = customtkinter.CTkLabel( # Renamed for clarity
            self, textvariable=self.manaPercentageGreaterThanOrEqualVar, text_color=MATRIX_GREEN)
        self.manaPercentageGreaterThanOrEqualValueLabel.grid(
            column=1, row=7, sticky='e', padx=10, pady=(0,5))

    def onToggleCheckButton(self):
        self.context.toggleSpellByKey(
            self.healingType, self.checkVar.get())

    def onChangeSpell(self, _):
        self.context.setSpellName(self.healingType, self.spellsCombobox.get())

    def onChangeHp(self, _):
        self.context.setSpellHpPercentageLessThanOrEqual(
            self.healingType, self.hpLessThanOrEqualVar.get())

    def onChangeMana(self, _):
        self.context.setSpellManaPercentageGreaterThanOrEqual(
            self.healingType, self.manaPercentageGreaterThanOrEqualVar.get())

    def onChangeHotkey(self, event):
        key = event.char
        key_pressed = event.keysym
        if key == '\b':
            return
        if re.match(r'^F[1-9]|1[0-2]$', key) or re.match(r'^[0-9]$', key) or re.match(r'^[a-z]$', key):
            self.hotkeyEntry.delete(0, tk.END)
            self.context.setSpellHotkeyByKey(self.healingType, key)
        else:
            self.context.setSpellHotkeyByKey(self.healingType, key_pressed)
            self.hotkeyEntryVar.set(key_pressed)
