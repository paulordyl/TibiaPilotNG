from tkinter import messagebox, ttk, StringVar, BooleanVar, filedialog
from src.repositories.radar.core import getCoordinate
from src.utils.core import getScreenshot
from .baseModal import BaseModal
from .refillModal import RefillModal
from .buyBackpackModal import BuyBackpackModal
from .depositItemsModal import DepositItemsModal
from .travelModal import TravelModal
from .refillCheckerModal import RefillCheckerModal
from .ignoreCreaturesPage import IgnoreCreaturesPage
import customtkinter
import json
from ...utils import genRanStr
from ...theme import MATRIX_BLACK, MATRIX_GREEN, MATRIX_GREEN_HOVER, MATRIX_GREEN_BORDER

class CavebotPage(customtkinter.CTkToplevel):
    def __init__(self, context):
        super().__init__()
        self.configure(fg_color=MATRIX_BLACK)
        self.context = context

        self.title(genRanStr())
        self.resizable(False, False)

        self.ignoreCreaturesPage = None

        # bg_color = self._apply_appearance_mode(customtkinter.ThemeManager.theme["CTkFrame"]["fg_color"])
        # text_color = self._apply_appearance_mode(customtkinter.ThemeManager.theme["CTkLabel"]["text_color"])

        treestyle = ttk.Style()
        treestyle.theme_use('default') # Or another base theme if 'default' causes issues with Matrix
        treestyle.configure("Treeview", 
                            background=MATRIX_BLACK, 
                            foreground=MATRIX_GREEN, 
                            fieldbackground=MATRIX_BLACK, 
                            borderwidth=1, # Can be 0 if no border is preferred
                            rowheight=25) # Optional: adjust row height
        treestyle.configure("Treeview.Heading", 
                            background=MATRIX_BLACK, 
                            foreground=MATRIX_GREEN, 
                            borderwidth=1, # Can be 0 or 1
                            font=('TkDefaultFont', 8, 'bold')) # Font styling
        
        # Map for selected items and heading states
        treestyle.map('Treeview', 
                      background=[('selected', MATRIX_GREEN_BORDER)], 
                      foreground=[('selected', MATRIX_BLACK)])
        treestyle.map("Treeview.Heading",
                      background=[('pressed', '!focus', MATRIX_GREEN_HOVER), 
                                  ('active', MATRIX_GREEN_BORDER),
                                  ('disabled', MATRIX_BLACK)], # Keep disabled heading subtle
                      foreground=[('pressed', '!focus', MATRIX_BLACK),
                                  ('active', MATRIX_BLACK),
                                  ('disabled', MATRIX_GREEN_BORDER)])

        self.bind("<<TreeviewSelect>>", lambda event: self.focus_set())

        self.columnconfigure(0, weight=8)
        self.columnconfigure(1, weight=2)
        self.rowconfigure(1, weight=1)
        self.baseModal = None
        self.refillModal = None
        self.backpackModal = None
        self.refillCheckerModal = None
        self.depositItemsModal = None
        self.travelModal = None

        self.tableFrame = customtkinter.CTkFrame(self, fg_color=MATRIX_BLACK, border_color=MATRIX_GREEN_BORDER, border_width=1)
        self.tableFrame.grid(row=0, column=0, rowspan=2, padx=10, pady=10, sticky="nsew")
        self.tableFrame.rowconfigure(0, weight=1)
        self.tableFrame.columnconfigure(0, weight=1)

        self.table = ttk.Treeview(self.tableFrame, columns=(
            'label', 'type', 'coordinate', 'options'), style="Treeview")
        self.table.grid(row=0, column=0, rowspan=1, sticky='nsew')
        self.table.heading('label', text='Label')
        self.table.heading('type', text='Type')
        self.table.heading('coordinate', text='Coordinate')
        self.table.heading('options', text='Options')
        self.table.column('#0', width=0)
        self.table.column('label', width=100)
        self.table.column('type', width=100)
        self.table.column('coordinate', width=100)
        self.table.column('options', width=100)

        self.table.bind('<Double-1>', self.onWaypointDoubleClick)

        for waypoint in context.context['ng_cave']['waypoints']['items']:
            self.table.insert('', 'end', values=(
                waypoint['label'], waypoint['type'], waypoint['coordinate'], waypoint['options']))
            
        self.directionsFrame = customtkinter.CTkFrame(self, fg_color=MATRIX_BLACK, border_color=MATRIX_GREEN_BORDER, border_width=1)
        self.directionsFrame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        self.directionsFrame.columnconfigure(0, weight=1)
        self.directionsFrame.columnconfigure(1, weight=1)
        self.directionsFrame.columnconfigure(2, weight=1)

        self.waypointDirection = StringVar(value='center')

        radio_button_args = {
            "variable": self.waypointDirection, 
            "text_color": MATRIX_GREEN,
            "fg_color": MATRIX_GREEN, 
            "hover_color": MATRIX_GREEN_HOVER,
            "border_color": MATRIX_GREEN_BORDER
        }

        northOption = customtkinter.CTkRadioButton(self.directionsFrame, text='North', value='north', **radio_button_args)
        northOption.grid(row=0, column=1)

        westOption = customtkinter.CTkRadioButton(self.directionsFrame, text='West', value='west', **radio_button_args)
        westOption.grid(row=1, column=0)

        centerOption = customtkinter.CTkRadioButton(self.directionsFrame, text='Center', value='center', **radio_button_args)
        centerOption.grid(row=1, column=1, pady=10)

        eastOption = customtkinter.CTkRadioButton(self.directionsFrame, text='East', value='east', **radio_button_args)
        eastOption.grid(row=1, column=2)

        southOption = customtkinter.CTkRadioButton(self.directionsFrame, text='South', value='south', **radio_button_args)
        southOption.grid(row=2, column=1)

        self.actionsFrame = customtkinter.CTkFrame(self, fg_color=MATRIX_BLACK, border_color=MATRIX_GREEN_BORDER, border_width=1)
        self.actionsFrame.grid(row=1, column=1, padx=10, pady=10, sticky="nsew")
        self.actionsFrame.columnconfigure(0, weight=1, uniform='equal')
        self.actionsFrame.columnconfigure(1, weight=1, uniform='equal')

        checkbox_args = {
            "text_color": MATRIX_GREEN,
            "fg_color": MATRIX_GREEN,
            "hover_color": MATRIX_GREEN_HOVER,
            "border_color": MATRIX_GREEN_BORDER,
            "checkmark_color": MATRIX_BLACK
        }
        
        button_args = {
            "corner_radius": 32,
            "fg_color": "transparent",
            "text_color": MATRIX_GREEN,
            "border_color": MATRIX_GREEN_BORDER,
            "border_width": 2,
            "hover_color": MATRIX_GREEN_HOVER
        }

        self.enabledVar = BooleanVar()
        self.enabledVar.set(self.context.context['ng_cave']['enabled'])
        self.checkbutton = customtkinter.CTkCheckBox(
            self.actionsFrame, text='Enabled', variable=self.enabledVar, command=self.onToggleEnabledButton, **checkbox_args)
        self.checkbutton.grid(column=0, row=0, padx=5, pady=5, sticky='w')

        self.runToCreaturesVar = BooleanVar()
        self.runToCreaturesVar.set(self.context.context['ng_cave']['runToCreatures'])
        self.runToCreaturesButton = customtkinter.CTkCheckBox(
            self.actionsFrame, text='Run to creatures', variable=self.runToCreaturesVar, command=self.onToggleRunButton, **checkbox_args)
        self.runToCreaturesButton.grid(column=1, row=0, padx=5, pady=5, sticky='w')

        self.deleteWaypoints = customtkinter.CTkButton(
            self.actionsFrame, text='Delete Waypoints', command=lambda: self.removeSelectedWaypoints(), **button_args)
        self.deleteWaypoints.grid(row=1, column=0, padx=5, pady=5, sticky='nsew')
        self.depositItemsHouseButton = customtkinter.CTkButton(
            self.actionsFrame, text='Deposit House', command=lambda: self.addWaypoint('depositItemsHouse'), **button_args)
        self.depositItemsHouseButton.grid(
            row=1, column=1, padx=5, pady=5, sticky='nsew')

        self.walkButton = customtkinter.CTkButton(
            self.actionsFrame, text='Walk', command=lambda: self.addWaypoint('walk'), **button_args)
        self.walkButton.grid(row=2, column=0, padx=5, pady=5, sticky='nsew')

        self.rightClickDirectionButton = customtkinter.CTkButton(
            self.actionsFrame, text='RC Direction', command=lambda: self.addWaypoint('rightClickDirection'), **button_args)
        self.rightClickDirectionButton.grid(row=2, column=1, padx=5, pady=5, sticky='nsew')

        self.walkIgnoreButton = customtkinter.CTkButton( # Renamed variable for clarity
            self.actionsFrame, text='Walk Ignore', command=lambda: self.addWaypoint('walk', ignore=True), **button_args)
        self.walkIgnoreButton.grid(row=3, column=0, padx=5, pady=5, sticky='nsew')

        self.walkIgnorePassinhoButton = customtkinter.CTkButton( # Renamed variable for clarity
            self.actionsFrame, text='Walk Ignore Passinho', command=lambda: self.addWaypoint('walk', ignore=True, passinho=True), **button_args)
        self.walkIgnorePassinhoButton.grid(row=3, column=1, padx=5, pady=5, sticky='nsew')

        self.ropeButton = customtkinter.CTkButton(
            self.actionsFrame, text='Rope', command=lambda: self.addWaypoint('useRope'), **button_args)
        self.ropeButton.grid(row=4, column=0, padx=5, pady=5, sticky='nsew')

        self.shovelButton = customtkinter.CTkButton(
            self.actionsFrame, text='Shovel', command=lambda: self.addWaypoint('useShovel'), **button_args)
        self.shovelButton.grid(row=4, column=1, padx=5, pady=5, sticky='nsew')

        self.rightClickUseButton = customtkinter.CTkButton(
            self.actionsFrame, text='Use Right Click', command=lambda: self.addWaypoint('rightClickUse'), **button_args)
        self.rightClickUseButton.grid(row=5, column=0, padx=5, pady=5, sticky='nsew')

        self.openDoorButton = customtkinter.CTkButton(
            self.actionsFrame, text='Open Door', command=lambda: self.addWaypoint('openDoor'), **button_args)
        self.openDoorButton.grid(row=5, column=1, padx=5, pady=5, sticky='nsew')

        self.singleMoveButton = customtkinter.CTkButton(
            self.actionsFrame, text='Single Move', command=lambda: self.addWaypoint('singleMove'), **button_args)
        self.singleMoveButton.grid(row=6, column=0, padx=5, pady=5, sticky='nsew')

        self.useLadderButton = customtkinter.CTkButton(
            self.actionsFrame, text='Use Ladder', command=lambda: self.addWaypoint('useLadder'), **button_args)
        self.useLadderButton.grid(row=6, column=1, padx=5, pady=5, sticky='nsew')

        self.moveUpButton = customtkinter.CTkButton(
            self.actionsFrame, text='Move Up', command=lambda: self.addWaypoint('moveUp'), **button_args)
        self.moveUpButton.grid(row=7, column=0, padx=5, pady=5, sticky='nsew')
        self.moveDownButton = customtkinter.CTkButton(
            self.actionsFrame, text='Move Down', command=lambda: self.addWaypoint('moveDown'), **button_args)
        self.moveDownButton.grid(
            row=7, column=1, padx=5, pady=5, sticky='nsew')

        self.depositGoldButton = customtkinter.CTkButton(
            self.actionsFrame, text='Deposit gold', command=lambda: self.addWaypoint('depositGold'), **button_args)
        self.depositGoldButton.grid(
            row=8, column=0, padx=5, pady=5, sticky='nsew')
        self.depositItemsButton = customtkinter.CTkButton(
            self.actionsFrame, text='Deposit items', command=lambda: self.addWaypoint('depositItems'), **button_args)
        self.depositItemsButton.grid(
            row=8, column=1, padx=5, pady=5, sticky='nsew')

        self.dropFlasksButton = customtkinter.CTkButton(
            self.actionsFrame, text='Drop flasks', command=lambda: self.addWaypoint('dropFlasks'), **button_args)
        self.dropFlasksButton.grid(
            row=9, column=0, padx=5, pady=5, sticky='nsew')
        
        self.buyBackpackButton = customtkinter.CTkButton(
            self.actionsFrame, text='Buy Backpack', command=lambda: self.openBackpackModal(), **button_args)
        self.buyBackpackButton.grid(
            row=9, column=1, padx=5, pady=5, sticky='nsew')

        self.refillButton = customtkinter.CTkButton(
            self.actionsFrame, text='Refill', command=lambda: self.openRefillModal(), **button_args)
        self.refillButton.grid(
            row=10, column=0, padx=5, pady=5, sticky='nsew')

        self.refillCheckerButton = customtkinter.CTkButton(
            self.actionsFrame, text='Refill checker', command=lambda: self.openRefillCheckerModal(), **button_args)
        self.refillCheckerButton.grid(
            row=10, column=1, padx=5, pady=5, sticky='nsew')
        
        self.travelButton = customtkinter.CTkButton(
            self.actionsFrame, text='Travel', command=lambda: self.addWaypoint('travel'), **button_args)
        self.travelButton.grid(
            row=11, column=0, padx=5, pady=5, sticky='nsew')
        
        self.ignoreCreaturesButton = customtkinter.CTkButton(
            self.actionsFrame, text='Ignorar Criaturas', command=self.ignoreCreaturesWindow, **button_args)
        self.ignoreCreaturesButton.grid(
            row=11, column=1, padx=5, pady=5, sticky='nsew')
        
        self.saveConfigFrame = customtkinter.CTkFrame(self, fg_color=MATRIX_BLACK, border_color=MATRIX_GREEN_BORDER, border_width=1)
        self.saveConfigFrame.grid(column=1, row=2, padx=10,
                            pady=10, sticky='nsew')

        saveConfigButton = customtkinter.CTkButton(self.saveConfigFrame, text="Save Script", command=self.saveScript, **button_args)
        saveConfigButton.grid(row=0, column=0, padx=20, pady=20, sticky='nsew')

        loadConfigButton = customtkinter.CTkButton(self.saveConfigFrame, text="Load Script", command=self.loadScript, **button_args)
        loadConfigButton.grid(row=0, column=1, padx=20, pady=20, sticky='nsew')
        
        self.saveConfigFrame.columnconfigure(0, weight=1, uniform='equal')
        self.saveConfigFrame.columnconfigure(1, weight=1, uniform='equal')

    def openBaseModal(self):
        if self.baseModal is None or not self.baseModal.winfo_exists():
            self.baseModal = BaseModal(self, onConfirm=lambda label, options: self.addWaypoint(
                'refill', options))

    def openRefillModal(self):
        if self.refillModal is None or not self.refillModal.winfo_exists():
            self.refillModal = RefillModal(self, onConfirm=lambda label, options: self.addWaypoint(
                'refill', options))
            
    def openBackpackModal(self):
        if self.backpackModal is None or not self.backpackModal.winfo_exists():
            self.backpackModal = BuyBackpackModal(self, onConfirm=lambda label, options: self.addWaypoint(
                'buyBackpack', options))

    def openRefillCheckerModal(self):
        waypointsLabels = self.context.getAllWaypointLabels()
        if len(waypointsLabels) == 0:
            messagebox.showerror(
                'Erro', 'There must be at least one labeled waypoint!')
        if self.refillCheckerModal is None or not self.refillCheckerModal.winfo_exists():
            self.refillCheckerModal = RefillCheckerModal(self, onConfirm=lambda label, options: self.addWaypoint(
                'refillChecker', options), waypointsLabels=waypointsLabels)

    # TODO: verificar se a coordenada é walkable
    def addWaypoint(self, waypointType, options=None, ignore=False, passinho=False):
        screenshot = getScreenshot()
        coordinate = getCoordinate(screenshot)
        
        if coordinate is None:
            messagebox.showerror('Erro', 'The Tibia minimap needs to be visible!')
            return
        
        waypointDirection = self.waypointDirection.get()
        
        if waypointDirection == 'north':
            coordinate = (coordinate[0], coordinate[1] - 1, coordinate[2])
        elif waypointDirection == 'south':
            coordinate = (coordinate[0], coordinate[1] + 1, coordinate[2])
        elif waypointDirection == 'east':
            coordinate = (coordinate[0] + 1, coordinate[1], coordinate[2])
        elif waypointDirection == 'west':
            coordinate = (coordinate[0] - 1, coordinate[1], coordinate[2])
        
        if options is None:
            options = {}  # Cria um novo dicionário se options for None
        
        waypoint = {'label': '', 'type': waypointType,
                    'coordinate': coordinate, 'options': options.copy(), 'ignore': ignore, 'passinho': passinho}
        
        if waypointType == 'moveUp' or waypointType == 'moveDown' or waypointType == 'singleMove' or waypointType == 'rightClickDirection':
            if waypointDirection == 'center':
                messagebox.showerror('Erro', 'Move Down or Move Up waypoint always needs a direction (North, West, East, South)')
                return
            waypoint['options']['direction'] = waypointDirection
        
        self.context.addWaypoint(waypoint)
        self.table.insert('', 'end', values=(
            waypoint['label'], waypoint['type'], waypoint['coordinate'], waypoint['options']))

    def removeSelectedWaypoints(self):
        selectedWaypoints = self.table.selection()
        for waypoint in selectedWaypoints:
            index = self.table.index(waypoint)
            self.table.delete(waypoint)
            self.context.removeWaypointByIndex(index)

    def onWaypointDoubleClick(self, event):
        item = self.table.identify_row(event.y)
        if item:
            index = self.table.index(item)
            waypoint = self.context.context['ng_cave']['waypoints']['items'][index]
            if waypoint['type'] == 'refill':
                if self.refillModal is None or not self.refillModal.winfo_exists():
                    self.refillModal = RefillModal(
                        self, waypoint=waypoint, onConfirm=lambda label, options: self.updateWaypointByIndex(index, label=label, options=options))
            elif waypoint['type'] == 'buyBackpack':
                if self.backpackModal is None or not self.backpackModal.winfo_exists():
                    self.backpackModal = BuyBackpackModal(
                        self, waypoint=waypoint, onConfirm=lambda label, options: self.updateWaypointByIndex(index, label=label, options=options))
            elif waypoint['type'] == 'depositItems':
                if self.depositItemsModal is None or not self.depositItemsModal.winfo_exists():
                    self.depositItemsModal = DepositItemsModal(
                        self, waypoint=waypoint, onConfirm=lambda label, options: self.updateWaypointByIndex(index, label=label, options=options))
            elif waypoint['type'] == 'travel':
                if self.travelModal is None or not self.travelModal.winfo_exists():
                    self.travelModal = TravelModal(
                        self, waypoint=waypoint, onConfirm=lambda label, options: self.updateWaypointByIndex(index, label=label, options=options))
            elif waypoint['type'] == 'refillChecker':
                if self.refillCheckerModal is None or not self.refillCheckerModal.winfo_exists():
                    waypointsLabels = self.context.getAllWaypointLabels()
                    self.refillCheckerModal = RefillCheckerModal(
                        self, waypoint=waypoint, onConfirm=lambda label, options: self.updateWaypointByIndex(index, label=label, options=options), waypointsLabels=waypointsLabels)
            else:
                if self.baseModal is None or not self.baseModal.winfo_exists():
                    self.baseModal = BaseModal(
                        self, waypoint=waypoint, onConfirm=lambda label, options: self.updateWaypointByIndex(index, label=label, options=options))

    def updateWaypointByIndex(self, index, label=None, options={}):
        self.context.updateWaypointByIndex(index, label=label, options=options)
        selecionado = self.table.focus()
        if selecionado:
            currentValues = self.table.item(selecionado)['values']
            if label is not None:
                currentValues[0] = label
            currentValues[3] = options
            self.table.item(selecionado, values=currentValues)
            self.table.update()

    def onToggleEnabledButton(self):
        enabled = self.enabledVar.get()
        self.context.toggleCavebot(enabled)

    def onToggleRunButton(self):
        enabled = self.runToCreaturesVar.get()
        self.context.toggleRunToCreatures(enabled)

    def ignoreCreaturesWindow(self):
        if self.ignoreCreaturesPage is None or not self.ignoreCreaturesPage.winfo_exists():
            self.ignoreCreaturesPage = IgnoreCreaturesPage(self.context)
        else:
            self.ignoreCreaturesPage.focus()

    def saveScript(self):
        file = filedialog.asksaveasfilename(
            defaultextension=".skbscript",
            filetypes=[("SKB Script", "*.skbscript"), ("Todos os arquivos", "*.*")]
        )

        if file:
            with open(file, 'w') as f:
                json.dump(self.context.context['ng_cave']['waypoints']['items'], f, indent=4)
            messagebox.showinfo('Sucesso', 'Script salvo com sucesso!')

    def loadScript(self):
        file = filedialog.askopenfilename(
            defaultextension=".skbscript",
            filetypes=[("SKB Script", "*.skbscript"), ("Todos os arquivos", "*.*")]
        )

        if file:
            with open(file, 'r') as f:
                self.table.delete()
                script = json.load(f)
                self.context.loadScript(script)
                for waypoint in script:
                    self.table.insert('', 'end', values=(
                        waypoint['label'], waypoint['type'], waypoint['coordinate'], waypoint['options']))
            messagebox.showinfo('Sucesso', 'Script carregado com sucesso!')