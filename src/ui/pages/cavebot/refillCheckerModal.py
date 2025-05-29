from tkinter import messagebox, BooleanVar
import customtkinter
from ...utils import genRanStr
from ...theme import MATRIX_BLACK, MATRIX_GREEN, MATRIX_GREEN_HOVER, MATRIX_GREEN_BORDER

class RefillCheckerModal(customtkinter.CTkToplevel):
    def __init__(self, parent, onConfirm=lambda: {}, waypoint=None, waypointsLabels=[]):
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

        checkbox_args = {
            "text_color": MATRIX_GREEN,
            "fg_color": MATRIX_GREEN,
            "hover_color": MATRIX_GREEN_HOVER,
            "border_color": MATRIX_GREEN_BORDER,
            "checkmark_color": MATRIX_BLACK
        }
        
        label_args = {"text_color": MATRIX_GREEN, "anchor": "w"}

        entry_args = {
            "validate": 'key',
            "validatecommand": (self.register(self.validateNumber), "%P"),
            "text_color": MATRIX_GREEN,
            "border_color": MATRIX_GREEN_BORDER,
            "fg_color": MATRIX_BLACK,
            "insertbackground": MATRIX_GREEN
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
        # Frame should be in row 0, buttons in row 1
        self.frame.grid(column=0, row=0, columnspan=2, padx=10, pady=10, sticky='nsew')
        # Configure columns inside the frame
        self.frame.columnconfigure(0, weight=1) # Allow widgets to expand if sticky='ew'

        self.healthEnabledVar = BooleanVar()
        if waypoint is not None:
            healthEnabled = waypoint['options'].get('healthEnabled')
            if healthEnabled is not None:
                self.healthEnabledVar.set(healthEnabled)
        self.healthEnabledButton = customtkinter.CTkCheckBox(
            self.frame, text='Check Health', variable=self.healthEnabledVar, **checkbox_args)
        self.healthEnabledButton.grid(column=0, row=0, padx=10, pady=10, sticky='w')

        self.minimumOfHealthPotionLabel = customtkinter.CTkLabel(
            self.frame, text='Health Potion:', **label_args)
        self.minimumOfHealthPotionLabel.grid(
            row=1, column=0, sticky='ew', padx=10, pady=(10, 0))

        self.minimumAmountOfHealthPotionsEntry = customtkinter.CTkEntry(self.frame, **entry_args)
        self.minimumAmountOfHealthPotionsEntry.grid(
            row=2, column=0, sticky='ew', padx=10, pady=10)
        if waypoint is not None and waypoint['options'].get('minimumAmountOfHealthPotions') is not None:
            self.minimumAmountOfHealthPotionsEntry.insert(
                0, str(waypoint['options']['minimumAmountOfHealthPotions']))

        self.minimumOfManaPotionLabel = customtkinter.CTkLabel(
            self.frame, text='Mana Potion:', **label_args)
        self.minimumOfManaPotionLabel.grid(
            row=3, column=0, sticky='ew', padx=10, pady=(10, 0))

        self.minimumAmountOfManaPotionsEntry = customtkinter.CTkEntry(self.frame, **entry_args)
        self.minimumAmountOfManaPotionsEntry.grid(
            row=4, column=0, sticky='ew', padx=10, pady=10)
        if waypoint is not None and waypoint['options'].get('minimumAmountOfManaPotions') is not None:
            self.minimumAmountOfManaPotionsEntry.insert(
                0, str(waypoint['options']['minimumAmountOfManaPotions']))

        self.minimumOfCapLabel = customtkinter.CTkLabel(
            self.frame, text='Cap:', **label_args)
        self.minimumOfCapLabel.grid(
            row=5, column=0, sticky='ew', padx=10, pady=(10, 0))

        self.minimumAmountOfCapEntry = customtkinter.CTkEntry(self.frame, **entry_args)
        self.minimumAmountOfCapEntry.grid(
            row=6, column=0, sticky='ew', padx=10, pady=10)
        if waypoint is not None and waypoint['options'].get('minimumAmountOfCap') is not None:
            self.minimumAmountOfCapEntry.insert(
                0, str(waypoint['options']['minimumAmountOfCap']))

        self.waypointLabelToRedirectLabel = customtkinter.CTkLabel(
            self.frame, text='Go to label:', **label_args)
        self.waypointLabelToRedirectLabel.grid(
            row=7, column=0, sticky='ew', padx=10, pady=(10, 0))

        self.waypointLabelToRedirectCombobox = customtkinter.CTkComboBox(
            self.frame, values=waypointsLabels, **combobox_args)
        self.waypointLabelToRedirectCombobox.grid(
            row=8, column=0, sticky='ew', padx=10, pady=10)
        if waypoint is not None and waypoint['options'].get('waypointLabelToRedirect', '') != '':
            self.waypointLabelToRedirectCombobox.set(
                waypoint['options']['waypointLabelToRedirect'])

        self.confirmButton = customtkinter.CTkButton(
            self, text='Confirm', command=self.confirm, **button_args)
        self.confirmButton.grid(
            row=1, column=0, padx=(10, 5), pady=(5, 10), sticky='nsew') # row changed to 1

        self.cancelButton = customtkinter.CTkButton(
            self, text='Cancel', command=self.destroy, **button_args)
        self.cancelButton.grid(
            row=1, column=1, padx=(5, 10), pady=(5, 10), sticky='nsew') # row changed to 1

    def validateNumber(self, value: int) -> bool:
        if value.isdigit() and int(value) > 0:
            return True
        messagebox.showerror(
            'Error', "Digite um número válido maior que zero.")
        return False

    def confirm(self):
        self.onConfirm(None, {
            'minimumAmountOfHealthPotions': int(self.minimumAmountOfHealthPotionsEntry.get()),
            'minimumAmountOfManaPotions': int(self.minimumAmountOfManaPotionsEntry.get()),
            'minimumAmountOfCap': int(self.minimumAmountOfCapEntry.get()),
            'waypointLabelToRedirect': self.waypointLabelToRedirectCombobox.get(),
            'healthEnabled': self.healthEnabledVar.get(),
        })
        self.destroy()
