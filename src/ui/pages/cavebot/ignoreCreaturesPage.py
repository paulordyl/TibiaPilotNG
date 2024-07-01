import customtkinter
from .ignoreCreaturesModal import IgnoreCreaturesModal
from tkinter import ttk
from ...utils import genRanStr

class IgnoreCreaturesPage(customtkinter.CTkToplevel):
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

        self.ignoreMontersModal = None

        self.columnconfigure(0, weight=8)
        self.columnconfigure(1, weight=2)
        self.rowconfigure(1, weight=1)

        self.tableFrame = customtkinter.CTkFrame(self)
        self.tableFrame.grid(row=0, column=0, rowspan=2, padx=10, pady=10, sticky="nsew")
        self.tableFrame.rowconfigure(0, weight=1)
        self.tableFrame.columnconfigure(0, weight=1)

        self.table = ttk.Treeview(self.tableFrame, columns=(
            'name'))
        self.table.grid(row=0, column=0, rowspan=1, sticky='nsew')
        self.table.heading('name', text='Name')
        self.table.column('#0', width=0)
        self.table.column('name', width=100)

        self.table.bind('<Double-1>', self.onComboDoubleClick)

        for creature in context.context['ignorable_creatures']:
            self.table.insert('', 'end', values=(creature))
            
        self.actionsFrame = customtkinter.CTkFrame(self)
        self.actionsFrame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        self.actionsFrame.columnconfigure(0, weight=1)
        self.actionsFrame.columnconfigure(1, weight=1)
        self.actionsFrame.columnconfigure(2, weight=1)

        self.addButton = customtkinter.CTkButton(
            self.actionsFrame, text='Add Creature', command=lambda: self.addCreature(),
            corner_radius=32, fg_color="transparent", border_color="#C20034",
            border_width=2, hover_color="#C20034")
        self.addButton.grid(row=0, column=0, padx=5, pady=5, sticky='nsew')

        self.deleteButton = customtkinter.CTkButton(
            self.actionsFrame, text='Delete Creature', command=lambda: self.deleteSelectedCreatures(),
            corner_radius=32, fg_color="transparent", border_color="#C20034",
            border_width=2, hover_color="#C20034")
        self.deleteButton.grid(row=1, column=0, padx=5, pady=5, sticky='nsew')

    def addCreature(self):
        self.context.addIgnorableCreature("Creature")
        self.table.insert('', 'end', values=("Creature"))

    def deleteSelectedCreatures(self):
        selectedCreatures = self.table.selection()
        for creature in selectedCreatures:
            indextable = self.table.index(creature)
            self.table.delete(creature)
            self.context.removeIgnorableCreatureByIndex(indextable)

    def onComboDoubleClick(self, event):
        item = self.table.identify_row(event.y)
        if item:
            index = self.table.index(item)
            name = self.context.context['ignorable_creatures'][index]
            if self.ignoreMontersModal is None or not self.ignoreMontersModal.winfo_exists():
                self.ignoreMontersModal = IgnoreCreaturesModal(self, name=name, onConfirm=lambda creatureName: self.updateIgnorableCreatureByIndex(index, name=creatureName))

    def updateIgnorableCreatureByIndex(self, index, name=None):
        self.context.updateIgnorableCreatureByIndex(index, name=name)
        selecionado = self.table.focus()
        if selecionado:
            currentValues = self.table.item(selecionado)['values']
            if name is not None:
                currentValues[0] = name
            self.table.item(selecionado, values=currentValues)
            self.table.update()