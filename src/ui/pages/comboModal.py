import customtkinter
from tkinter import ttk, BooleanVar, StringVar
from .comboSpellModal import ComboSpellModal
from ..utils import genRanStr

class ComboModal(customtkinter.CTkToplevel):
    def __init__(self, parent, combo=None, context=None, index=None):
        super().__init__(parent)
        self.context = context
        self.index = index
        

        self.title(genRanStr())
        self.resizable(False, False)
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)

        bg_color = self._apply_appearance_mode(customtkinter.ThemeManager.theme["CTkFrame"]["fg_color"])
        text_color = self._apply_appearance_mode(customtkinter.ThemeManager.theme["CTkLabel"]["text_color"])

        treestyle = ttk.Style()
        treestyle.theme_use('default')
        treestyle.configure("Treeview", background=bg_color, foreground=text_color, fieldbackground=bg_color, borderwidth=0)
        treestyle.configure("Treeview.Heading", background=bg_color, borderwidth=0, foreground="#C20034")
        ttk.Style().map("Treeview.Heading",
                background = [('pressed', '!focus', bg_color),
                            ('active', bg_color),
                            ('disabled',"#C20034")])
        treestyle.map('Treeview', background=[('selected', '#C20034')], foreground=[('selected', '#FFF')])
        self.bind("<<TreeviewSelect>>", lambda event: self.focus_set())

        self.comboModal = None

        self.columnconfigure(0, weight=8)
        self.columnconfigure(1, weight=2)
        self.rowconfigure(1, weight=1)

        self.tableFrame = customtkinter.CTkFrame(self)
        self.tableFrame.grid(row=0, column=0, rowspan=2, padx=10, pady=10, sticky="nsew")
        self.tableFrame.rowconfigure(0, weight=1)
        self.tableFrame.columnconfigure(0, weight=1)

        self.table = ttk.Treeview(self.tableFrame, columns=(
            'name', 'hotkey'))
        self.table.grid(row=0, column=0, rowspan=1, sticky='nsew')
        self.table.heading('name', text='Name')
        self.table.heading('hotkey', text='Hotkey')
        self.table.column('#0', width=0)
        self.table.column('name', width=100)
        self.table.column('hotkey', width=100)

        self.table.bind('<Double-1>', self.onComboDoubleClick)

        for spell in combo['spells']:
            self.table.insert('', 'end', values=(
                spell['name'], spell['hotkey']))
            
        self.actionsFrame = customtkinter.CTkFrame(self)
        self.actionsFrame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        self.actionsFrame.columnconfigure(0, weight=1)
        self.actionsFrame.columnconfigure(1, weight=1)
        self.actionsFrame.columnconfigure(2, weight=1)

        self.enabledVar = BooleanVar()
        self.enabledVar.set(combo['enabled'])
        self.checkbutton = customtkinter.CTkCheckBox(
            self.actionsFrame, text='Enabled', variable=self.enabledVar, command=self.onToggleEnabledButton,
            hover_color="#870125", fg_color='#C20034')
        self.checkbutton.grid(column=0, row=0, padx=5, pady=5, sticky='w')

        self.label = customtkinter.CTkLabel(self.actionsFrame, text="Name:")
        self.label.grid(row=1, column=0, sticky='w', padx=5, pady=(5, 0))

        self.labelEntryVar = StringVar()
        self.labelEntryVar.set(combo['name'])
        self.labelEntryVar.trace_add('write', self.changeComboName)
        self.labelEntry = customtkinter.CTkEntry(self.actionsFrame, textvariable=self.labelEntryVar)
        self.labelEntry.grid(
            row=2, column=0, sticky='nsew', padx=5, pady=5)
        
        self.label = customtkinter.CTkLabel(self.actionsFrame, text="When:")
        self.label.grid(row=3, column=0, sticky='w', padx=5, pady=(5, 0))

        self.compareCondition = customtkinter.CTkComboBox(
            self.actionsFrame, values=['lessThan', 'lessThanOrEqual', 'greaterThan', 'greaterThanOrEqual'], state='readonly',
            command=self.onChangeCompare)
        self.compareCondition.set(combo['creatures']['compare'])
        self.compareCondition.grid(column=0, row=4, sticky='ew', padx=5, pady=5)

        self.label = customtkinter.CTkLabel(self.actionsFrame, text="When value:")
        self.label.grid(row=5, column=0, sticky='w', padx=5, pady=(5, 0))

        self.compareValueVar = StringVar()
        self.compareValueVar.set(combo['creatures']['value'])
        self.compareValueVar.trace_add('write', self.changeCompareValue)
        self.compareValue = customtkinter.CTkEntry(self.actionsFrame, textvariable=self.compareValueVar)
        self.compareValue.grid(
            row=6, column=0, sticky='nsew', padx=5, pady=5)

        self.addButton = customtkinter.CTkButton(
            self.actionsFrame, text='Add Spell', command=lambda: self.addSpell(),
            corner_radius=32, fg_color="transparent", border_color="#C20034",
            border_width=2, hover_color="#C20034")
        self.addButton.grid(row=7, column=0, padx=5, pady=5, sticky='nsew')

        self.deleteButton = customtkinter.CTkButton(
            self.actionsFrame, text='Delete Spell', command=lambda: self.removeSelectedSpells(),
            corner_radius=32, fg_color="transparent", border_color="#C20034",
            border_width=2, hover_color="#C20034")
        self.deleteButton.grid(row=8, column=0, padx=5, pady=5, sticky='nsew')

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