import customtkinter
from .comboModal import ComboModal
from tkinter import ttk, BooleanVar
from ..utils import genRanStr

class ComboSpellsPage(customtkinter.CTkToplevel):
    def __init__(self, context):
        super().__init__()
        self.context = context
        self.title(genRanStr())
        self.resizable(False, False)

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
            'name', 'enabled'))
        self.table.grid(row=0, column=0, rowspan=1, sticky='nsew')
        self.table.heading('name', text='Name')
        self.table.heading('enabled', text='Enabled')
        self.table.column('#0', width=0)
        self.table.column('name', width=100)
        self.table.column('enabled', width=100)

        self.table.bind('<Double-1>', self.onComboDoubleClick)

        for combo in context.context['ng_comboSpells']['items']:
            self.table.insert('', 'end', values=(
                combo['name'], combo['enabled']))
            
        self.actionsFrame = customtkinter.CTkFrame(self)
        self.actionsFrame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        self.actionsFrame.columnconfigure(0, weight=1)
        self.actionsFrame.columnconfigure(1, weight=1)
        self.actionsFrame.columnconfigure(2, weight=1)

        self.enabledVar = BooleanVar()
        self.enabledVar.set(self.context.context['ng_comboSpells']['enabled'])
        self.checkbutton = customtkinter.CTkCheckBox(
            self.actionsFrame, text='Enabled', variable=self.enabledVar, command=self.onToggleEnabledButton,
            hover_color="#870125", fg_color='#C20034')
        self.checkbutton.grid(column=0, row=0, padx=5, pady=5, sticky='w')

        self.addButton = customtkinter.CTkButton(
            self.actionsFrame, text='Add Combo', command=lambda: self.addCombo(),
            corner_radius=32, fg_color="transparent", border_color="#C20034",
            border_width=2, hover_color="#C20034")
        self.addButton.grid(row=1, column=0, padx=5, pady=5, sticky='nsew')

        self.deleteButton = customtkinter.CTkButton(
            self.actionsFrame, text='Delete Combo', command=lambda: self.deleteSelectedCombos(),
            corner_radius=32, fg_color="transparent", border_color="#C20034",
            border_width=2, hover_color="#C20034")
        self.deleteButton.grid(row=2, column=0, padx=5, pady=5, sticky='nsew')

    def addCombo(self):
        combo = {
            "enabled": False,
            "name": "Default",
            "creatures": {
                "compare": "lessThan",
                "value": 5
            },
            "spells": [],
            "currentSpellIndex": 0
        }
        self.context.addCombo(combo)
        self.table.insert('', 'end', values=(
            combo['name'], combo['enabled']))

    def deleteSelectedCombos(self):
        selectedCombos = self.table.selection()
        for combo in selectedCombos:
            indextable = self.table.index(combo)
            self.table.delete(combo)
            self.context.removeComboByIndex(indextable)

    def onComboDoubleClick(self, event):
        item = self.table.identify_row(event.y)
        if item:
            index = self.table.index(item)
            combo = self.context.context['ng_comboSpells']['items'][index]
            if self.comboModal is None or not self.comboModal.winfo_exists():
                self.comboModal = ComboModal(
                        self, combo=combo, context=self.context, index=index)
                
    def onToggleEnabledButton(self):
        enabled = self.enabledVar.get()
        self.context.toggleComboSpells(enabled)