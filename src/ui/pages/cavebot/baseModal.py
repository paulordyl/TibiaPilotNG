import customtkinter
from ...utils import genRanStr

class BaseModal(customtkinter.CTkToplevel):
    def __init__(self, parent, waypoint=None, onConfirm=lambda: {}):
        super().__init__(parent)        
        self.onConfirm = onConfirm

        self.title(genRanStr())
        self.resizable(False, False)

        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)

        self.frame = customtkinter.CTkFrame(self)
        self.frame.grid(column=0, row=0, columnspan=2, padx=10,
                        pady=10, sticky='nsew')
        self.frame.rowconfigure(0, weight=1)
        self.frame.rowconfigure(1, weight=1)

        self.label = customtkinter.CTkLabel(self.frame, text="Label:")
        self.label.grid(row=0, column=0, sticky='w', padx=10, pady=(10, 0))

        self.labelEntry = customtkinter.CTkEntry(self.frame)
        self.labelEntry.grid(
            row=1, column=0, sticky='nsew', padx=10, pady=10)
        if waypoint is not None and waypoint['label']:
            self.labelEntry.insert(0, waypoint['label'])

        self.confirmButton = customtkinter.CTkButton(
            self, text='Confirm', command=self.confirm,
            corner_radius=32, fg_color="transparent", border_color="#C20034",
            border_width=2, hover_color="#C20034")
        self.confirmButton.grid(
            row=6, column=0, padx=(10, 5), pady=(5, 10), sticky='nsew')

        self.cancelButton = customtkinter.CTkButton(
            self, text='Cancel', command=self.destroy,
            corner_radius=32, fg_color="transparent", border_color="#C20034",
            border_width=2, hover_color="#C20034")
        self.cancelButton.grid(
            row=6, column=1, padx=(5, 10), pady=(5, 10), sticky='nsew')

    def confirm(self):
        self.onConfirm(self.labelEntry.get(), {})
        self.destroy()
