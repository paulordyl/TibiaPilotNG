import customtkinter
from tkinter import messagebox, BooleanVar
from ...utils import genRanStr
from ...theme import MATRIX_BLACK, MATRIX_GREEN, MATRIX_GREEN_HOVER, MATRIX_GREEN_BORDER

class RefillModal(customtkinter.CTkToplevel):
    def __init__(self, parent, onConfirm=lambda: {}, waypoint=None):
        super().__init__(parent)
        self.configure(fg_color=MATRIX_BLACK)
        self.onConfirm = onConfirm

        self.title(genRanStr())
        self.resizable(False, False)
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)

        checkbox_args = {
            "text_color": MATRIX_GREEN,
            "fg_color": MATRIX_GREEN,
            "hover_color": MATRIX_GREEN_HOVER,
            "border_color": MATRIX_GREEN_BORDER,
            "checkmark_color": MATRIX_BLACK
        }
        
        combobox_args = {
            "state": 'readonly',
            "text_color": MATRIX_GREEN,
            "border_color": MATRIX_GREEN_BORDER,
            "fg_color": MATRIX_BLACK,
            "button_color": MATRIX_GREEN_BORDER,
            "button_hover_color": MATRIX_GREEN_HOVER,
            "dropdown_fg_color": MATRIX_BLACK,
            "dropdown_hover_color": MATRIX_GREEN_HOVER,
            "dropdown_text_color": MATRIX_GREEN
        }

        entry_args = {
            "validate": 'key',
            "validatecommand": (self.register(self.validateNumber), "%P"),
            "text_color": MATRIX_GREEN,
            "border_color": MATRIX_GREEN_BORDER,
            "fg_color": MATRIX_BLACK,
            "insertbackground": MATRIX_GREEN
        }

        frame_args = {
            "fg_color": MATRIX_BLACK,
            "border_color": MATRIX_GREEN_BORDER,
            "border_width": 1
        }
        
        button_args = {
            "corner_radius": 32,
            "fg_color": "transparent",
            "text_color": MATRIX_GREEN,
            "border_color": MATRIX_GREEN_BORDER,
            "border_width": 2,
            "hover_color": MATRIX_GREEN_HOVER
        }

        self.healthPotionFrame = customtkinter.CTkFrame(self, **frame_args)
        self.healthPotionFrame.grid(column=0, row=1, padx=(10, 5),
                                    pady=(10, 0), sticky='nsew')
        self.healthPotionFrame.rowconfigure(0, weight=1)
        self.healthPotionFrame.rowconfigure(1, weight=1)
        self.healthPotionFrame.columnconfigure(0, weight=1)


        self.healthPotionEnabledVar = BooleanVar()
        if waypoint is not None:
            healthPotionEnabled = waypoint['options'].get('healthPotionEnabled')
            if healthPotionEnabled is not None:
                self.healthPotionEnabledVar.set(healthPotionEnabled)
        self.healthPotionEnabledButton = customtkinter.CTkCheckBox(
            self, text='Buy Health Potion', variable=self.healthPotionEnabledVar, **checkbox_args)
        self.healthPotionEnabledButton.grid(column=0, row=0, padx=(10, 5), pady=(10, 0), sticky='w')

        self.healthPotionCombobox = customtkinter.CTkComboBox(
            self.healthPotionFrame, values=['Small Health Potion', 'Health Potion', 'Strong Health Potion', 'Great Health Potion', 'Ultimate Health Potion', 'Supreme Health Potion'], **combobox_args)
        self.healthPotionCombobox.grid(
            row=0, column=0, sticky='ew', padx=10, pady=10)
        if waypoint is not None and waypoint['options'].get('healthPotion', {}).get('item'):
            self.healthPotionCombobox.set(waypoint['options']['healthPotion']['item'])

        self.healthPotionEntry = customtkinter.CTkEntry(self.healthPotionFrame, **entry_args)
        self.healthPotionEntry.grid(
            row=1, column=0, sticky='ew', padx=10, pady=10)
        if waypoint is not None and waypoint['options'].get('healthPotion', {}).get('quantity') is not None:
            self.healthPotionEntry.insert(0, str(waypoint['options']['healthPotion']['quantity']))

        self.manaPotionFrame = customtkinter.CTkFrame(self, **frame_args)
        self.manaPotionFrame.grid(column=1, row=1, padx=(5, 10),
                                pady=(10, 0), sticky='nsew')
        self.manaPotionFrame.rowconfigure(0, weight=1)
        self.manaPotionFrame.rowconfigure(1, weight=1)
        self.manaPotionFrame.columnconfigure(0, weight=1)


        self.houseNpcEnabledVar = BooleanVar()
        if waypoint is not None:
            houseNpcEnabled = waypoint['options'].get('houseNpcEnabled')
            if houseNpcEnabled is not None:
                self.houseNpcEnabledVar.set(houseNpcEnabled)
        self.houseNpcEnabledButton = customtkinter.CTkCheckBox(
            self, text='Buy In House NPC', variable=self.houseNpcEnabledVar, **checkbox_args)
        self.houseNpcEnabledButton.grid(column=1, row=0, padx=(5, 10), pady=(10, 0), sticky='w') # Adjusted padx

        self.manaPotionCombobox = customtkinter.CTkComboBox(
            self.manaPotionFrame, values=['Mana Potion', 'Strong Mana Potion', 'Great Mana Potion', 'Ultimate Mana Potion'], **combobox_args)
        self.manaPotionCombobox.grid(
            row=0, column=0, sticky='ew', padx=10, pady=10)
        if waypoint is not None and waypoint['options'].get('manaPotion', {}).get('item'):
            self.manaPotionCombobox.set(waypoint['options']['manaPotion']['item'])

        self.manaPotionEntry = customtkinter.CTkEntry(self.manaPotionFrame, **entry_args)
        self.manaPotionEntry.grid(
            row=1, column=0, sticky='ew', padx=10, pady=10)
        if waypoint is not None and waypoint['options'].get('manaPotion', {}).get('quantity') is not None:
            self.manaPotionEntry.insert(0, str(waypoint['options']['manaPotion']['quantity']))

        self.confirmButton = customtkinter.CTkButton(
            self, text='Confirm', command=self.confirm, **button_args)
        self.confirmButton.grid(
            row=2, column=0, padx=10, pady=10, sticky='nsew')

        self.cancelButton = customtkinter.CTkButton(
            self, text='Cancel', command=self.destroy, **button_args)
        self.cancelButton.grid(
            row=2, column=1, padx=10, pady=10, sticky='nsew')

    def validateNumber(self, value: int) -> bool:
        if value.isdigit() and int(value) > 0:
            return True
        messagebox.showerror(
            'Error', "Digite um número válido maior que zero.")
        return False

    def confirm(self):
        self.onConfirm(None, {
            'healthPotionEnabled': self.healthPotionEnabledVar.get(),
            'houseNpcEnabled': self.houseNpcEnabledVar.get(),
            'healthPotion': {
                'item': self.healthPotionCombobox.get(),
                'quantity': int(self.healthPotionEntry.get())
            },
            'manaPotion': {
                'item': self.manaPotionCombobox.get(),
                'quantity': int(self.manaPotionEntry.get())
            },
        })
        self.destroy()
