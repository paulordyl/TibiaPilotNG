import customtkinter
from tkinter import ttk, BooleanVar, StringVar
from .comboSpellModal import ComboSpellModal
from ..utils import genRanStr
from ..theme import MATRIX_BLACK, MATRIX_GREEN, MATRIX_GREEN_HOVER, MATRIX_GREEN_BORDER

class ComboModal(customtkinter.CTkToplevel):
    def __init__(self, parent, combo=None, context=None, index=None):
        super().__init__(parent)
        self.configure(fg_color=MATRIX_BLACK)
        self.context = context
        self.index = index
        
        self.title(genRanStr())
        self.resizable(False, False)
        # Column configure for the main window (ComboModal itself)
        # These were defined twice, once before ttk styling and once after. Consolidating.
        self.columnconfigure(0, weight=8) # For tableFrame
        self.columnconfigure(1, weight=2) # For actionsFrame
        self.rowconfigure(0, weight=1)    # Allow actionsFrame to be in row 0
        # self.rowconfigure(1, weight=1) # tableFrame spans 2 rows, so this might not be needed

        # bg_color = self._apply_appearance_mode(customtkinter.ThemeManager.theme["CTkFrame"]["fg_color"])
        # text_color = self._apply_appearance_mode(customtkinter.ThemeManager.theme["CTkLabel"]["text_color"])

        treestyle = ttk.Style()
        treestyle.theme_use('default')
        treestyle.configure("Treeview", 
                            background=MATRIX_BLACK, 
                            foreground=MATRIX_GREEN, 
                            fieldbackground=MATRIX_BLACK, 
                            borderwidth=0,
                            rowheight=25)
        treestyle.configure("Treeview.Heading", 
                            background=MATRIX_BLACK, 
                            foreground=MATRIX_GREEN, 
                            borderwidth=0,
                            font=('TkDefaultFont', 8, 'bold'))
        
        treestyle.map('Treeview', 
                      background=[('selected', MATRIX_GREEN_BORDER)], 
                      foreground=[('selected', MATRIX_BLACK)])
        treestyle.map("Treeview.Heading",
                      background=[('pressed', '!focus', MATRIX_GREEN_HOVER), 
                                  ('active', MATRIX_GREEN_BORDER),
                                  ('disabled', MATRIX_BLACK)],
                      foreground=[('pressed', '!focus', MATRIX_BLACK),
                                  ('active', MATRIX_BLACK),
                                  ('disabled', MATRIX_GREEN_BORDER)])
        self.bind("<<TreeviewSelect>>", lambda event: self.focus_set())

        self.comboSpellModal = None # Renamed from self.comboModal to avoid conflict with class name

        frame_args = {"fg_color": MATRIX_BLACK, "border_color": MATRIX_GREEN_BORDER, "border_width": 1}
        button_args = {"corner_radius": 32, "fg_color": "transparent", "text_color": MATRIX_GREEN, "border_color": MATRIX_GREEN_BORDER, "border_width": 2, "hover_color": MATRIX_GREEN_HOVER}
        checkbox_args = {"text_color": MATRIX_GREEN, "fg_color": MATRIX_GREEN, "hover_color": MATRIX_GREEN_HOVER, "border_color": MATRIX_GREEN_BORDER, "checkmark_color": MATRIX_BLACK}
        entry_args = {"text_color": MATRIX_GREEN, "border_color": MATRIX_GREEN_BORDER, "fg_color": MATRIX_BLACK, "insertbackground": MATRIX_GREEN}
        label_args = {"text_color": MATRIX_GREEN}
        combobox_args = {"state": 'readonly', "text_color": MATRIX_GREEN, "border_color": MATRIX_GREEN_BORDER, "fg_color": MATRIX_BLACK, "button_color": MATRIX_GREEN_BORDER, "button_hover_color": MATRIX_GREEN_HOVER, "dropdown_fg_color": MATRIX_BLACK, "dropdown_hover_color": MATRIX_GREEN_HOVER, "dropdown_text_color": MATRIX_GREEN}


        self.tableFrame = customtkinter.CTkFrame(self, **frame_args)
        self.tableFrame.grid(row=0, column=0, rowspan=2, padx=10, pady=10, sticky="nsew")
        self.tableFrame.rowconfigure(0, weight=1)
        self.tableFrame.columnconfigure(0, weight=1)

        self.table = ttk.Treeview(self.tableFrame, columns=('name', 'hotkey'), style="Treeview")
        self.table.grid(row=0, column=0, rowspan=1, sticky='nsew')
        self.table.heading('name', text='Name')
        self.table.heading('hotkey', text='Hotkey')
        self.table.column('#0', width=0)
        self.table.column('name', width=100, anchor='w')
        self.table.column('hotkey', width=100, anchor='w')

        self.table.bind('<Double-1>', self.onComboDoubleClick)

        for spell in combo['spells']:
            self.table.insert('', 'end', values=(
                spell['name'], spell['hotkey']))
            
        self.actionsFrame = customtkinter.CTkFrame(self, **frame_args)
        self.actionsFrame.grid(row=0, column=1, padx=10, pady=10, sticky="ns") # sticky changed to "ns"
        self.actionsFrame.columnconfigure(0, weight=1) # All actions in one column

        self.enabledVar = BooleanVar()
        self.enabledVar.set(combo['enabled'])
        self.checkbutton = customtkinter.CTkCheckBox(
            self.actionsFrame, text='Enabled', variable=self.enabledVar, command=self.onToggleEnabledButton, **checkbox_args)
        self.checkbutton.grid(column=0, row=0, padx=10, pady=10, sticky='ew')

        self.nameLabel = customtkinter.CTkLabel(self.actionsFrame, text="Name:", **label_args) # Renamed
        self.nameLabel.grid(row=1, column=0, sticky='w', padx=10, pady=(10, 0))

        self.labelEntryVar = StringVar()
        self.labelEntryVar.set(combo['name'])
        self.labelEntryVar.trace_add('write', self.changeComboName)
        self.nameEntry = customtkinter.CTkEntry(self.actionsFrame, textvariable=self.labelEntryVar, **entry_args) # Renamed
        self.nameEntry.grid(
            row=2, column=0, sticky='ew', padx=10, pady=5)
        
        self.whenLabel = customtkinter.CTkLabel(self.actionsFrame, text="When:", **label_args) # Renamed
        self.whenLabel.grid(row=3, column=0, sticky='w', padx=10, pady=(5, 0))

        self.compareCondition = customtkinter.CTkComboBox(
            self.actionsFrame, values=['lessThan', 'lessThanOrEqual', 'greaterThan', 'greaterThanOrEqual'], 
            command=self.onChangeCompare, **combobox_args)
        self.compareCondition.set(combo['creatures']['compare'])
        self.compareCondition.grid(column=0, row=4, sticky='ew', padx=10, pady=5)

        self.whenValueLabel = customtkinter.CTkLabel(self.actionsFrame, text="When value:", **label_args) # Renamed
        self.whenValueLabel.grid(row=5, column=0, sticky='w', padx=10, pady=(5, 0))

        self.compareValueVar = StringVar()
        self.compareValueVar.set(combo['creatures']['value'])
        self.compareValueVar.trace_add('write', self.changeCompareValue)
        self.compareValueEntry = customtkinter.CTkEntry(self.actionsFrame, textvariable=self.compareValueVar, **entry_args) # Renamed
        self.compareValueEntry.grid(
            row=6, column=0, sticky='ew', padx=10, pady=5)

        self.addButton = customtkinter.CTkButton(
            self.actionsFrame, text='Add Spell', command=lambda: self.addSpell(), **button_args)
        self.addButton.grid(row=7, column=0, padx=10, pady=10, sticky='ew')

        self.deleteButton = customtkinter.CTkButton(
            self.actionsFrame, text='Delete Spell', command=lambda: self.removeSelectedSpells(), **button_args)
        self.deleteButton.grid(row=8, column=0, padx=10, pady=10, sticky='ew')

    def addSpell(self):
        spell = {
            "name": "exori",
            "hotkey": "f4"
        }
        self.context.addSpellByIndex(self.index, spell)
        self.table.insert('', 'end', values=(
            spell['name'], spell['hotkey']))

    def removeSelectedSpells(self):
        selectedSpells = self.table.selection()
        for spell in selectedSpells:
            indextable = self.table.index(spell)
            self.table.delete(spell)
            self.context.removeSpellByIndex(self.index, indextable)

    def changeComboName(self, var, index, mode):
        name = self.labelEntryVar.get()
        self.context.changeComboName(name, self.index)

    def changeCompareValue(self, var, index, mode):
        compareValue = self.compareValueVar.get()
        self.context.changeCompareValue(compareValue, self.index)

    def onToggleEnabledButton(self):
        enabled = self.enabledVar.get()
        self.context.toggleSingleCombo(enabled, self.index)

    def onChangeCompare(self, _):
        selectedCompare = self.compareCondition.get()
        self.context.setCompare(selectedCompare, index=self.index)

    def onComboDoubleClick(self, event):
        item = self.table.identify_row(event.y)
        if item:
            indexSecond = self.table.index(item)
            spell = self.context.context['ng_comboSpells']['items'][self.index]['spells'][indexSecond]
            if self.comboModal is None or not self.comboModal.winfo_exists():
                self.comboModal = ComboSpellModal(
                        self, spell=spell, context=self.context, index=self.index, indexSecond=indexSecond)