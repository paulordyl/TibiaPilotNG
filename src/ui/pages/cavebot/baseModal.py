import customtkinter
from ...utils import genRanStr
from ...theme import MATRIX_BLACK, MATRIX_GREEN, MATRIX_GREEN_HOVER, MATRIX_GREEN_BORDER

class BaseModal(customtkinter.CTkToplevel):
    def __init__(self, parent, waypoint=None, onConfirm=lambda: {}):
        super().__init__(parent)
        self.configure(fg_color=MATRIX_BLACK)
        self.onConfirm = onConfirm

        self.title(genRanStr())
        self.resizable(False, False)

        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)

        self.frame = customtkinter.CTkFrame(self, fg_color=MATRIX_BLACK, border_color=MATRIX_GREEN_BORDER, border_width=1)
        self.frame.grid(column=0, row=0, columnspan=2, padx=10,
                        pady=10, sticky='nsew')
        self.frame.rowconfigure(0, weight=1) # For Label
        self.frame.rowconfigure(1, weight=1) # For Entry
        self.frame.columnconfigure(0, weight=1) # Ensure entry expands

        self.labelDescLabel = customtkinter.CTkLabel(self.frame, text="Label:", text_color=MATRIX_GREEN) # Renamed
        self.labelDescLabel.grid(row=0, column=0, sticky='w', padx=10, pady=(10, 0))

        self.labelEntry = customtkinter.CTkEntry(self.frame, 
                                                 text_color=MATRIX_GREEN, 
                                                 border_color=MATRIX_GREEN_BORDER,
                                                 fg_color=MATRIX_BLACK, 
                                                 insertbackground=MATRIX_GREEN)
        self.labelEntry.grid(
            row=1, column=0, sticky='ew', padx=10, pady=10) # sticky changed to 'ew'
        if waypoint is not None and waypoint['label']:
            self.labelEntry.insert(0, waypoint['label'])

        button_args = {
            "corner_radius": 32,
            "fg_color": "transparent",
            "text_color": MATRIX_GREEN,
            "border_color": MATRIX_GREEN_BORDER,
            "border_width": 2,
            "hover_color": MATRIX_GREEN_HOVER
        }

        self.confirmButton = customtkinter.CTkButton(
            self, text='Confirm', command=self.confirm, **button_args)
        self.confirmButton.grid(
            row=1, column=0, padx=(10, 5), pady=(5, 10), sticky='nsew') # Changed row from 6 to 1

        self.cancelButton = customtkinter.CTkButton(
            self, text='Cancel', command=self.destroy, **button_args)
        self.cancelButton.grid(
            row=1, column=1, padx=(5, 10), pady=(5, 10), sticky='nsew') # Changed row from 6 to 1

    def confirm(self):
        self.onConfirm(self.labelEntry.get(), {})
        self.destroy()
