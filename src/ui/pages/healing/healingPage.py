from .highPriorityTab import HighPriorityTab
from .potionsTab import PotionsTab
from .spellsTab import SpellsTab
from .foodTab import FoodTab
import customtkinter
from ...utils import genRanStr
from ...theme import MATRIX_BLACK, MATRIX_GREEN, MATRIX_GREEN_HOVER, MATRIX_GREEN_BORDER

class HealingPage(customtkinter.CTkToplevel):
    def __init__(self, context):
        super().__init__()
        self.configure(fg_color=MATRIX_BLACK)
        self.context = context

        self.title(genRanStr())
        self.resizable(False, False)

        self.tabControl = customtkinter.CTkTabview(self,
                                                text_color=MATRIX_GREEN,
                                                segmented_button_fg_color=MATRIX_BLACK,
                                                segmented_button_selected_color=MATRIX_GREEN_BORDER,
                                                segmented_button_selected_hover_color=MATRIX_GREEN_HOVER,
                                                segmented_button_unselected_color=MATRIX_BLACK,
                                                segmented_button_unselected_hover_color=MATRIX_GREEN_BORDER)
        
        # Ensure the content of the tabs also has a black background
        # This is often handled by the tab content itself, but explicitly setting for the frame within the tab
        # is a good fallback if the content isn't a frame that gets styled.
        # However, Customtkinter's CTkTabview creates frames for tab contents.
        # We will style those frames within their respective classes (e.g. HighPriorityTab)

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
