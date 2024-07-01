from .highPriorityTab import HighPriorityTab
from .potionsTab import PotionsTab
from .spellsTab import SpellsTab
from .foodTab import FoodTab
import customtkinter
from ...utils import genRanStr

class HealingPage(customtkinter.CTkToplevel):
    def __init__(self, context):
        super().__init__()
        self.context = context

        self.title(genRanStr())
        self.resizable(False, False)

        self.tabControl = customtkinter.CTkTabview(self, segmented_button_selected_color='#C20034',
                                                segmented_button_selected_hover_color='#870125',
                                                segmented_button_unselected_hover_color='#870125')

        self.tabControl.add('High Priority')
        self.tabControl.add('Potions')
        self.tabControl.add('Spells')
        self.tabControl.add('Food')
        self.tabControl.pack(expand=1, fill='both')

        self.highPriorityTab = HighPriorityTab(self.tabControl.tab("High Priority"), self.context)
        self.highPriorityTab.pack()
        self.potionsTab = PotionsTab(self.tabControl.tab("Potions"), self.context)
        self.potionsTab.pack()
        self.spellsTab = SpellsTab(self.tabControl.tab("Spells"), self.context)
        self.spellsTab.pack()
        self.foodTab = FoodTab(self.tabControl.tab("Food"), self.context)
        self.foodTab.pack()
