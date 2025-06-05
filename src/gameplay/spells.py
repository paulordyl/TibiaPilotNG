from typing import List, Dict, Optional, TypedDict

# TypedDict Definitions

class SpellAction(TypedDict):
    """
    Represents a single spell action to be executed, often as part of a sequence.
    """
    name: str  # Name of the spell, should match a key in KNOWN_SPELLS
    words: str # Actual spell words to say/use
    target_type: str  # e.g., "self", "current_target", "player_name", "creature_name", "none"
    target_value: Optional[str]  # Value for target_type if needed (e.g., player's name)
    delay_ms: int  # Delay in milliseconds after performing this action
    mana_cost: Optional[int] # Mana cost for this specific action, could override default

class SpellDefinition(TypedDict):
    """
    Defines a known spell in the game, its properties, and default values.
    """
    name: str
    words: str
    effect: str
    spell_type: str  # e.g., "Instant", "Rune"
    group_spell: str  # e.g., "Support", "Attack", "Healing"
    group_secondary: Optional[str] # e.g., "Paralyze", "Poison"
    group_rune: Optional[str] # If it's a rune, its specific name e.g., "Sudden Death"
    element: Optional[str] # e.g., "Fire", "Ice", "Energy", "Earth", "Holy", "Death", "Physical"
    mana_cost: Optional[int] # Default mana cost

class SpellSequence(TypedDict):
    """
    Describes a defined sequence of spell actions, typically loaded from a script.
    """
    label: str  # Unique label for this sequence
    spells: List[SpellAction] # The list of spell actions in this sequence

# Initialize KNOWN_SPELLS with a representative subset
KNOWN_SPELLS: Dict[str, SpellDefinition] = {
    "Light Healing": {
        "name": "Light Healing", "words": "exura",
        "effect": "Restores a small amount of health.",
        "spell_type": "Instant", "group_spell": "Healing",
        "group_secondary": None, "group_rune": None,
        "element": "Holy", "mana_cost": 20 # Placeholder
    },
    "Antidote": {
        "name": "Antidote", "words": "exana pox",
        "effect": "Cures poison.",
        "spell_type": "Instant", "group_spell": "Healing",
        "group_secondary": "Poison", "group_rune": None,
        "element": None, "mana_cost": 30 # Placeholder
    },
    "Intense Healing": {
        "name": "Intense Healing", "words": "exura gran",
        "effect": "Restores a moderate amount of health.",
        "spell_type": "Instant", "group_spell": "Healing",
        "group_secondary": None, "group_rune": None,
        "element": "Holy", "mana_cost": 70 # Placeholder
    },
    "Ultimate Healing": {
        "name": "Ultimate Healing", "words": "exura vita",
        "effect": "Restores a large amount of health.",
        "spell_type": "Instant", "group_spell": "Healing",
        "group_secondary": None, "group_rune": None,
        "element": "Holy", "mana_cost": 160 # Placeholder
    },
    "Magic Rope": {
        "name": "Magic Rope", "words": "exani tera",
        "effect": "Teleports the caster up one floor if standing on a rope spot.",
        "spell_type": "Instant", "group_spell": "Support",
        "group_secondary": "Teleportation", "group_rune": None,
        "element": None, "mana_cost": 20 # Placeholder
    },
    "Sudden Death": { # Example of a Rune
        "name": "Sudden Death", "words": "adori gran mort",
        "effect": "Deals massive Death damage to a single target.",
        "spell_type": "Rune", "group_spell": "Attack",
        "group_secondary": None, "group_rune": "Sudden Death",
        "element": "Death", "mana_cost": 0 # Placeholder (runes don't cost mana directly)
    },
    "Energy Beam": {
        "name": "Energy Beam", "words": "exevo vis lux",
        "effect": "Deals Energy damage in a beam.",
        "spell_type": "Instant", "group_spell": "Attack",
        "group_secondary": "Beam", "group_rune": None,
        "element": "Energy", "mana_cost": 80 # Placeholder
    },
    "Great Energy Beam": {
        "name": "Great Energy Beam", "words": "exevo gran vis lux",
        "effect": "Deals more Energy damage in a wider beam.",
        "spell_type": "Instant", "group_spell": "Attack",
        "group_secondary": "Beam", "group_rune": None,
        "element": "Energy", "mana_cost": 200 # Placeholder
    },
    "Haste": {
        "name": "Haste", "words": "utani hur",
        "effect": "Increases movement speed.",
        "spell_type": "Instant", "group_spell": "Support",
        "group_secondary": "Movement", "group_rune": None,
        "element": None, "mana_cost": 60 # Placeholder
    },
    "Strong Haste": {
        "name": "Strong Haste", "words": "utani gran hur",
        "effect": "Greatly increases movement speed.",
        "spell_type": "Instant", "group_spell": "Support",
        "group_secondary": "Movement", "group_rune": None,
        "element": None, "mana_cost": 100 # Placeholder
    }
}

# TODO: Add more spells from the provided list
# TODO: Verify mana costs and other properties from a reliable game data source
