from tkinter import messagebox
import customtkinter
from ..utils import genRanStr
from ..theme import MATRIX_BLACK, MATRIX_GREEN, MATRIX_GREEN_HOVER, MATRIX_GREEN_BORDER

class InventoryPage(customtkinter.CTkToplevel):
    backpacks = [
        '25 Years Backpack',
        'Anniversary Backpack',
        'Beach Backpack',
        'Birthday Backpack',
        'Brocade Backpack',
        'Buggy Backpack',
        'Cake Backpack',
        'Camouflage Backpack',
        'Crown Backpack',
        'Crystal Backpack',
        'Deepling Backpack',
        'Demon Backpack',
        'Dragon Backpack',
        'Expedition Backpack',
        'Fur Backpack',
        'Glooth Backpack',
        'Heart Backpack',
        'Minotaur Backpack',
        'Moon Backpack',
        'Mushroom Backpack',
        'Pannier Backpack',
        'Pirate Backpack',
        'Raccoon Backpack',
        'Santa Backpack',
        'Wolf Backpack',
    ]

    def __init__(self, context):
        super().__init__()
        self.configure(fg_color=MATRIX_BLACK)
        self.context = context

        self.title(genRanStr())
        self.resizable(False, False)

        self.mainBackpackFrame = customtkinter.CTkFrame(self, fg_color=MATRIX_BLACK, border_color=MATRIX_GREEN_BORDER, border_width=1)
        self.mainBackpackFrame.grid(column=0, row=0, padx=10,
                                    pady=10, sticky='nsew')

        self.mainBackpackFrame.rowconfigure(0, weight=1)
        self.mainBackpackFrame.columnconfigure(0, weight=1)

        self.mainBackpackLabel = customtkinter.CTkLabel(self.mainBackpackFrame, text="Main Backpack:", text_color=MATRIX_GREEN)
        self.mainBackpackLabel.grid(row=0, column=0, sticky='w', padx=10, pady=(10, 0))

        self.listOfMainBackpacksCombobox = customtkinter.CTkComboBox(
            self.mainBackpackFrame, values=self.backpacks, state='readonly',
            command=self.setMainBackpack, text_color=MATRIX_GREEN, border_color=MATRIX_GREEN_BORDER,
            fg_color=MATRIX_BLACK, button_color=MATRIX_GREEN_BORDER, button_hover_color=MATRIX_GREEN_HOVER,
            dropdown_fg_color=MATRIX_BLACK, dropdown_hover_color=MATRIX_GREEN_HOVER, dropdown_text_color=MATRIX_GREEN)
        if self.context.enabledProfile is not None and self.context.enabledProfile['config']['ng_backpacks']['main'] is not None:
            self.listOfMainBackpacksCombobox.set(
                self.context.enabledProfile['config']['ng_backpacks']['main'])
        self.listOfMainBackpacksCombobox.grid(row=1, column=0, sticky='ew', padx=10, pady=10)

        self.lootBackpackFrame = customtkinter.CTkFrame(self, fg_color=MATRIX_BLACK, border_color=MATRIX_GREEN_BORDER, border_width=1)
        self.lootBackpackFrame.grid(
            row=0, column=1, padx=10, pady=10, sticky='nsew')

        self.lootBackpackFrame.rowconfigure(0, weight=1)
        self.lootBackpackFrame.columnconfigure(0, weight=1)

        self.lootBackpackLabel = customtkinter.CTkLabel(self.lootBackpackFrame, text="Loot Backpack:", text_color=MATRIX_GREEN)
        self.lootBackpackLabel.grid(row=0, column=0, sticky='w', padx=10, pady=(10, 0))

        self.listOfLootBackpacksombobox = customtkinter.CTkComboBox(
            self.lootBackpackFrame, values=self.backpacks, state='readonly',
            command=self.setLootBackpack, text_color=MATRIX_GREEN, border_color=MATRIX_GREEN_BORDER,
            fg_color=MATRIX_BLACK, button_color=MATRIX_GREEN_BORDER, button_hover_color=MATRIX_GREEN_HOVER,
            dropdown_fg_color=MATRIX_BLACK, dropdown_hover_color=MATRIX_GREEN_HOVER, dropdown_text_color=MATRIX_GREEN)
        if self.context.enabledProfile is not None and self.context.enabledProfile['config']['ng_backpacks']['loot'] is not None:
            self.listOfLootBackpacksombobox.set(
                self.context.enabledProfile['config']['ng_backpacks']['loot'])
        self.listOfLootBackpacksombobox.grid(row=1, column=0, sticky='ew', padx=10, pady=10)

        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self.columnconfigure(1, weight=1)

    def setMainBackpack(self, _):
        if not self.canChangeBackpack():
            self.listOfMainBackpacksCombobox.set(
                self.context.enabledProfile['config']['ng_backpacks']['main'])
            messagebox.showerror(
                'Erro', 'The Main Backpack has to be different from the Loot Backpack!')
            return
        self.context.updateMainBackpack(self.listOfMainBackpacksCombobox.get())

    def setLootBackpack(self, _):
        if not self.canChangeBackpack():
            self.listOfLootBackpacksombobox.set(
                self.context.enabledProfile['config']['ng_backpacks']['loot'])
            messagebox.showerror(
                'Erro', 'The Loot Backpack has to be different from the Main Backpack!')
            return
        self.context.updateLootBackpack(self.listOfLootBackpacksombobox.get())

    def canChangeBackpack(self):
        return self.listOfMainBackpacksCombobox.get(
        ) != self.listOfLootBackpacksombobox.get()
