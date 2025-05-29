import customtkinter
from .comboModal import ComboModal
from tkinter import ttk, BooleanVar
from ..utils import genRanStr
from ..theme import MATRIX_BLACK, MATRIX_GREEN, MATRIX_GREEN_HOVER, MATRIX_GREEN_BORDER

class ComboSpellsPage(customtkinter.CTkToplevel):
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
                            borderwidth=0, # Set borderwidth to 0 as per original
                            rowheight=25) 
        treestyle.configure("Treeview.Heading", 
                            background=MATRIX_BLACK, 
                            foreground=MATRIX_GREEN, # Changed from #C20034
                            borderwidth=0, # Set borderwidth to 0 as per original
                            font=('TkDefaultFont', 8, 'bold'))
        
        # Map for selected items and heading states
        treestyle.map('Treeview', 
                      background=[('selected', MATRIX_GREEN_BORDER)], 
                      foreground=[('selected', MATRIX_BLACK)])
        # Original heading map was complex, simplifying for Matrix theme
        # Keeping heading background black, foreground green, active/pressed states using theme colors
        treestyle.map("Treeview.Heading",
                      background=[('pressed', '!focus', MATRIX_GREEN_HOVER), 
                                  ('active', MATRIX_GREEN_BORDER),
                                  ('disabled', MATRIX_BLACK)],
                      foreground=[('pressed', '!focus', MATRIX_BLACK),
                                  ('active', MATRIX_BLACK),
                                  ('disabled', MATRIX_GREEN_BORDER)])
        self.bind("<<TreeviewSelect>>", lambda event: self.focus_set())

        self.comboModal = None

        self.columnconfigure(0, weight=8)
        self.columnconfigure(1, weight=2)
        self.rowconfigure(0, weight=1) # Adjusted to allow actionsFrame to be in row 0
        # self.rowconfigure(1, weight=1) # tableFrame spans 2 rows

        self.tableFrame = customtkinter.CTkFrame(self, fg_color=MATRIX_BLACK, border_color=MATRIX_GREEN_BORDER, border_width=1)
        self.tableFrame.grid(row=0, column=0, rowspan=2, padx=10, pady=10, sticky="nsew")
        self.tableFrame.rowconfigure(0, weight=1)
        self.tableFrame.columnconfigure(0, weight=1)

        self.table = ttk.Treeview(self.tableFrame, columns=(
            'name', 'enabled'), style="Treeview")
        self.table.grid(row=0, column=0, rowspan=1, sticky='nsew')
        self.table.heading('name', text='Name')
        self.table.heading('enabled', text='Enabled')
        self.table.column('#0', width=0)
        self.table.column('name', width=100, anchor='w')
        self.table.column('enabled', width=100, anchor='w')

        self.table.bind('<Double-1>', self.onComboDoubleClick)

        for combo in context.context['ng_comboSpells']['items']:
            self.table.insert('', 'end', values=(
                combo['name'], combo['enabled']))
            
        self.actionsFrame = customtkinter.CTkFrame(self, fg_color=MATRIX_BLACK, border_color=MATRIX_GREEN_BORDER, border_width=1)
        self.actionsFrame.grid(row=0, column=1, padx=10, pady=10, sticky="ns") # sticky changed to "ns"
        self.actionsFrame.columnconfigure(0, weight=1) # Only one column needed for these buttons
        # self.actionsFrame.columnconfigure(1, weight=1) 
        # self.actionsFrame.columnconfigure(2, weight=1)

        checkbox_args = {
            "text_color": MATRIX_GREEN,
            "fg_color": MATRIX_GREEN,
            "hover_color": MATRIX_GREEN_HOVER,
            "border_color": MATRIX_GREEN_BORDER,
            "checkmark_color": MATRIX_BLACK
        }

        button_args = {
            "corner_radius": 32,
            "fg_color": "transparent", # Or MATRIX_BLACK
            "text_color": MATRIX_GREEN,
            "border_color": MATRIX_GREEN_BORDER,
            "border_width": 2,
            "hover_color": MATRIX_GREEN_HOVER
        }

        self.enabledVar = BooleanVar()
        self.enabledVar.set(self.context.context['ng_comboSpells']['enabled'])
        self.checkbutton = customtkinter.CTkCheckBox(
            self.actionsFrame, text='Enabled', variable=self.enabledVar, command=self.onToggleEnabledButton, **checkbox_args)
        self.checkbutton.grid(column=0, row=0, padx=10, pady=10, sticky='ew') # padx/pady increased, sticky ew

        self.addButton = customtkinter.CTkButton(
            self.actionsFrame, text='Add Combo', command=lambda: self.addCombo(), **button_args)
        self.addButton.grid(row=1, column=0, padx=10, pady=10, sticky='ew')

        self.deleteButton = customtkinter.CTkButton(
            self.actionsFrame, text='Delete Combo', command=lambda: self.deleteSelectedCombos(), **button_args)
        self.deleteButton.grid(row=2, column=0, padx=10, pady=10, sticky='ew')

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