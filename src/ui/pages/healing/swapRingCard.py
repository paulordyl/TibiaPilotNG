import tkinter as tk
import customtkinter
import re
from tkinter import messagebox
from ...theme import MATRIX_BLACK, MATRIX_GREEN, MATRIX_GREEN_HOVER, MATRIX_GREEN_BORDER

class SwapRingCard(customtkinter.CTkFrame):
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

        self.titleLabel = customtkinter.CTkLabel(self, text="Swap ring", text_color=MATRIX_GREEN) # Renamed from healthFoodLabel
        self.titleLabel.grid(row=0, column=0, columnspan=2, sticky='ew', padx=10, pady=(10, 5))

        self.checkVar = tk.BooleanVar()
        self.checkVar.set(
            self.context.context['healing']['highPriority']['swapRing']['enabled'])
        self.checkbutton = customtkinter.CTkCheckBox(
            self, text='Enabled', variable=self.checkVar, command=self.onToggleCheckButton,
            text_color=MATRIX_GREEN, fg_color=MATRIX_GREEN, hover_color=MATRIX_GREEN_HOVER,
            border_color=MATRIX_GREEN_BORDER, checkmark_color=MATRIX_BLACK)
        self.checkbutton.grid(column=1, row=1, sticky='e', padx=10, pady=5)

        # --- Tank Ring Section ---
        self.tankRingSectionLabel = customtkinter.CTkLabel(self, text="Tank Ring:", text_color=MATRIX_GREEN, font=("Arial", 12, "bold"))
        self.tankRingSectionLabel.grid(row=2, column=0, columnspan=2, sticky='ew', padx=10, pady=(10,2))

        self.tankHotkeyDescLabel = customtkinter.CTkLabel(self, text='Hotkey:', text_color=MATRIX_GREEN) # Renamed
        self.tankHotkeyDescLabel.grid(column=0, row=3, padx=10, pady=5, sticky='w')

        self.tankHotkeyEntryVar = tk.StringVar()
        self.tankHotkeyEntryVar.set(self.context.context['healing']['highPriority']['swapRing']['tankRing']['hotkey'])
        self.tankHotkeyEntry = customtkinter.CTkEntry(self, textvariable=self.tankHotkeyEntryVar,
                                                     text_color=MATRIX_GREEN, border_color=MATRIX_GREEN_BORDER,
                                                     fg_color=MATRIX_BLACK, insertbackground=MATRIX_GREEN)
        self.tankHotkeyEntry.bind('<Key>', self.onChangeTankHotkey)
        self.tankHotkeyEntry.grid(column=1, row=3, padx=10, pady=5, sticky='ew')
        
        self.slotTankDescLabel = customtkinter.CTkLabel(self, text='Slot:', text_color=MATRIX_GREEN) # Renamed
        self.slotTankDescLabel.grid(column=0, row=4, padx=10, pady=5, sticky='w')

        self.slotTankEntryVar = tk.StringVar()
        self.slotTankEntryVar.set(self.context.context['healing']['highPriority']['swapRing']['tankRing']['slot'])
        self.slotTankEntry = customtkinter.CTkEntry(self, textvariable=self.slotTankEntryVar, validate='key',
                                        validatecommand=(self.register(self.validateNumber), "%P"),
                                        text_color=MATRIX_GREEN, border_color=MATRIX_GREEN_BORDER,
                                        fg_color=MATRIX_BLACK, insertbackground=MATRIX_GREEN)
        self.slotTankEntry.bind('<KeyRelease>', self.onChangeTankNumber)
        self.slotTankEntry.grid(column=1, row=4, padx=10, pady=5, sticky='ew')

        self.tankHpDescLabel = customtkinter.CTkLabel(self, text='HP % <=:', text_color=MATRIX_GREEN) # Renamed from aaaLabel
        self.tankHpDescLabel.grid(column=0, row=5, sticky='w', padx=10, pady=5)

        self.hpLessThanOrEqualVar = tk.IntVar()
        self.hpLessThanOrEqualVar.set(
            self.context.context['healing']['highPriority']['swapRing']['tankRing']['hpPercentageLessThanOrEqual'])
        self.hpLessThanOrEqualSlider = customtkinter.CTkSlider(self, from_=10, to=100,
                                                button_color=MATRIX_GREEN_BORDER, button_hover_color=MATRIX_GREEN_HOVER,
                                                progress_color=MATRIX_GREEN, fg_color=MATRIX_GREEN_BORDER,
                                                variable=self.hpLessThanOrEqualVar, command=self.onChangeHpLessThanOrEqual)
        self.hpLessThanOrEqualSlider.grid(column=1, row=5, padx=10, pady=5, sticky='ew')

        self.hpLessThanOrEqualValueLabel = customtkinter.CTkLabel(self, textvariable=self.hpLessThanOrEqualVar, text_color=MATRIX_GREEN) # Renamed
        self.hpLessThanOrEqualValueLabel.grid(column=1, row=6, sticky='e', padx=10, pady=(0,5))
        
        # --- Main Ring Section ---
        self.mainRingSectionLabel = customtkinter.CTkLabel(self, text="Main Ring:", text_color=MATRIX_GREEN, font=("Arial", 12, "bold"))
        self.mainRingSectionLabel.grid(row=7, column=0, columnspan=2, sticky='ew', padx=10, pady=(10,2))

        self.mainHotkeyDescLabel = customtkinter.CTkLabel(self, text='Hotkey:', text_color=MATRIX_GREEN) # Renamed
        self.mainHotkeyDescLabel.grid(column=0, row=8, padx=10, pady=5, sticky='w')

        self.mainHotkeyEntryVar = tk.StringVar()
        self.mainHotkeyEntryVar.set(self.context.context['healing']['highPriority']['swapRing']['mainRing']['hotkey'])
        self.mainHotkeyEntry = customtkinter.CTkEntry(self, textvariable=self.mainHotkeyEntryVar,
                                                     text_color=MATRIX_GREEN, border_color=MATRIX_GREEN_BORDER,
                                                     fg_color=MATRIX_BLACK, insertbackground=MATRIX_GREEN)
        self.mainHotkeyEntry.bind('<Key>', self.onChangeMainHotkey)
        self.mainHotkeyEntry.grid(column=1, row=8, padx=10, pady=5, sticky='ew')
        
        self.slotMainDescLabel = customtkinter.CTkLabel(self, text='Slot:', text_color=MATRIX_GREEN) # Renamed
        self.slotMainDescLabel.grid(column=0, row=9, padx=10, pady=5, sticky='w')

        self.slotMainEntryVar = tk.StringVar()
        self.slotMainEntryVar.set(self.context.context['healing']['highPriority']['swapRing']['mainRing']['slot'])
        self.slotMainEntry = customtkinter.CTkEntry(self, textvariable=self.slotMainEntryVar, validate='key',
                                        validatecommand=(self.register(self.validateNumber), "%P"),
                                        text_color=MATRIX_GREEN, border_color=MATRIX_GREEN_BORDER,
                                        fg_color=MATRIX_BLACK, insertbackground=MATRIX_GREEN)
        self.slotMainEntry.bind('<KeyRelease>', self.onChangeMainNumber)
        self.slotMainEntry.grid(column=1, row=9, padx=10, pady=5, sticky='ew')

        self.mainHpDescLabel = customtkinter.CTkLabel(self, text='HP % >:', text_color=MATRIX_GREEN) # Renamed from bbbLabel
        self.mainHpDescLabel.grid(column=0, row=10, sticky='w', padx=10, pady=5)

        self.hpGreaterThanVar = tk.IntVar()
        self.hpGreaterThanVar.set(
            self.context.context['healing']['highPriority']['swapRing']['mainRing']['hpPercentageGreaterThan'])
        self.hpGreaterThanSlider = customtkinter.CTkSlider(self, from_=10, to=100,
                                            button_color=MATRIX_GREEN_BORDER, button_hover_color=MATRIX_GREEN_HOVER,
                                            progress_color=MATRIX_GREEN, fg_color=MATRIX_GREEN_BORDER,
                                            variable=self.hpGreaterThanVar, command=self.onChangeHpGreaterThan)
        self.hpGreaterThanSlider.grid(column=1, row=10, padx=10, pady=5, sticky='ew')

        self.hpGreaterThanValueLabel = customtkinter.CTkLabel(self, textvariable=self.hpGreaterThanVar, text_color=MATRIX_GREEN) # Renamed
        self.hpGreaterThanValueLabel.grid(column=1, row=11, sticky='e', padx=10, pady=(0,5))

    def onToggleCheckButton(self):
        self.context.toggleHealingHighPriorityByKey(
            'swapRing', self.checkVar.get())

    def onChangeHpLessThanOrEqual(self, _):
        self.context.setSwapRingHpPercentageLessThanOrEqual(
            self.hpLessThanOrEqualVar.get())

    def onChangeHpGreaterThan(self, _):
        self.context.setSwapRingHpPercentageGreaterThan(
            self.hpGreaterThanVar.get())
        
    def onChangeTankHotkey(self, event):
        key = event.char
        key_pressed = event.keysym
        if key == '\b':
            return
        if re.match(r'^F[1-9]|1[0-2]$', key) or re.match(r'^[0-9]$', key) or re.match(r'^[a-z]$', key):
            self.tankHotkeyEntry.delete(0, tk.END)
            self.context.setSwapTankRingHotkey(key)
        else:
            self.context.setSwapTankRingHotkey(key_pressed)
            self.tankHotkeyEntryVar.set(key_pressed)

    def onChangeMainHotkey(self, event):
        key = event.char
        key_pressed = event.keysym
        if key == '\b':
            return
        if re.match(r'^F[1-9]|1[0-2]$', key) or re.match(r'^[0-9]$', key) or re.match(r'^[a-z]$', key):
            self.mainHotkeyEntry.delete(0, tk.END)
            self.context.setSwapMainRingHotkey(key)
        else:
            self.context.setSwapMainRingHotkey(key_pressed)
            self.mainHotkeyEntryVar.set(key_pressed)

    def onChangeTankNumber(self, event):
        value = self.slotTankEntry.get()
        if value.isdigit() and int(value) > 0:
            self.context.setSwapTankRingSlotByKey(int(value))

    def onChangeMainNumber(self, event):
        value = self.slotMainEntry.get()
        if value.isdigit() and int(value) > 0:
            self.context.setSwapMainRingSlotByKey(int(value))

    def validateNumber(self, value: int) -> bool:
        if value == '':
            return True
        if value.isdigit() and int(value) > 0:
            return True
        messagebox.showerror(
            'Error', "Digite um número válido maior que zero.")
        return False