import customtkinter
from tkinter import messagebox
from ...utils import genRanStr
from ...theme import MATRIX_BLACK, MATRIX_GREEN, MATRIX_GREEN_HOVER, MATRIX_GREEN_BORDER

class BuyBackpackModal(customtkinter.CTkToplevel):
    def __init__(self, parent, onConfirm=lambda: {}, waypoint=None):
        super().__init__(parent)
        self.configure(fg_color=MATRIX_BLACK)
        self.onConfirm = onConfirm

        self.title(genRanStr())
        self.resizable(False, False)
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1) # For confirm/cancel buttons if they are side-by-side

        frame_args = {
            "fg_color": MATRIX_BLACK,
            "border_color": MATRIX_GREEN_BORDER,
            "border_width": 1
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
        
        button_args = {
            "corner_radius": 32,
            "fg_color": "transparent",
            "text_color": MATRIX_GREEN,
            "border_color": MATRIX_GREEN_BORDER,
            "border_width": 2,
            "hover_color": MATRIX_GREEN_HOVER
        }

        self.buyBackpackFrame = customtkinter.CTkFrame(self, **frame_args)
        # Grid layout changed: frame spans 2 columns, buttons will be below it.
        self.buyBackpackFrame.grid(column=0, row=0, columnspan=2, padx=10, pady=10, sticky='nsew')
        self.buyBackpackFrame.rowconfigure(0, weight=1) # For combobox
        self.buyBackpackFrame.rowconfigure(1, weight=1) # For entry
        self.buyBackpackFrame.columnconfigure(0, weight=1) # Ensure widgets inside expand

        self.backpackCombobox = customtkinter.CTkComboBox(
            self.buyBackpackFrame, values=['Orange Backpack', 'Red Backpack', 'Parcel'], **combobox_args)
        self.backpackCombobox.grid(
            row=0, column=0, sticky='ew', padx=10, pady=10)
        if waypoint is not None:
            backpackItem = waypoint['options'].get(
                'name', 'Orange Backpack')
            self.backpackCombobox.set(backpackItem)

        self.backpackAmountEntry = customtkinter.CTkEntry(self.buyBackpackFrame, **entry_args)
        self.backpackAmountEntry.grid(
            row=1, column=0, sticky='ew', padx=10, pady=10)
        if waypoint is not None:
            backpackAmount = str(
                waypoint['options'].get('amount', 12))
            self.backpackAmountEntry.insert(0, backpackAmount)

        self.confirmButton = customtkinter.CTkButton(
            self, text='Confirm', command=self.confirm, **button_args)
        self.confirmButton.grid(
            row=1, column=0, padx=(10,5), pady=10, sticky='nsew') # row changed to 1

        self.cancelButton = customtkinter.CTkButton(
            self, text='Cancel', command=self.destroy, **button_args)
        self.cancelButton.grid(
            row=1, column=1, padx=(5,10), pady=10, sticky='nsew') # row changed to 1

    def validateNumber(self, value: int) -> bool:
        if value.isdigit() and int(value) > 0:
            return True
        messagebox.showerror(
            'Error', "Digite um número válido maior que zero.")
        return False

    def confirm(self):
        self.onConfirm(None, {
            'name': self.backpackCombobox.get(),
            'amount': int(self.backpackAmountEntry.get())
        })
        self.destroy()
