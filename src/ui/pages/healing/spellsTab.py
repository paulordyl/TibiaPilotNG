from .spellCard import SpellCard
from .uturaCard import UturaCard
from .uturaGranCard import UturaGranCard
import customtkinter
from ...theme import MATRIX_BLACK # Only MATRIX_BLACK is needed here as cards handle their own styling


class SpellsTab(customtkinter.CTkFrame):
    def __init__(self, parent, context):
        super().__init__(parent, fg_color=MATRIX_BLACK)
        self.configure(fg_color=MATRIX_BLACK) # Ensure the main frame bg is black
        self.context = context
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self.rowconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

        self.criticalHealingCard = SpellCard(
            self, context, 'criticalHealing', title='Critical healing')
        self.criticalHealingCard.grid(column=0, row=0, padx=10,
                                    pady=10, sticky='nsew')

        self.lightHealingCard = SpellCard(
            self, context, 'lightHealing', title='Light healing')
        self.lightHealingCard.grid(column=1, row=0, padx=10,
                                pady=10, sticky='nsew')

        self.uturaCard = UturaCard(self, context)
        self.uturaCard.grid(column=0, row=1, padx=10,
                            pady=10, sticky='nsew')

        self.uturaGranCard = UturaGranCard(
            self, context)
        self.uturaGranCard.grid(column=1, row=1, padx=10,
                                pady=10, sticky='nsew')
