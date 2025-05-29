import customtkinter
from ...utils import genRanStr
from ...theme import MATRIX_BLACK, MATRIX_GREEN, MATRIX_GREEN_HOVER, MATRIX_GREEN_BORDER

class DepositItemsModal(customtkinter.CTkToplevel):
    def __init__(self, parent, waypoint=None, onConfirm=lambda: {}):
        super().__init__(parent)
        self.configure(fg_color=MATRIX_BLACK)
        self.onConfirm = onConfirm

        self.title(genRanStr())
        self.resizable(False, False)

        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)

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
        
        button_args = {
            "corner_radius": 32,
            "fg_color": "transparent",
            "text_color": MATRIX_GREEN,
            "border_color": MATRIX_GREEN_BORDER,
            "border_width": 2,
            "hover_color": MATRIX_GREEN_HOVER
        }

        self.frame = customtkinter.CTkFrame(self, **frame_args)
        self.frame.grid(column=0, row=0, columnspan=2, padx=10,
                        pady=10, sticky='nsew')
        self.frame.rowconfigure(0, weight=1) # For Label
        self.frame.rowconfigure(1, weight=1) # For Combobox
        self.frame.columnconfigure(0, weight=1) # Ensure combobox expands

        self.cityDescLabel = customtkinter.CTkLabel(self.frame, text="City:", text_color=MATRIX_GREEN) # Renamed
        self.cityDescLabel.grid(row=0, column=0, sticky='w', padx=10, pady=(10, 0))

        self.cityCombobox = customtkinter.CTkComboBox(
            self.frame, values=['AbDendriel', 'Ankrahmun', 'Carlin', 'Darashia', 'Edron', 'Farmine', 'Issavi', 'Kazoordon', 'LibertBay', 'PortHope', 'Rathleton', 'Svargrond', 'Thais', 'Venore', 'Yalahar', 'Feyrist', 'Dark Mansion'], **combobox_args)
        self.cityCombobox.grid(
            row=1, column=0, sticky='ew', padx=10, pady=10) # sticky changed to 'ew'
        if waypoint is not None:
            city = waypoint['options'].get('city')
            if city is not None:
                self.cityCombobox.set(city)

        self.confirmButton = customtkinter.CTkButton(
            self, text='Confirm', command=self.confirm, **button_args)
        self.confirmButton.grid(
            row=1, column=0, padx=(10, 5), pady=(5, 10), sticky='nsew') # row changed to 1

        self.cancelButton = customtkinter.CTkButton(
            self, text='Cancel', command=self.destroy, **button_args)
        self.cancelButton.grid(
            row=1, column=1, padx=(5, 10), pady=(5, 10), sticky='nsew') # row changed to 1

    def confirm(self):
        self.onConfirm(None, {
            'city': self.cityCombobox.get(),
        })
        self.destroy()
