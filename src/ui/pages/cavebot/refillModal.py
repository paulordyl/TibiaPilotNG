import customtkinter
from tkinter import messagebox, BooleanVar
from ...utils import genRanStr

class RefillModal(customtkinter.CTkToplevel):
    def __init__(self, parent, onConfirm=lambda: {}, waypoint=None):
        super().__init__(parent)        
        self.onConfirm = onConfirm

        self.title(genRanStr())
        self.resizable(False, False)
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)

        self.healthPotionFrame = customtkinter.CTkFrame(self)
        self.healthPotionFrame.grid(column=0, row=1, padx=(10, 5),
                                    pady=(10, 0), sticky='nsew')
        self.healthPotionFrame.rowconfigure(0, weight=1)
        self.healthPotionFrame.rowconfigure(1, weight=1)

        self.healthPotionEnabledVar = BooleanVar()
        if waypoint is not None:
            healthPotionEnabled = waypoint['options'].get('healthPotionEnabled')
            if healthPotionEnabled is not None:
                self.healthPotionEnabledVar.set(healthPotionEnabled)
        self.healthPotionEnabledButton = customtkinter.CTkCheckBox(
            self, text='Buy Health Potion', variable=self.healthPotionEnabledVar,
            hover_color="#870125", fg_color='#C20034')
        self.healthPotionEnabledButton.grid(column=0, row=0, padx=(10, 5), pady=(10, 0), sticky='w')

        self.healthPotionCombobox = customtkinter.CTkComboBox(
            self.healthPotionFrame, values=['Small Health Potion', 'Health Potion', 'Strong Health Potion', 'Great Health Potion', 'Ultimate Health Potion', 'Supreme Health Potion'], state='readonly')
        self.healthPotionCombobox.grid(
            row=0, column=0, sticky='nsew', padx=10, pady=10)
        if waypoint is not None:
            healthPotionItem = waypoint['options'].get(
                'healthPotion').get('item')
            self.healthPotionCombobox.set(healthPotionItem)

        self.healthPotionEntry = customtkinter.CTkEntry(self.healthPotionFrame, validate='key',
                                        validatecommand=(self.register(self.validateNumber), "%P"))
        self.healthPotionEntry.grid(
            row=1, column=0, sticky='nsew', padx=10, pady=10)
        if waypoint is not None:
            healthPotionQuantity = str(
                waypoint['options'].get('healthPotion').get('quantity'))
            self.healthPotionEntry.insert(0, healthPotionQuantity)

        self.manaPotionFrame = customtkinter.CTkFrame(self)
        self.manaPotionFrame.grid(column=1, row=1, padx=(5, 10),
                                pady=(10, 0), sticky='nsew')
        self.manaPotionFrame.rowconfigure(0, weight=1)
        self.manaPotionFrame.rowconfigure(1, weight=1)

        self.houseNpcEnabledVar = BooleanVar()
        if waypoint is not None:
            houseNpcEnabled = waypoint['options'].get('houseNpcEnabled')
            if houseNpcEnabled is not None:
                self.houseNpcEnabledVar.set(houseNpcEnabled)
        self.houseNpcEnabledButton = customtkinter.CTkCheckBox(
            self, text='Buy In House NPC', variable=self.houseNpcEnabledVar,
            hover_color="#870125", fg_color='#C20034')
        self.houseNpcEnabledButton.grid(column=1, row=0, padx=(10, 5), pady=(10, 0), sticky='w')

        self.manaPotionCombobox = customtkinter.CTkComboBox(
            self.manaPotionFrame, values=['Mana Potion', 'Strong Mana Potion', 'Great Mana Potion', 'Ultimate Mana Potion'], state='readonly')
        self.manaPotionCombobox.grid(
            row=0, column=0, sticky='nsew', padx=10, pady=10)
        if waypoint is not None:
            manaPotionItem = waypoint['options'].get('manaPotion').get('item')
            self.manaPotionCombobox.set(manaPotionItem)

        self.manaPotionEntry = customtkinter.CTkEntry(self.manaPotionFrame, validate='key',
                                        validatecommand=(self.register(self.validateNumber), "%P"))
        self.manaPotionEntry.grid(
            row=1, column=0, sticky='nsew', padx=10, pady=10)
        if waypoint is not None:
            manaPotionQuantity = str(waypoint['options'].get(
                'manaPotion').get('quantity'))
            self.manaPotionEntry.insert(0, manaPotionQuantity)

        self.confirmButton = customtkinter.CTkButton(
            self, text='Confirm', command=self.confirm,
            corner_radius=32, fg_color="transparent", border_color="#C20034",
            border_width=2, hover_color="#C20034")
        self.confirmButton.grid(
            row=2, column=0, padx=10, pady=10, sticky='nsew')

        self.cancelButton = customtkinter.CTkButton(
            self, text='Cancel', command=self.destroy,
            corner_radius=32, fg_color="transparent", border_color="#C20034",
            border_width=2, hover_color="#C20034")
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
