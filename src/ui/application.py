import customtkinter
from tkinter import BooleanVar
# from .pages.config import ConfigPage # Old config page
from .pages.settings_page import SettingsPage # New settings page
from .pages.comboSpells import ComboSpellsPage
from .pages.inventory import InventoryPage
from .pages.cavebot.cavebotPage import CavebotPage
from .pages.healing.healingPage import HealingPage
from .utils import genRanStr

class Application(customtkinter.CTk):
    def __init__(self, context):
        super().__init__()
        
        customtkinter.set_appearance_mode("dark")

        self.context = context
        self.title(genRanStr())
        self.resizable(False, False)

        # self.configPage = None # Old config page
        self.settingsPage = None # New settings page
        self.inventoryPage = None
        self.cavebotPage = None
        self.healingPage = None
        self.comboPage = None
        self.canvasWindow = None

        # Define the Matrix color palette
        matrix_primary_color = "#39FF14"  # Matrix green
        matrix_hover_color = "#2ECC71"    # Darker/alternative green
        matrix_text_color = "#000000"     # Black for button text
        corner_radius = 10                # Keeping corner radius

        configurationBtn = customtkinter.CTkButton(self, text="Configuration", corner_radius=corner_radius,
                                        fg_color=matrix_primary_color, border_color=matrix_primary_color,
                                        border_width=2, hover_color=matrix_hover_color,
                                        text_color=matrix_text_color,
                                        command=self.configurationWindow)
        configurationBtn.grid(row=0, column=0, padx=20, pady=20)

        inventoryBtn = customtkinter.CTkButton(self, text="Inventory", corner_radius=corner_radius,
                                        fg_color=matrix_primary_color, border_color=matrix_primary_color,
                                        border_width=2, hover_color=matrix_hover_color,
                                        text_color=matrix_text_color,
                                        command=self.inventoryWindow)
        inventoryBtn.grid(row=0, column=1, padx=20, pady=20)

        cavebotBtn = customtkinter.CTkButton(self, text="Cave", corner_radius=corner_radius,
                                        fg_color=matrix_primary_color, border_color=matrix_primary_color,
                                        border_width=2, hover_color=matrix_hover_color,
                                        text_color=matrix_text_color,
                                        command=self.caveWindow)
        cavebotBtn.grid(row=0, column=2, padx=20, pady=20)

        healingBtn = customtkinter.CTkButton(self, text="Healing", corner_radius=corner_radius,
                                        fg_color=matrix_primary_color, border_color=matrix_primary_color,
                                        border_width=2, hover_color=matrix_hover_color,
                                        text_color=matrix_text_color,
                                        command=self.healingWindow)
        healingBtn.grid(row=1, column=0, padx=20, pady=20)

        comboBtn = customtkinter.CTkButton(self, text="Combo Spells", corner_radius=corner_radius,
                                        fg_color=matrix_primary_color, border_color=matrix_primary_color,
                                        border_width=2, hover_color=matrix_hover_color,
                                        text_color=matrix_text_color,
                                        command=self.comboWindow)
        comboBtn.grid(row=1, column=1, padx=20, pady=20)

        self.enabledVar = BooleanVar()
        self.checkbutton = customtkinter.CTkCheckBox(
            self, text='Enabled', variable=self.enabledVar, command=self.onToggleEnabledButton,
            hover_color=matrix_hover_color, fg_color=matrix_primary_color)
        self.checkbutton.grid(column=2, row=1, padx=20, pady=20, sticky='w')

    def configurationWindow(self):
        if self.settingsPage is None or not self.settingsPage.winfo_exists():
            # Pass 'self' as master for the Toplevel window
            self.settingsPage = SettingsPage(self, self.context)
            self.settingsPage.grab_set() # Make it modal / focus
        else:
            self.settingsPage.focus()

    def inventoryWindow(self):
        if self.inventoryPage is None or not self.inventoryPage.winfo_exists():
            self.inventoryPage = InventoryPage(self.context)
        else:
            self.inventoryPage.focus()

    def caveWindow(self):
        if self.cavebotPage is None or not self.cavebotPage.winfo_exists():
            self.cavebotPage = CavebotPage(self.context)
        else:
            self.cavebotPage.focus()

    def healingWindow(self):
        if self.healingPage is None or not self.healingPage.winfo_exists():
            self.healingPage = HealingPage(self.context)
        else:
            self.healingPage.focus()

    def comboWindow(self):
        if self.comboPage is None or not self.comboPage.winfo_exists():
            self.comboPage = ComboSpellsPage(self.context)
        else:
            self.comboPage.focus()

    def onToggleEnabledButton(self):
        varStatus = self.enabledVar.get()

        if varStatus is True:
            self.context.play()
        else:
            self.context.pause()