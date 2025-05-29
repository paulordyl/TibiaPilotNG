import customtkinter
from .ignoreCreaturesModal import IgnoreCreaturesModal
from tkinter import ttk
from ...utils import genRanStr
from ...theme import MATRIX_BLACK, MATRIX_GREEN, MATRIX_GREEN_HOVER, MATRIX_GREEN_BORDER

class IgnoreCreaturesPage(customtkinter.CTkToplevel):
    def __init__(self, context):
        super().__init__()
        self.configure(fg_color=MATRIX_BLACK)
        self.context = context
        self.title(genRanStr())
        self.resizable(False, False)

        # bg_color = self._apply_appearance_mode(customtkinter.ThemeManager.theme["CTkFrame"]["fg_color"])
        # text_color = self._apply_appearance_mode(customtkinter.ThemeManager.theme["CTkLabel"]["text_color"])

        treestyle = ttk.Style()
        treestyle.theme_use('default')
        treestyle.configure("Treeview", 
                            background=MATRIX_BLACK, 
                            foreground=MATRIX_GREEN, 
                            fieldbackground=MATRIX_BLACK, 
                            borderwidth=1,
                            rowheight=25)
        treestyle.configure("Treeview.Heading", 
                            background=MATRIX_BLACK, 
                            foreground=MATRIX_GREEN, 
                            borderwidth=1,
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

        self.ignoreMontersModal = None # Variable name kept from original

        self.columnconfigure(0, weight=8)
        self.columnconfigure(1, weight=2)
        self.rowconfigure(0, weight=1) # Changed from 1 to 0 as actionsFrame is in row 0
        # self.rowconfigure(1, weight=1) # tableFrame spans 2 rows, so this might not be needed or adjust as per layout goals

        self.tableFrame = customtkinter.CTkFrame(self, fg_color=MATRIX_BLACK, border_color=MATRIX_GREEN_BORDER, border_width=1)
        self.tableFrame.grid(row=0, column=0, rowspan=2, padx=10, pady=10, sticky="nsew") # rowspan should cover actionsFrame too if it's in row 1
        self.tableFrame.rowconfigure(0, weight=1)
        self.tableFrame.columnconfigure(0, weight=1)

        self.table = ttk.Treeview(self.tableFrame, columns=('name'), style="Treeview")
        self.table.grid(row=0, column=0, rowspan=1, sticky='nsew')
        self.table.heading('name', text='Name')
        self.table.column('#0', width=0)
        self.table.column('name', width=100, anchor='w') # anchor to west for better text alignment

        self.table.bind('<Double-1>', self.onComboDoubleClick) # Original method name kept

        for creature in context.context['ignorable_creatures']:
            self.table.insert('', 'end', values=(creature,)) # Ensure values is a tuple
            
        self.actionsFrame = customtkinter.CTkFrame(self, fg_color=MATRIX_BLACK, border_color=MATRIX_GREEN_BORDER, border_width=1)
        self.actionsFrame.grid(row=0, column=1, padx=10, pady=10, sticky="ns") # sticky "ns" to fill vertically
        self.actionsFrame.columnconfigure(0, weight=1)
        # self.actionsFrame.columnconfigure(1, weight=1) # Only one column for buttons
        # self.actionsFrame.columnconfigure(2, weight=1)

        button_args = {
            "corner_radius": 32,
            "fg_color": "transparent",
            "text_color": MATRIX_GREEN,
            "border_color": MATRIX_GREEN_BORDER,
            "border_width": 2,
            "hover_color": MATRIX_GREEN_HOVER
        }

        self.addButton = customtkinter.CTkButton(
            self.actionsFrame, text='Add Creature', command=lambda: self.addCreature(), **button_args)
        self.addButton.grid(row=0, column=0, padx=5, pady=10, sticky='ew') # pady increased

        self.deleteButton = customtkinter.CTkButton(
            self.actionsFrame, text='Delete Creature', command=lambda: self.deleteSelectedCreatures(), **button_args)
        self.deleteButton.grid(row=1, column=0, padx=5, pady=10, sticky='ew') # pady increased

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