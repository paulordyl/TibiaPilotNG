import re
import tkinter as tk
import customtkinter

class HealthFoodCard(customtkinter.CTkFrame):
    def __init__(self, parent, context):
        super().__init__(parent)
        self.context = context
        self.columnconfigure(0, weight=3)
        self.columnconfigure(1, weight=7)
        self.rowconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)
        self.rowconfigure(2, weight=1)
        self.rowconfigure(3, weight=1)

        self.healthFoodLabel = customtkinter.CTkLabel(self, text="Health food")
        self.healthFoodLabel.grid(row=0, column=0, sticky='w', padx=10, pady=(10, 0))

        self.checkVar = tk.BooleanVar()
        self.checkVar.set(
            self.context.context['healing']['highPriority']['healthFood']['enabled'])
        self.checkbutton = customtkinter.CTkCheckBox(
            self, text='Enabled', variable=self.checkVar, command=self.onToggleCheckButton,
            hover_color="#870125", fg_color='#C20034')
        self.checkbutton.grid(column=1, row=1, sticky='e', pady=10)

        self.hotkeyLabel = customtkinter.CTkLabel(
            self, text='Hotkey:')
        self.hotkeyLabel.grid(column=0, row=2, padx=5,
                            pady=5, sticky='nsew')

        self.hotkeyEntryVar = tk.StringVar()
        self.hotkeyEntryVar.set(self.context.context['healing']
                                    ['highPriority']['healthFood']['hotkey'])
        self.hotkeyEntry = customtkinter.CTkEntry(self, textvariable=self.hotkeyEntryVar)
        self.hotkeyEntry.bind('<Key>', self.onChangeHotkey)
        self.hotkeyEntry.grid(column=1, row=2, padx=5,
                            pady=5, sticky='nsew')

        self.hpPercentageLessThanOrEqualLabel = customtkinter.CTkLabel(
            self, text='HP % less than or equal:')
        self.hpPercentageLessThanOrEqualLabel.grid(
            column=0, row=3, sticky='nsew', padx=(10, 0))

        self.hpLessThanOrEqualVar = tk.IntVar()
        self.hpLessThanOrEqualVar.set(
            self.context.context['healing']['highPriority']['healthFood']['hpPercentageLessThanOrEqual'])
        self.hpLessThanOrEqualSlider = customtkinter.CTkSlider(self, from_=10, to=100, 
                                            button_color='#C20034', button_hover_color='#870125',
                                            variable=self.hpLessThanOrEqualVar, command=self.onChangeHp)
        self.hpLessThanOrEqualSlider.grid(column=1, row=3, sticky='ew', padx=10, pady=10)

        self.hpLessThanOrEqualLabel = customtkinter.CTkLabel(
            self, textvariable=self.hpLessThanOrEqualVar)
        self.hpLessThanOrEqualLabel.grid(
            column=1, row=4, sticky='nsew')

    def onToggleCheckButton(self):
        self.context.toggleHealingHighPriorityByKey(
            'healthFood', self.checkVar.get())

    def onChangeHp(self, _):
        self.context.setHealthFoodHpPercentageLessThanOrEqual(
            self.hpLessThanOrEqualVar.get())

    def onChangeHotkey(self, event):
            key = event.char
            key_pressed = event.keysym
            if key == '\b':
                return
            if re.match(r'^F[1-9]|1[0-2]$', key) or re.match(r'^[0-9]$', key) or re.match(r'^[a-z]$', key):
                self.hotkeyEntry.delete(0, tk.END)
                self.context.setHotkeyHealingHighPriorityByKey('healthFood', key)
            else:
                self.context.setHotkeyHealingHighPriorityByKey('healthFood', key_pressed)
                self.hotkeyEntryVar.set(key_pressed)