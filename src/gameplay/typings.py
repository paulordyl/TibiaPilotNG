from typing import Any, List, Dict, Optional, TypedDict

# Forward declare SpellAction if it's used by SpellSequence internally,
# or ensure SpellAction is defined before SpellSequence if they are in the same file.
# For this case, SpellAction is defined in .spells where SpellSequence is also defined.
from .spells import SpellSequence

# The main application context is a large dictionary.
# While not fully typed here, specific complex substructures can be.
# For now, Context remains Any, but we make SpellSequence available for type hinting.
Context = Any

# Example of how one might start typing parts of the context if desired:
# class NgCaveWaypoints(TypedDict):
#     currentIndex: Optional[int]
#     items: List[Dict] # This would be List[Waypoint] if Waypoint type is defined
#     state: Optional[str]

# class NgCaveContext(TypedDict):
#     enabled: bool
#     runToCreatures: bool
#     holesOrStairs: List[Any] # Define more specifically if possible
#     isAttackingSomeCreature: bool
#     previousTargetCreature: Optional[Any] # Define Creature type
#     targetCreature: Optional[Any] # Define Creature type
#     waypoints: NgCaveWaypoints
#     # If spell_sequences were specific to cave context:
#     # spell_sequences: Dict[str, SpellSequence]

# class MainContext(TypedDict):
#     # ... other top-level keys ...
#     ng_cave: NgCaveContext
#     ng_spellSequences: Dict[str, SpellSequence] # If adding at top level of main context
#     # ... more keys ...

# This file primarily makes shared type definitions available.
# The actual main context structure is in gameplay/context.py
# and can be gradually typed here if the project moves towards stricter typing.
# For now, the subtask was to add SpellSequence to the context,
# which has been done by adding the key in context.py and making the type available here.

__all__ = [
    'Context',
    'SpellSequence',
    # Add other important shared gameplay types here if they get defined
]
