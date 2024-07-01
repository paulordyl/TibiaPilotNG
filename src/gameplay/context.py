from src.gameplay.core.tasks.orchestrator import TasksOrchestrator


context = {
    'ng_backpacks': {
        'main': '',
        'loot': '',
    },
    'ng_battleList': {
        'beingAttackedCreatureCategory': None,
        'creatures': [],
    },
    'ng_cave': {
        'enabled': True,
        'runToCreatures': False,
        'holesOrStairs': [],
        'isAttackingSomeCreature': False,
        'previousTargetCreature': None,
        'targetCreature': None,
        'waypoints': {
            'currentIndex': None,
            'items': [],
            'state': None
        },
    },
    'ng_chat': {
        'tabs': {}
    },
    'ng_comingFromDirection': None,
    'ng_comboSpells': {
        'enabled': True,
        'lastUsedSpell': None,
        'lastUsedSpellAt': None,
        'items': [],
    },
    'ng_deposit': {
        'lockerCoordinate': None
    },
    'gameWindow': {
        'coordinate': None,
        'image': None,
        'previousGameWindowImage': None,
        'previousMonsters': [],
        'monsters': [],
        'players': [],
        'walkedPixelsInSqm': 0,
    },
    'healing': {
        'highPriority': {
            'healthFood': {
                'enabled': False,
                'hotkey': None,
                'hpPercentageLessThanOrEqual': None,
            },
            'manaFood': {
                'enabled': False,
                'hotkey': None,
                'manaPercentageLessThanOrEqual': None,
            },
            'swapRing': {
                'enabled': False,
                'tankRing': {
                    'hotkey': None,
                    'hpPercentageLessThanOrEqual': 0
                },
                'mainRing': {
                    'hotkey': None,
                    'hpPercentageGreaterThanOrEqual': 0
                },
                'tankRingAlwaysEquipped': False
            },
            'swapAmulet': {
                'enabled': False,
                'tankAmulet': {
                    'hotkey': None,
                    'hpPercentageLessThanOrEqual': 0
                },
                'mainAmulet': {
                    'hotkey': None,
                    'hpPercentageGreaterThan': 0
                },
                'tankAmuletAlwaysEquipped': False
            }
        },
        'potions': {
            'firstHealthPotion': {
                'enabled': False,
                'hotkey': None,
                'slot': None,
                'hpPercentageLessThanOrEqual': None,
                'manaPercentageGreaterThanOrEqual': None,
            },
            'firstManaPotion': {
                'enabled': False,
                'hotkey': None,
                'slot': None,
                'manaPercentageLessThanOrEqual': None,
            },
        },
        'spells': {
            'criticalHealing': {
                'enabled': False,
                'hotkey': None,
                'hpPercentageLessThanOrEqual': None,
                'spell': None
            },
            'lightHealing': {
                'enabled': False,
                'hotkey': None,
                'hpPercentageLessThanOrEqual': None,
                'spell': None
            },
            'utura': {
                'enabled': False,
                'hotkey': None,
                'spell': {
                    'name': 'utura',
                    'manaNeeded': '75'
                }
            },
            'uturaGran': {
                'enabled': False,
                'hotkey': None,
                'spell': {
                    'name': 'utura gran',
                    'manaNeeded': '165'
                }
            },
        },
        'eatFood': {
            'enabled': False,
            'hotkey': 'f',
            'eatWhenFoodIslessOrEqual': 0,
        }
    },
    'loot': {
        'corpsesToLoot': [],
    },
    'ng_lastPressedKey': None,
    'ng_pause': True,
    'ng_radar': {
        'coordinate': None,
        'previousCoordinate': None,
        'lastCoordinateVisited': None,
    },
    'ng_resolution': 1080,
    'ng_statusBar': {
        'hpPercentage': None,
        'hp': None,
        'manaPercentage': None,
        'mana': None,
    },
    'ng_targeting': {
        'enabled': False,
        'creatures': {},
        'canIgnoreCreatures': True,
        'hasIgnorableCreatures': False,
    },
    'general_hotkeys': {
        'shovel_hotkey': 'p',
        'rope_hotkey': 'o',
    },
    'auto_hur': {
        'enabled': False,
        'hotkey': 't',
        'spell': 'utani hur',
        'pz': False
    },
    'statsBar': {
        'pz': None,
        'hur': None,
        'poison': None,
    },
    'alert': {
        'enabled': False,
        'cave': False,
        'sayPlayer': False
    },
    'clear_stats': {
        'poison': False,
        'poison_hotkey': 'g'
    },
    'ignorable_creatures': [],
    'ng_tasksOrchestrator': TasksOrchestrator(),
    'ng_screenshot': None,
    'way': None,
    'window': None,
    'ng_lastLootIndex': None,
    'ng_lastUsedSpellLoot': None,
    'healCount': 0
}
