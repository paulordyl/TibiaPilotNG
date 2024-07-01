import customtkinter
from tkinter import BooleanVar
from .pages.config import ConfigPage
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

        self.configPage = None
        self.inventoryPage = None
        self.cavebotPage = None
        self.healingPage = None
        self.comboPage = None
        self.canvasWindow = None

        configurationBtn = customtkinter.CTkButton(self, text="Configuration", corner_radius=32,
                                        fg_color="transparent", border_color="#C20034",
                                        border_width=2, hover_color="#C20034",
                                        command=self.configurationWindow)
        configurationBtn.grid(row=0, column=0, padx=20, pady=20)

        inventoryBtn = customtkinter.CTkButton(self, text="Inventory", corner_radius=32,
                                        fg_color="transparent", border_color="#C20034",
                                        border_width=2, hover_color="#C20034",
                                        command=self.inventoryWindow)
        inventoryBtn.grid(row=0, column=1, padx=20, pady=20)

        cavebotBtn = customtkinter.CTkButton(self, text="Cave", corner_radius=32,
                                        fg_color="transparent", border_color="#C20034",
                                        border_width=2, hover_color="#C20034",
                                        command=self.caveWindow)
        cavebotBtn.grid(row=0, column=2, padx=20, pady=20)

        healingBtn = customtkinter.CTkButton(self, text="Healing", corner_radius=32,
                                        fg_color="transparent", border_color="#C20034",
                                        border_width=2, hover_color="#C20034",
                                        command=self.healingWindow)
        healingBtn.grid(row=1, column=0, padx=20, pady=20)

        comboBtn = customtkinter.CTkButton(self, text="Combo Spells", corner_radius=32,
                                        fg_color="transparent", border_color="#C20034",
                                        border_width=2, hover_color="#C20034",
                                        command=self.comboWindow)
        comboBtn.grid(row=1, column=1, padx=20, pady=20)

        self.enabledVar = BooleanVar()
        self.checkbutton = customtkinter.CTkCheckBox(
            self, text='Enabled', variable=self.enabledVar, command=self.onToggleEnabledButton,
            hover_color="#870125", fg_color='#C20034')
        self.checkbutton.grid(column=2, row=1, padx=20, pady=20, sticky='w')

    def configurationWindow(self):
        if self.configPage is None or not self.configPage.winfo_exists():
            self.configPage = ConfigPage(self.context)
        else:
            self.configPage.focus()

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