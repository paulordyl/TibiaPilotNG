from tkinter import messagebox, BooleanVar
import customtkinter
from ...utils import genRanStr

class RefillCheckerModal(customtkinter.CTkToplevel):
    def __init__(self, parent, onConfirm=lambda: {}, waypoint=None, waypointsLabels=[]):
        super().__init__(parent)        
        self.onConfirm = onConfirm

        self.title(genRanStr())
        self.resizable(False, False)
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)

        self.frame = customtkinter.CTkFrame(self)
        self.frame.grid(column=0, row=1, columnspan=2, padx=10,
                        pady=10, sticky='nsew')
        self.frame.rowconfigure(0, weight=1)
        self.frame.rowconfigure(1, weight=1)

        self.healthEnabledVar = BooleanVar()
        if waypoint is not None:
            healthEnabled = waypoint['options'].get('healthEnabled')
            if healthEnabled is not None:
                self.healthEnabledVar.set(healthEnabled)
        self.healthEnabledButton = customtkinter.CTkCheckBox(
            self.frame, text='Check Health', variable=self.healthEnabledVar,
            hover_color="#870125", fg_color='#C20034')
        self.healthEnabledButton.grid(column=0, row=0, padx=10, pady=10, sticky='w')

        self.minimumOfHealthPotionLabel = customtkinter.CTkLabel(
            self.frame, text='Health Potion:', anchor='w')
        self.minimumOfHealthPotionLabel.grid(
            row=1, column=0, sticky='nsew', padx=10, pady=(10, 0))

        self.minimumAmountOfHealthPotionsEntry = customtkinter.CTkEntry(self.frame, validate='key',
                                                        validatecommand=(self.register(self.validateNumber), "%P"))
        self.minimumAmountOfHealthPotionsEntry.grid(
            row=2, column=0, sticky='nsew', padx=10, pady=10)
        if waypoint is not None:
            self.minimumAmountOfHealthPotionsEntry.insert(
                0, str(waypoint['options'].get('minimumAmountOfHealthPotions')))

        self.minimumOfManaPotionLabel = customtkinter.CTkLabel(
            self.frame, text='Mana Potion:', anchor='w')
        self.minimumOfManaPotionLabel.grid(
            row=3, column=0, sticky='nsew', padx=10, pady=(10, 0))

        self.minimumAmountOfManaPotionsEntry = customtkinter.CTkEntry(self.frame, validate='key',
                                                        validatecommand=(self.register(self.validateNumber), "%P"))
        self.minimumAmountOfManaPotionsEntry.grid(
            row=4, column=0, sticky='nsew', padx=10, pady=10)
        if waypoint is not None:
            self.minimumAmountOfManaPotionsEntry.insert(
                0, str(waypoint['options'].get('minimumAmountOfManaPotions')))

        self.minimumOfCapLabel = customtkinter.CTkLabel(
            self.frame, text='Cap:', anchor='w')
        self.minimumOfCapLabel.grid(
            row=5, column=0, sticky='nsew', padx=10, pady=(10, 0))

        self.minimumAmountOfCapEntry = customtkinter.CTkEntry(self.frame, validate='key',
                                                validatecommand=(self.register(self.validateNumber), "%P"))
        self.minimumAmountOfCapEntry.grid(
            row=6, column=0, sticky='nsew', padx=10, pady=10)
        if waypoint is not None:
            self.minimumAmountOfCapEntry.insert(
                0, str(waypoint['options'].get('minimumAmountOfCap')))

        self.waypointLabelToRedirectLabel = customtkinter.CTkLabel(
            self.frame, text='Go to label:', anchor='w')
        self.waypointLabelToRedirectLabel.grid(
            row=7, column=0, sticky='nsew', padx=10, pady=(10, 0))

        self.waypointLabelToRedirectCombobox = customtkinter.CTkComboBox(
            self.frame, values=waypointsLabels, state='readonly')
        self.waypointLabelToRedirectCombobox.grid(
            row=8, column=0, sticky='nsew', padx=10, pady=10)
        if waypoint is not None and waypoint['options']['waypointLabelToRedirect'] != '':
            self.waypointLabelToRedirectCombobox.set(
                waypoint['options']['waypointLabelToRedirect'])

        self.confirmButton = customtkinter.CTkButton(
            self, text='Confirm', command=self.confirm,
            corner_radius=32, fg_color="transparent", border_color="#C20034",
            border_width=2, hover_color="#C20034")
        self.confirmButton.grid(
            row=7, column=0, padx=(10, 5), pady=(5, 10), sticky='nsew')

        self.cancelButton = customtkinter.CTkButton(
            self, text='Cancel', command=self.destroy,
            corner_radius=32, fg_color="transparent", border_color="#C20034",
            border_width=2, hover_color="#C20034")
        self.cancelButton.grid(
            row=7, column=1, padx=(5, 10), pady=(5, 10), sticky='nsew')

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
