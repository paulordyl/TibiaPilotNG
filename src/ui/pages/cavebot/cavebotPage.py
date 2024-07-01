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

class CavebotPage(customtkinter.CTkToplevel):
    def __init__(self, context):
        super().__init__()
        self.context = context

        self.title(genRanStr())
        self.resizable(False, False)

        self.ignoreCreaturesPage = None

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

        self.columnconfigure(0, weight=8)
        self.columnconfigure(1, weight=2)
        self.rowconfigure(1, weight=1)
        self.baseModal = None
        self.refillModal = None
        self.backpackModal = None
        self.refillCheckerModal = None
        self.depositItemsModal = None
        self.travelModal = None

        self.tableFrame = customtkinter.CTkFrame(self)
        self.tableFrame.grid(row=0, column=0, rowspan=2, padx=10, pady=10, sticky="nsew")
        self.tableFrame.rowconfigure(0, weight=1)
        self.tableFrame.columnconfigure(0, weight=1)

        self.table = ttk.Treeview(self.tableFrame, columns=(
            'label', 'type', 'coordinate', 'options'))
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
            
        self.directionsFrame = customtkinter.CTkFrame(self)
        self.directionsFrame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        self.directionsFrame.columnconfigure(0, weight=1)
        self.directionsFrame.columnconfigure(1, weight=1)
        self.directionsFrame.columnconfigure(2, weight=1)

        self.waypointDirection = StringVar(value='center')

        northOption = customtkinter.CTkRadioButton(self.directionsFrame, variable=self.waypointDirection,
                                    text='North', value='north', fg_color="#C20034", hover_color="#870125")
        northOption.grid(row=0, column=1)

        westOption = customtkinter.CTkRadioButton(self.directionsFrame, variable=self.waypointDirection,
                                    text='West', value='west', fg_color="#C20034", hover_color="#870125")
        westOption.grid(row=1, column=0)

        centerOption = customtkinter.CTkRadioButton(self.directionsFrame, variable=self.waypointDirection,
                                    text='Center', value='center', fg_color="#C20034", hover_color="#870125")
        centerOption.grid(row=1, column=1, pady=10)

        eastOption = customtkinter.CTkRadioButton(self.directionsFrame, variable=self.waypointDirection,
                                    text='East', value='east', fg_color="#C20034", hover_color="#870125")
        eastOption.grid(row=1, column=2)

        southOption = customtkinter.CTkRadioButton(self.directionsFrame, variable=self.waypointDirection,
                                    text='South', value='south', fg_color="#C20034", hover_color="#870125")
        southOption.grid(row=2, column=1)

        self.actionsFrame = customtkinter.CTkFrame(self)
        self.actionsFrame.grid(row=1, column=1, padx=10, pady=10, sticky="nsew")
        self.actionsFrame.columnconfigure(0, weight=1, uniform='equal')
        self.actionsFrame.columnconfigure(1, weight=1, uniform='equal')

        self.enabledVar = BooleanVar()
        self.enabledVar.set(self.context.context['ng_cave']['enabled'])
        self.checkbutton = customtkinter.CTkCheckBox(
            self.actionsFrame, text='Enabled', variable=self.enabledVar, command=self.onToggleEnabledButton,
            hover_color="#870125", fg_color='#C20034')
        self.checkbutton.grid(column=0, row=0, padx=5, pady=5, sticky='w')

        self.runToCreaturesVar = BooleanVar()
        self.runToCreaturesVar.set(self.context.context['ng_cave']['runToCreatures'])
        self.runToCreaturesButton = customtkinter.CTkCheckBox(
            self.actionsFrame, text='Run to creatures', variable=self.runToCreaturesVar, command=self.onToggleRunButton,
            hover_color="#870125", fg_color='#C20034')
        self.runToCreaturesButton.grid(column=1, row=0, padx=5, pady=5, sticky='w')

        self.deleteWaypoints = customtkinter.CTkButton(
            self.actionsFrame, text='Delete Waypoints', command=lambda: self.removeSelectedWaypoints(),
            corner_radius=32, fg_color="transparent", border_color="#C20034",
            border_width=2, hover_color="#C20034")
        self.deleteWaypoints.grid(row=1, column=0, padx=5, pady=5, sticky='nsew')
        self.depositItemsHouseButton = customtkinter.CTkButton(
            self.actionsFrame, text='Deposit House', command=lambda: self.addWaypoint('depositItemsHouse'),
            corner_radius=32, fg_color="transparent", border_color="#C20034",
            border_width=2, hover_color="#C20034")
        self.depositItemsHouseButton.grid(
            row=1, column=1, padx=5, pady=5, sticky='nsew')

        self.walkButton = customtkinter.CTkButton(
            self.actionsFrame, text='Walk', command=lambda: self.addWaypoint('walk'),
            corner_radius=32, fg_color="transparent", border_color="#C20034",
            border_width=2, hover_color="#C20034")
        self.walkButton.grid(row=2, column=0, padx=5, pady=5, sticky='nsew')

        self.rightClickDirectionButton = customtkinter.CTkButton(
            self.actionsFrame, text='RC Direction', command=lambda: self.addWaypoint('rightClickDirection'),
            corner_radius=32, fg_color="transparent", border_color="#C20034",
            border_width=2, hover_color="#C20034")
        self.rightClickDirectionButton.grid(row=2, column=1, padx=5, pady=5, sticky='nsew')

        self.walkButton = customtkinter.CTkButton(
            self.actionsFrame, text='Walk Ignore', command=lambda: self.addWaypoint('walk', ignore=True),
            corner_radius=32, fg_color="transparent", border_color="#C20034",
            border_width=2, hover_color="#C20034")
        self.walkButton.grid(row=3, column=0, padx=5, pady=5, sticky='nsew')

        self.walkButton = customtkinter.CTkButton(
            self.actionsFrame, text='Walk Ignore Passinho', command=lambda: self.addWaypoint('walk', ignore=True, passinho=True),
            corner_radius=32, fg_color="transparent", border_color="#C20034",
            border_width=2, hover_color="#C20034")
        self.walkButton.grid(row=3, column=1, padx=5, pady=5, sticky='nsew')

        self.ropeButton = customtkinter.CTkButton(
            self.actionsFrame, text='Rope', command=lambda: self.addWaypoint('useRope'),
            corner_radius=32, fg_color="transparent", border_color="#C20034",
            border_width=2, hover_color="#C20034")
        self.ropeButton.grid(row=4, column=0, padx=5, pady=5, sticky='nsew')

        self.shovelButton = customtkinter.CTkButton(
            self.actionsFrame, text='Shovel', command=lambda: self.addWaypoint('useShovel'),
            corner_radius=32, fg_color="transparent", border_color="#C20034",
            border_width=2, hover_color="#C20034")
        self.shovelButton.grid(row=4, column=1, padx=5, pady=5, sticky='nsew')

        self.rightClickUseButton = customtkinter.CTkButton(
            self.actionsFrame, text='Use Right Click', command=lambda: self.addWaypoint('rightClickUse'),
            corner_radius=32, fg_color="transparent", border_color="#C20034",
            border_width=2, hover_color="#C20034")
        self.rightClickUseButton.grid(row=5, column=0, padx=5, pady=5, sticky='nsew')

        self.openDoorButton = customtkinter.CTkButton(
            self.actionsFrame, text='Open Door', command=lambda: self.addWaypoint('openDoor'),
            corner_radius=32, fg_color="transparent", border_color="#C20034",
            border_width=2, hover_color="#C20034")
        self.openDoorButton.grid(row=5, column=1, padx=5, pady=5, sticky='nsew')

        self.singleMoveButton = customtkinter.CTkButton(
            self.actionsFrame, text='Single Move', command=lambda: self.addWaypoint('singleMove'),
            corner_radius=32, fg_color="transparent", border_color="#C20034",
            border_width=2, hover_color="#C20034")
        self.singleMoveButton.grid(row=6, column=0, padx=5, pady=5, sticky='nsew')

        self.useLadderButton = customtkinter.CTkButton(
            self.actionsFrame, text='Use Ladder', command=lambda: self.addWaypoint('useLadder'),
            corner_radius=32, fg_color="transparent", border_color="#C20034",
            border_width=2, hover_color="#C20034")
        self.useLadderButton.grid(row=6, column=1, padx=5, pady=5, sticky='nsew')

        self.moveUpButton = customtkinter.CTkButton(
            self.actionsFrame, text='Move Up', command=lambda: self.addWaypoint('moveUp'),
            corner_radius=32, fg_color="transparent", border_color="#C20034",
            border_width=2, hover_color="#C20034")
        self.moveUpButton.grid(row=7, column=0, padx=5, pady=5, sticky='nsew')
        self.moveDownButton = customtkinter.CTkButton(
            self.actionsFrame, text='Move Down', command=lambda: self.addWaypoint('moveDown'),
            corner_radius=32, fg_color="transparent", border_color="#C20034",
            border_width=2, hover_color="#C20034")
        self.moveDownButton.grid(
            row=7, column=1, padx=5, pady=5, sticky='nsew')

        self.depositGoldButton = customtkinter.CTkButton(
            self.actionsFrame, text='Deposit gold', command=lambda: self.addWaypoint('depositGold'),
            corner_radius=32, fg_color="transparent", border_color="#C20034",
            border_width=2, hover_color="#C20034")
        self.depositGoldButton.grid(
            row=8, column=0, padx=5, pady=5, sticky='nsew')
        self.depositItemsButton = customtkinter.CTkButton(
            self.actionsFrame, text='Deposit items', command=lambda: self.addWaypoint('depositItems'),
            corner_radius=32, fg_color="transparent", border_color="#C20034",
            border_width=2, hover_color="#C20034")
        self.depositItemsButton.grid(
            row=8, column=1, padx=5, pady=5, sticky='nsew')

        self.dropFlasksButton = customtkinter.CTkButton(
            self.actionsFrame, text='Drop flasks', command=lambda: self.addWaypoint('dropFlasks'),
            corner_radius=32, fg_color="transparent", border_color="#C20034",
            border_width=2, hover_color="#C20034")
        self.dropFlasksButton.grid(
            row=9, column=0, padx=5, pady=5, sticky='nsew')
        
        self.buyBackpackButton = customtkinter.CTkButton(
            self.actionsFrame, text='Buy Backpack', command=lambda: self.openBackpackModal(),
            corner_radius=32, fg_color="transparent", border_color="#C20034",
            border_width=2, hover_color="#C20034")
        self.buyBackpackButton.grid(
            row=9, column=1, padx=5, pady=5, sticky='nsew')

        self.refillButton = customtkinter.CTkButton(
            self.actionsFrame, text='Refill', command=lambda: self.openRefillModal(),
            corner_radius=32, fg_color="transparent", border_color="#C20034",
            border_width=2, hover_color="#C20034")
        self.refillButton.grid(
            row=10, column=0, padx=5, pady=5, sticky='nsew')

        self.refillCheckerButton = customtkinter.CTkButton(
            self.actionsFrame, text='Refill checker', command=lambda: self.openRefillCheckerModal(),
            corner_radius=32, fg_color="transparent", border_color="#C20034",
            border_width=2, hover_color="#C20034")
        self.refillCheckerButton.grid(
            row=10, column=1, padx=5, pady=5, sticky='nsew')
        
        self.travelButton = customtkinter.CTkButton(
            self.actionsFrame, text='Travel', command=lambda: self.addWaypoint('travel'),
            corner_radius=32, fg_color="transparent", border_color="#C20034",
            border_width=2, hover_color="#C20034")
        self.travelButton.grid(
            row=11, column=0, padx=5, pady=5, sticky='nsew')
        
        self.ignoreCreaturesButton = customtkinter.CTkButton(
            self.actionsFrame, text='Ignorar Criaturas', command=self.ignoreCreaturesWindow,
            corner_radius=32, fg_color="transparent", border_color="#C20034",
            border_width=2, hover_color="#C20034")
        self.ignoreCreaturesButton.grid(
            row=11, column=1, padx=5, pady=5, sticky='nsew')
        
        self.saveConfigFrame = customtkinter.CTkFrame(self)
        self.saveConfigFrame.grid(column=1, row=2, padx=10,
                            pady=10, sticky='nsew')

        saveConfigButton = customtkinter.CTkButton(self.saveConfigFrame, text="Save Script", corner_radius=32,
                                        fg_color="transparent", border_color="#C20034",
                                        border_width=2, hover_color="#C20034", command=self.saveScript)
        saveConfigButton.grid(row=0, column=0, padx=20, pady=20, sticky='nsew')

        loadConfigButton = customtkinter.CTkButton(self.saveConfigFrame, text="Load Script", corner_radius=32,
                                        fg_color="transparent", border_color="#C20034",
                                        border_width=2, hover_color="#C20034", command=self.loadScript)
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
            defaultextension=".pilotscript",
            filetypes=[("PilotNG Script", "*.pilotscript"), ("Todos os arquivos", "*.*")]
        )

        if file:
            with open(file, 'w') as f:
                json.dump(self.context.context['ng_cave']['waypoints']['items'], f, indent=4)
            messagebox.showinfo('Sucesso', 'Script salvo com sucesso!')

    def loadScript(self):
        file = filedialog.askopenfilename(
            defaultextension=".pilotscript",
            filetypes=[("PilotNG Script", "*.pilotscript"), ("Todos os arquivos", "*.*")]
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