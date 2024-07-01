from os.path import exists
import time
from tinydb import Query, TinyDB
from tkinter import messagebox
from src.gameplay.core.load import loadContextFromConfig, loadNgCfgs
from src.repositories.chat.core import resetOldList
# from src.utils.core import getScreenshot


class Context:
    filePath: str = 'file.json'

    def __init__(self, context):
        shouldInsertProfile = not exists(self.filePath)
        self.db = TinyDB(self.filePath)
        if shouldInsertProfile:
            self.insertProfile()
        self.enabledProfile = self.getEnabledProfile()
        self.context = loadContextFromConfig(
            self.enabledProfile['config'], context)

    def updateMainBackpack(self, backpack: str):
        self.context['ng_backpacks']['main'] = backpack
        self.enabledProfile['config']['ng_backpacks']['main'] = backpack
        self.db.update(self.enabledProfile)

    def insertProfile(self):
        self.db.insert({
            'enabled': True,
            'config': {
                'ng_backpacks': {
                    'main': None,
                    'loot': None
                },
                'ng_cave': {
                    'enabled': False,
                    'runToCreatures': False,
                    'waypoints': {
                        'items': []
                    }
                },
                'ng_comboSpells': {
                    'enabled': False,
                    'items': []
                },
                'general_hotkeys': {
                    'shovel_hotkey': 'p',
                    'rope_hotkey': 'o'
                },
                'auto_hur': {
                    'enabled': False,
                    'hotkey': 't',
                    'spell': 'utani hur',
                    'pz': False
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
                'healing': {
                    'highPriority': {
                        'healthFood': {
                            'enabled': False,
                            'hotkey': '3',
                            'hpPercentageLessThanOrEqual': 0,
                        },
                        'manaFood': {
                            'enabled': False,
                            'hotkey': '4',
                            'manaPercentageLessThanOrEqual': 0,
                        },
                        'swapRing': {
                            'enabled': False,
                            'tankRing': {
                                'hotkey': 'f11',
                                'hpPercentageLessThanOrEqual': 0,
                                'slot': 21
                            },
                            'mainRing': {
                                'hotkey': 'f12',
                                'hpPercentageGreaterThan': 0,
                                'slot': 22
                            },
                            'tankRingAlwaysEquipped': False
                        },
                        'swapAmulet': {
                            'enabled': False,
                            'tankAmulet': {
                                'hotkey': 'u',
                                'hpPercentageLessThanOrEqual': 0,
                                'slot': 23
                            },
                            'mainAmulet': {
                                'hotkey': 'i',
                                'hpPercentageGreaterThan': 0,
                                'slot': 24
                            },
                            'tankAmuletAlwaysEquipped': False
                        }
                    },
                    'potions': {
                        'firstHealthPotion': {
                            'enabled': False,
                            'hotkey': '1',
                            'slot': 1,
                            'hpPercentageLessThanOrEqual': 0,
                            'manaPercentageGreaterThanOrEqual': 0,
                        },
                        'firstManaPotion': {
                            'enabled': False,
                            'hotkey': '2',
                            'slot': 2,
                            'manaPercentageLessThanOrEqual': 0,
                        },
                    },
                    'spells': {
                        'criticalHealing': {
                            'enabled': False,
                            'hotkey': '5',
                            'hpPercentageLessThanOrEqual': 0,
                            'manaPercentageGreaterThanOrEqual': 0,
                            'spell': None
                        },
                        'lightHealing': {
                            'enabled': False,
                            'hotkey': '7',
                            'hpPercentageLessThanOrEqual': 0,
                            'manaPercentageGreaterThanOrEqual': 0,
                            'spell': None
                        },
                        'utura': {
                            'enabled': False,
                            'hotkey': '8',
                            'hpPercentageLessThanOrEqual': 0,
                            'manaPercentageGreaterThanOrEqual': 0,
                            'spell': None
                        },
                        'uturaGran': {
                            'enabled': False,
                            'hotkey': '9',
                            'hpPercentageLessThanOrEqual': 0,
                            'manaPercentageGreaterThanOrEqual': 0,
                            'spell': None
                        },
                    },
                    'eatFood': {
                        'enabled': False,
                        'hotkey': 'f',
                        'eatWhenFoodIslessOrEqual': 0,
                    }
                },
            }
        })

    def loadScript(self, script):
        self.context['ng_cave']['waypoints']['items'] = script.copy()
        self.enabledProfile['config']['ng_cave']['waypoints']['items'] = script.copy()
        self.db.update(self.enabledProfile)

    def loadCfg(self, cfg):
        self.context = loadNgCfgs(cfg, self.context)
        self.enabledProfile['config']['ng_backpacks'] = self.context['ng_backpacks']
        self.enabledProfile['config']['general_hotkeys'] = self.context['general_hotkeys']
        self.enabledProfile['config']['auto_hur'] = self.context['auto_hur']
        self.enabledProfile['config']['alert'] = self.context['alert']
        self.enabledProfile['config']['clear_stats'] = self.context['clear_stats']
        self.enabledProfile['config']['ng_comboSpells']['enabled'] = self.context['ng_comboSpells']['enabled']
        for comboSpellsItem in self.context['ng_comboSpells']['items']:
            comboSpellsItem['currentSpellIndex'] = 0
            self.enabledProfile['config']['ng_comboSpells']['items'].append(comboSpellsItem)
        self.enabledProfile['config']['healing'] = self.context['healing']
        self.db.update(self.enabledProfile)

    def getEnabledProfile(self):
        return self.db.search(Query().enabled == True)[0]

    def updateLootBackpack(self, backpack: str):
        self.context['ng_backpacks']['loot'] = backpack
        self.enabledProfile['config']['ng_backpacks']['loot'] = backpack
        self.db.update(self.enabledProfile)

    def addWaypoint(self, waypoint):
        self.context['ng_cave']['waypoints']['items'].append(waypoint)
        self.enabledProfile['config']['ng_cave']['waypoints']['items'].append(
            waypoint)
        self.db.update(self.enabledProfile)

    def addCombo(self, combo):
        self.context['ng_comboSpells']['items'].append(combo)
        self.enabledProfile['config']['ng_comboSpells']['items'].append(
            combo)
        self.db.update(self.enabledProfile)

    def addIgnorableCreature(self, creature):
        self.context['ignorable_creatures'].append(creature)
        self.enabledProfile['config']['ignorable_creatures'].append(creature)
        self.db.update(self.enabledProfile)

    def addSpellByIndex(self, index, spell):
        self.context['ng_comboSpells']['items'][index]['spells'].append(spell)
        # self.enabledProfile['config']['ng_comboSpells']['items'][index]['spells'].append(
        #     spell)
        self.db.update(self.enabledProfile)

    def getAllWaypointLabels(self):
        waypointsLabels = [waypointItem['label'] for waypointItem in self.context['ng_cave']
                        ['waypoints']['items'] if waypointItem['label'] != '']
        return waypointsLabels

    def hasWaypointWithLabel(self, label: str, ignoreLabel=None) -> bool:
        for waypoint in self.context['ng_cave']['waypoints']['points']:
            if waypoint['label'] == label and ignoreLabel is not None:
                return True
        return False

    def updateWaypointByIndex(self, waypointIndex, label=None, options={}):
        if label is not None:
            self.context['ng_cave']['waypoints']['items'][waypointIndex]['label'] = label
            self.enabledProfile['config']['ng_cave']['waypoints']['items'][waypointIndex]['label'] = label
        self.context['ng_cave']['waypoints']['items'][waypointIndex]['options'] = options
        self.enabledProfile['config']['ng_cave']['waypoints']['items'][waypointIndex]['options'] = options
        self.db.update(self.enabledProfile)

    def updateIgnorableCreatureByIndex(self, creatureIndex, name=None):
        if name is not None:
            self.context['ignorable_creatures'][creatureIndex] = name
            self.enabledProfile['config']['ignorable_creatures'][creatureIndex] = name
            self.db.update(self.enabledProfile)

    def removeWaypointByIndex(self, index):
        self.context['ng_cave']['waypoints']['items'].pop(index)
        self.enabledProfile['config']['ng_cave']['waypoints']['items'].pop(
            index)
        self.db.update(self.enabledProfile)

    def removeComboByIndex(self, index):
        self.context['ng_comboSpells']['items'].pop(index)
        self.enabledProfile['config']['ng_comboSpells']['items'].pop(
            index)
        self.db.update(self.enabledProfile)

    def removeIgnorableCreatureByIndex(self, index):
        self.context['ignorable_creatures'].pop(index)
        self.enabledProfile['config']['ignorable_creatures'].pop(index)
        self.db.update(self.enabledProfile)

    def play(self):
        if self.context['window'] is None:
            messagebox.showerror(
                'Erro', 'Tibia window is not set!')
            return
        self.context['window'].activate()
        time.sleep(1)
        # screenshot = getScreenshot()
        # chatTabs = getTabs(screenshot)
        # if 'loot' not in chatTabs:
        #     messagebox.showerror(
        #         'Erro', 'Loot tab must be open!')
        #     return
        self.context['ng_pause'] = False

    def pause(self):
        self.context['ng_pause'] = True
        self.context['ng_tasksOrchestrator'].setRootTask(self.context, None)
        self.context['ng_cave']['waypoints']['currentIndex'] = None
        self.context['loot']['corpsesToLoot'] = []
        resetOldList()

    def toggleHealingPotionsByKey(self, healthPotionType, enabled):
        self.context['healing']['potions'][healthPotionType]['enabled'] = enabled
        self.enabledProfile['config']['healing']['potions'][healthPotionType]['enabled'] = enabled
        self.db.update(self.enabledProfile)

    def toggleFoodByKey(self, enabled):
        self.context['healing']['eatFood']['enabled'] = enabled
        self.enabledProfile['config']['healing']['eatFood']['enabled'] = enabled
        self.db.update(self.enabledProfile)

    def toggleHealingHighPriorityByKey(self, key, enabled):
        self.context['healing']['highPriority'][key]['enabled'] = enabled
        self.enabledProfile['config']['healing']['highPriority'][key]['enabled'] = enabled
        self.db.update(self.enabledProfile)

    def setShovelHotkey(self, hotkey):
        self.context['general_hotkeys']['shovel_hotkey'] = hotkey
        self.enabledProfile['config']['general_hotkeys']['shovel_hotkey'] = hotkey
        self.db.update(self.enabledProfile)

    def setRopeHotkey(self, hotkey):
        self.context['general_hotkeys']['rope_hotkey'] = hotkey
        self.enabledProfile['config']['general_hotkeys']['rope_hotkey'] = hotkey
        self.db.update(self.enabledProfile)

    def setHotkeyHealingHighPriorityByKey(self, key, hotkey):
        self.context['healing']['highPriority'][key]['hotkey'] = hotkey
        self.enabledProfile['config']['healing']['highPriority'][key]['hotkey'] = hotkey
        self.db.update(self.enabledProfile)

    def setHealthFoodHpPercentageLessThanOrEqual(self, hpPercentageLessThanOrEqual):
        self.context['healing']['highPriority']['healthFood']['hpPercentageLessThanOrEqual'] = hpPercentageLessThanOrEqual
        self.enabledProfile['config']['healing']['highPriority']['healthFood'][
            'hpPercentageLessThanOrEqual'] = hpPercentageLessThanOrEqual
        self.db.update(self.enabledProfile)

    def setManaFoodHpPercentageLessThanOrEqual(self, manaPercentageLessThanOrEqual):
        self.context['healing']['highPriority']['manaFood']['manaPercentageLessThanOrEqual'] = manaPercentageLessThanOrEqual
        self.enabledProfile['config']['healing']['highPriority']['manaFood'][
            'manaPercentageLessThanOrEqual'] = manaPercentageLessThanOrEqual
        self.db.update(self.enabledProfile)

    def toggleSpellByKey(self, healthPotionType, enabled):
        self.context['healing']['spells'][healthPotionType]['enabled'] = enabled
        self.enabledProfile['config']['healing']['spells'][healthPotionType]['enabled'] = enabled
        self.db.update(self.enabledProfile)

    def setFoodHotkey(self, hotkey):
        self.context['healing']['eatFood']['hotkey'] = hotkey
        self.enabledProfile['config']['healing']['eatFood']['hotkey'] = hotkey
        self.db.update(self.enabledProfile)

    def setHealthPotionHotkeyByKey(self, healthPotionType, hotkey):
        self.context['healing']['potions'][healthPotionType]['hotkey'] = hotkey
        self.enabledProfile['config']['healing']['potions'][healthPotionType]['hotkey'] = hotkey
        self.db.update(self.enabledProfile)

    def setHealthPotionSlotByKey(self, healthPotionType, slot):
        self.context['healing']['potions'][healthPotionType]['slot'] = slot
        self.enabledProfile['config']['healing']['potions'][healthPotionType]['slot'] = slot
        self.db.update(self.enabledProfile)

    def setSpellHotkeyByKey(self, healthPotionType, hotkey):
        self.context['healing']['spells'][healthPotionType]['hotkey'] = hotkey
        self.enabledProfile['config']['healing']['spells'][healthPotionType]['hotkey'] = hotkey
        self.db.update(self.enabledProfile)

    def setHealthPotionHpPercentageLessThanOrEqual(self, healthPotionType, hpPercentage):
        self.context['healing']['potions'][healthPotionType]['hpPercentageLessThanOrEqual'] = hpPercentage
        self.enabledProfile['config']['healing']['potions'][healthPotionType]['hpPercentageLessThanOrEqual'] = hpPercentage
        self.db.update(self.enabledProfile)

    def setSwapRingHpPercentageLessThanOrEqual(self, hpPercentageLessThanOrEqual):
        self.context['healing']['highPriority']['swapRing']['tankRing']['hpPercentageLessThanOrEqual'] = hpPercentageLessThanOrEqual
        self.enabledProfile['config']['healing']['highPriority']['swapRing']['tankRing'][
            'hpPercentageLessThanOrEqual'] = hpPercentageLessThanOrEqual
        self.db.update(self.enabledProfile)

    def setSwapTankRingHotkey(self, hotkey):
        self.context['healing']['highPriority']['swapRing']['tankRing']['hotkey'] = hotkey
        self.enabledProfile['config']['healing']['highPriority']['swapRing']['tankRing']['hotkey'] = hotkey
        self.db.update(self.enabledProfile)

    def setSwapTankRingSlotByKey(self, slot):
        self.context['healing']['highPriority']['swapRing']['tankRing']['slot'] = slot
        self.enabledProfile['config']['healing']['highPriority']['swapRing']['tankRing']['slot'] = slot
        self.db.update(self.enabledProfile)

    def setSwapMainRingSlotByKey(self, slot):
        self.context['healing']['highPriority']['swapRing']['mainRing']['slot'] = slot
        self.enabledProfile['config']['healing']['highPriority']['swapRing']['mainRing']['slot'] = slot
        self.db.update(self.enabledProfile)

    def setSwapMainRingHotkey(self, hotkey):
        self.context['healing']['highPriority']['swapRing']['mainRing']['hotkey'] = hotkey
        self.enabledProfile['config']['healing']['highPriority']['swapRing']['mainRing']['hotkey'] = hotkey
        self.db.update(self.enabledProfile)

    def setSwapRingHpPercentageGreaterThan(self, hpPercentageGreaterThan):
        self.context['healing']['highPriority']['swapRing']['mainRing']['hpPercentageGreaterThan'] = hpPercentageGreaterThan
        self.enabledProfile['config']['healing']['highPriority']['swapRing']['mainRing'][
            'hpPercentageGreaterThan'] = hpPercentageGreaterThan
        self.db.update(self.enabledProfile)

    def setSwapAmuletHpPercentageLessThanOrEqual(self, hpPercentageLessThanOrEqual):
        self.context['healing']['highPriority']['swapAmulet']['tankAmulet']['hpPercentageLessThanOrEqual'] = hpPercentageLessThanOrEqual
        self.enabledProfile['config']['healing']['highPriority']['swapAmulet']['tankAmulet'][
            'hpPercentageLessThanOrEqual'] = hpPercentageLessThanOrEqual
        self.db.update(self.enabledProfile)

    def setSwapAmuletHpPercentageGreaterThan(self, hpPercentageGreaterThan):
        self.context['healing']['highPriority']['swapAmulet']['mainAmulet']['hpPercentageGreaterThan'] = hpPercentageGreaterThan
        self.enabledProfile['config']['healing']['highPriority']['swapAmulet']['mainAmulet'][
            'hpPercentageGreaterThan'] = hpPercentageGreaterThan
        self.db.update(self.enabledProfile)

    def setSwapTankAmuletHotkey(self, hotkey):
        self.context['healing']['highPriority']['swapAmulet']['tankAmulet']['hotkey'] = hotkey
        self.enabledProfile['config']['healing']['highPriority']['swapAmulet']['tankAmulet']['hotkey'] = hotkey
        self.db.update(self.enabledProfile)

    def setSwapMainAmuletHotkey(self, hotkey):
        self.context['healing']['highPriority']['swapAmulet']['mainAmulet']['hotkey'] = hotkey
        self.enabledProfile['config']['healing']['highPriority']['swapAmulet']['mainAmulet']['hotkey'] = hotkey
        self.db.update(self.enabledProfile)

    def setSwapTankAmuletSlotByKey(self, slot):
        self.context['healing']['highPriority']['swapAmulet']['tankAmulet']['slot'] = slot
        self.enabledProfile['config']['healing']['highPriority']['swapAmulet']['tankAmulet']['slot'] = slot
        self.db.update(self.enabledProfile)

    def setSwapMainAmuletSlotByKey(self, slot):
        self.context['healing']['highPriority']['swapAmulet']['mainAmulet']['slot'] = slot
        self.enabledProfile['config']['healing']['highPriority']['swapAmulet']['mainAmulet']['slot'] = slot
        self.db.update(self.enabledProfile)

    def setSpellHpPercentageLessThanOrEqual(self, spellType, hpPercentage):
        self.context['healing']['spells'][spellType]['hpPercentageLessThanOrEqual'] = hpPercentage
        self.enabledProfile['config']['healing']['spells'][spellType]['hpPercentageLessThanOrEqual'] = hpPercentage
        self.db.update(self.enabledProfile)

    def setSpellManaPercentageGreaterThanOrEqual(self, spellType, hpPercentage):
        self.context['healing']['spells'][spellType]['manaPercentageGreaterThanOrEqual'] = hpPercentage
        self.enabledProfile['config']['healing']['spells'][spellType]['manaPercentageGreaterThanOrEqual'] = hpPercentage
        self.db.update(self.enabledProfile)

    def setSpellName(self, spellType, spell):
        self.context['healing']['spells'][spellType]['spell'] = spell
        self.enabledProfile['config']['healing']['spells'][spellType]['spell'] = spell
        self.db.update(self.enabledProfile)

    def setHealthPotionManaPercentageGreaterThanOrEqual(self, healthPotionType, hpPercentage):
        self.context['healing']['potions'][healthPotionType]['manaPercentageGreaterThanOrEqual'] = hpPercentage
        self.enabledProfile['config']['healing']['potions'][healthPotionType]['manaPercentageGreaterThanOrEqual'] = hpPercentage
        self.db.update(self.enabledProfile)

    def setHealthPotionManaPercentageLessThanOrEqual(self, healthPotionType, hpPercentage):
        self.context['healing']['potions'][healthPotionType]['manaPercentageLessThanOrEqual'] = hpPercentage
        self.enabledProfile['config']['healing']['potions'][healthPotionType]['manaPercentageLessThanOrEqual'] = hpPercentage
        self.db.update(self.enabledProfile)

    def toggleCavebot(self, enabled):
        self.context['ng_cave']['enabled'] = enabled
        self.enabledProfile['config']['ng_cave']['enabled'] = enabled
        self.db.update(self.enabledProfile)

    def toggleRunToCreatures(self, enabled):
        self.context['ng_cave']['runToCreatures'] = enabled
        self.enabledProfile['config']['ng_cave']['runToCreatures'] = enabled
        self.db.update(self.enabledProfile)

    def toggleComboSpells(self, enabled):
        self.context['ng_comboSpells']['enabled'] = enabled
        self.enabledProfile['config']['ng_comboSpells']['enabled'] = enabled
        self.db.update(self.enabledProfile)

    def toggleSingleCombo(self, enabled, index):
        self.context['ng_comboSpells']['items'][index]['enabled'] = enabled
        self.enabledProfile['config']['ng_comboSpells']['items'][index]['enabled'] = enabled
        self.db.update(self.enabledProfile)

    def removeSpellByIndex(self, index, indexTable):
        self.context['ng_comboSpells']['items'][index]['spells'].pop(indexTable)
        # self.enabledProfile['config']['ng_comboSpells']['items'][index]['spells'].pop(
        #     index)
        self.db.update(self.enabledProfile)

    def changeComboName(self, name, index):
        self.context['ng_comboSpells']['items'][index]['name'] = name
        self.enabledProfile['config']['ng_comboSpells']['items'][index]['name'] = name
        self.db.update(self.enabledProfile)

    def setCompare(self, compare, index):
        self.context['ng_comboSpells']['items'][index]['creatures']['compare'] = compare
        self.enabledProfile['config']['ng_comboSpells']['items'][index]['creatures']['compare'] = compare
        self.db.update(self.enabledProfile)

    def changeCompareValue(self, value, index):
        if not value:
            return
        self.context['ng_comboSpells']['items'][index]['creatures']['value'] = int(value)
        self.enabledProfile['config']['ng_comboSpells']['items'][index]['creatures']['value'] = int(value)
        self.db.update(self.enabledProfile)

    def setComboSpellName(self, name, index, indexSecond):
        self.context['ng_comboSpells']['items'][index]['spells'][indexSecond]['name'] = name
        self.enabledProfile['config']['ng_comboSpells']['items'][index]['spells'][indexSecond]['name'] = name
        self.db.update(self.enabledProfile)

    def setComboSpellHotkey(self, key, index, indexSecond):
        self.context['ng_comboSpells']['items'][index]['spells'][indexSecond]['hotkey'] = key
        self.enabledProfile['config']['ng_comboSpells']['items'][index]['spells'][indexSecond]['hotkey'] = key
        self.db.update(self.enabledProfile)

    def toggleAutoHur(self, enabled):
        self.context['auto_hur']['enabled'] = enabled
        self.enabledProfile['config']['auto_hur']['enabled'] = enabled
        self.db.update(self.enabledProfile)

    def toggleAutoHurPz(self, enabled):
        self.context['auto_hur']['pz'] = enabled
        self.enabledProfile['config']['auto_hur']['pz'] = enabled
        self.db.update(self.enabledProfile)

    def setAutoHurHotkey(self, hotkey):
        self.context['auto_hur']['hotkey'] = hotkey
        self.enabledProfile['config']['auto_hur']['hotkey'] = hotkey
        self.db.update(self.enabledProfile)

    def setAutoHurSpell(self, spell):
        self.context['auto_hur']['spell'] = spell
        self.enabledProfile['config']['auto_hur']['spell'] = spell
        self.db.update(self.enabledProfile)

    def toggleAlert(self, enabled):
        self.context['alert']['enabled'] = enabled
        self.enabledProfile['config']['alert']['enabled'] = enabled
        self.db.update(self.enabledProfile)

    def toggleAlertCave(self, enabled):
        self.context['alert']['cave'] = enabled
        self.enabledProfile['config']['alert']['cave'] = enabled
        self.db.update(self.enabledProfile)

    def toggleAlertSayPlayer(self, enabled):
        self.context['alert']['sayPlayer'] = enabled
        self.enabledProfile['config']['alert']['sayPlayer'] = enabled
        self.db.update(self.enabledProfile)

    def toggleClearStatsPoison(self, enabled):
        self.context['clear_stats']['poison'] = enabled
        self.enabledProfile['config']['clear_stats']['poison'] = enabled
        self.db.update(self.enabledProfile)

    def setClearStatsPoisonHotkey(self, hotkey):
        self.context['clear_stats']['poison_hotkey'] = hotkey
        self.enabledProfile['config']['clear_stats']['poison_hotkey'] = hotkey
        self.db.update(self.enabledProfile)

    def toggleManaPotionsByKey(self, manaPotionType, enabled):
        self.context['healing']['potions'][manaPotionType]['enabled'] = enabled

    def setManaPotionManaPercentageLessThanOrEqual(self, manaPotionType, manaPercentage):
        self.context['healing']['potions'][manaPotionType]['manaPercentageLessThanOrEqual'] = manaPercentage

    def toggleHealingSpellsByKey(self, contextKey, enabled):
        self.context['healing']['spells'][contextKey]['enabled'] = enabled

    def setHealingSpellsHpPercentage(self, contextKey, hpPercentage):
        self.context['healing']['spells'][contextKey]['hpPercentageLessThanOrEqual'] = hpPercentage

    def setHealingSpellsHotkey(self, contextKey, hotkey):
        self.context['healing']['spells'][contextKey]['hotkey'] = hotkey
