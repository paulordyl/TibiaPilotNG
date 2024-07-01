import tkinter as tk
import customtkinter
import re
from tkinter import messagebox

class SwapAmuletCard(customtkinter.CTkFrame):
    def __init__(self, parent, context):
        super().__init__(parent)
        self.context = context
        self.columnconfigure(0, weight=3)
        self.columnconfigure(1, weight=7)
        self.rowconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)
        self.rowconfigure(2, weight=1)
        self.rowconfigure(3, weight=1)

        self.healthFoodLabel = customtkinter.CTkLabel(self, text="Swap amulet")
        self.healthFoodLabel.grid(row=0, column=0, sticky='w', padx=10, pady=(10, 0))

        self.checkVar = tk.BooleanVar()
        self.checkVar.set(
            self.context.context['healing']['highPriority']['swapAmulet']['enabled'])
        self.checkbutton = customtkinter.CTkCheckBox(
            self, text='Enabled', variable=self.checkVar, command=self.onToggleCheckButton,
            hover_color="#870125", fg_color='#C20034')
        self.checkbutton.grid(column=1, row=1, sticky='e')

        self.tankHotkeyLabel = customtkinter.CTkLabel(
            self, text='Tank Hotkey:')
        self.tankHotkeyLabel.grid(column=0, row=2, padx=10,
                            pady=10, sticky='nsew')

        self.tankHotkeyEntryVar = tk.StringVar()
        self.tankHotkeyEntryVar.set(self.context.context['healing']['highPriority']['swapAmulet']['tankAmulet']['hotkey'])
        self.tankHotkeyEntry = customtkinter.CTkEntry(self, textvariable=self.tankHotkeyEntryVar)
        self.tankHotkeyEntry.bind('<Key>', self.onChangeTankHotkey)
        self.tankHotkeyEntry.grid(column=1, row=2, padx=10,
                            pady=10, sticky='nsew')
        
        self.slotTankLabel = customtkinter.CTkLabel(
            self, text='Tank Slot:')
        self.slotTankLabel.grid(column=0, row=3, padx=10,
                            pady=10, sticky='nsew')

        self.slotTankEntryVar = tk.StringVar()
        self.slotTankEntryVar.set(self.context.context['healing']['highPriority']['swapAmulet']['tankAmulet']['slot'])
        self.slotTankEntry = customtkinter.CTkEntry(self, textvariable=self.slotTankEntryVar, validate='key',
                                        validatecommand=(self.register(self.validateNumber), "%P"))
        self.slotTankEntry.bind('<KeyRelease>', self.onChangeTankNumber)
        self.slotTankEntry.grid(column=1, row=3, padx=10,
                            pady=10, sticky='nsew')

        self.aaaLabel = customtkinter.CTkLabel(self, text='Tank - HP % less than or equal:')
        self.aaaLabel.grid(column=0, row=4, sticky='nsew', padx=(10, 0))

        self.hpLessThanOrEqualVar = tk.IntVar()
        self.hpLessThanOrEqualVar.set(
            self.context.context['healing']['highPriority']['swapAmulet']['tankAmulet']['hpPercentageLessThanOrEqual'])
        self.hpLessThanOrEqualSlider = customtkinter.CTkSlider(self, from_=10, to=100,
                                                button_color='#C20034', button_hover_color='#870125',
                                                variable=self.hpLessThanOrEqualVar, command=self.onChangeHpLessThanOrEqual)
        self.hpLessThanOrEqualSlider.grid(column=1, row=4, sticky='ew')

        self.hpLessThanOrEqualLabel = customtkinter.CTkLabel(
            self, textvariable=self.hpLessThanOrEqualVar)
        self.hpLessThanOrEqualLabel.grid(
            column=1, row=5, sticky='nsew')
        
        self.mainHotkeyLabel = customtkinter.CTkLabel(
            self, text='Main Hotkey:')
        self.mainHotkeyLabel.grid(column=0, row=6, padx=10,
                            pady=10, sticky='nsew')

        self.mainHotkeyEntryVar = tk.StringVar()
        self.mainHotkeyEntryVar.set(self.context.context['healing']['highPriority']['swapAmulet']['mainAmulet']['hotkey'])
        self.mainHotkeyEntry = customtkinter.CTkEntry(self, textvariable=self.mainHotkeyEntryVar)
        self.mainHotkeyEntry.bind('<Key>', self.onChangeMainHotkey)
        self.mainHotkeyEntry.grid(column=1, row=6, padx=10,
                            pady=10, sticky='nsew')
        
        self.slotMainLabel = customtkinter.CTkLabel(
            self, text='Main Slot:')
        self.slotMainLabel.grid(column=0, row=7, padx=10,
                            pady=10, sticky='nsew')

        self.slotMainEntryVar = tk.StringVar()
        self.slotMainEntryVar.set(self.context.context['healing']['highPriority']['swapAmulet']['mainAmulet']['slot'])
        self.slotMainEntry = customtkinter.CTkEntry(self, textvariable=self.slotMainEntryVar, validate='key',
                                        validatecommand=(self.register(self.validateNumber), "%P"))
        self.slotMainEntry.bind('<KeyRelease>', self.onChangeMainNumber)
        self.slotMainEntry.grid(column=1, row=7, padx=10,
                            pady=10, sticky='nsew')

        self.bbbLabel = customtkinter.CTkLabel(self, text='Main - HP % greater than:')
        self.bbbLabel.grid(column=0, row=8, sticky='nsew', padx=(10, 0))

        self.hpGreaterThanVar = tk.IntVar()
        self.hpGreaterThanVar.set(
            self.context.context['healing']['highPriority']['swapAmulet']['mainAmulet']['hpPercentageGreaterThan'])
        self.hpGreaterThanSlider = customtkinter.CTkSlider(self, from_=10, to=100,
                                            button_color='#C20034', button_hover_color='#870125',
                                            variable=self.hpGreaterThanVar, command=self.onChangeHpGreaterThan)
        self.hpGreaterThanSlider.grid(column=1, row=8, sticky='ew')

        self.hpGreaterThanLabel = customtkinter.CTkLabel(
            self, textvariable=self.hpGreaterThanVar)
        self.hpGreaterThanLabel.grid(
            column=1, row=9, sticky='nsew')

    def onToggleCheckButton(self):
        self.context.toggleHealingHighPriorityByKey(
            'swapAmulet', self.checkVar.get())

    def onChangeHpLessThanOrEqual(self, _):
        self.context.setSwapAmuletHpPercentageLessThanOrEqual(
            self.hpLessThanOrEqualVar.get())

    def onChangeHpGreaterThan(self, _):
        self.context.setSwapAmuletHpPercentageGreaterThan(
            self.hpGreaterThanVar.get())

    def onChangeTankHotkey(self, event):
        key = event.char
        key_pressed = event.keysym
        if key == '\b':
            return
        if re.match(r'^F[1-9]|1[0-2]$', key) or re.match(r'^[0-9]$', key) or re.match(r'^[a-z]$', key):
            self.tankHotkeyEntry.delete(0, tk.END)
            self.context.setSwapTankAmuletHotkey(key)
        else:
            self.context.setSwapTankAmuletHotkey(key_pressed)
            self.tankHotkeyEntryVar.set(key_pressed)

    def onChangeMainHotkey(self, event):
        key = event.char
        key_pressed = event.keysym
        if key == '\b':
            return
        if re.match(r'^F[1-9]|1[0-2]$', key) or re.match(r'^[0-9]$', key) or re.match(r'^[a-z]$', key):
            self.mainHotkeyEntry.delete(0, tk.END)
            self.context.setSwapMainAmuletHotkey(key)
        else:
            self.context.setSwapMainAmuletHotkey(key_pressed)
            self.mainHotkeyEntryVar.set(key_pressed)

    def onChangeTankNumber(self, event):
        value = self.slotTankEntry.get()
        if value.isdigit() and int(value) > 0:
            self.context.setSwapTankAmuletSlotByKey(int(value))

    def onChangeMainNumber(self, event):
        value = self.slotMainEntry.get()
        if value.isdigit() and int(value) > 0:
            self.context.setSwapMainAmuletSlotByKey(int(value))

    def validateNumber(self, value: int) -> bool:
        if value == '':
            return True
        if value.isdigit() and int(value) > 0:
            return True
        messagebox.showerror(
            'Error', "Digite um número válido maior que zero.")
        return False