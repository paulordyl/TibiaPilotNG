# TODO: add types
# TODO: add unit tests
def loadContextFromConfig(config, context):
    context['ng_backpacks'] = config['ng_backpacks'].copy()
    context['general_hotkeys'] = config['general_hotkeys'].copy()
    context['auto_hur'] = config['auto_hur'].copy()
    context['alert'] = config['alert'].copy()
    context['clear_stats'] = config['clear_stats'].copy()
    context['ignorable_creatures'] = config['ignorable_creatures'].copy()
    context['ng_cave']['enabled'] = config['ng_cave']['enabled']
    context['ng_cave']['runToCreatures'] = config['ng_cave']['runToCreatures']
    context['ng_cave']['waypoints']['items'] = config['ng_cave']['waypoints']['items'].copy()
    context['ng_comboSpells']['enabled'] = config['ng_comboSpells']['enabled']
    for comboSpellsItem in config['ng_comboSpells']['items']:
        comboSpellsItem['currentSpellIndex'] = 0
        context['ng_comboSpells']['items'].append(comboSpellsItem)
    context['healing'] = config['healing'].copy()
    return context

def loadNgCfgs(config, context):
    context['ng_backpacks'] = config['ng_backpacks'].copy()
    context['general_hotkeys'] = config['general_hotkeys'].copy()
    context['auto_hur'] = config['auto_hur'].copy()
    context['alert'] = config['alert'].copy()
    context['clear_stats'] = config['clear_stats'].copy()
    context['ng_comboSpells']['enabled'] = config['ng_comboSpells']['enabled']
    for comboSpellsItem in config['ng_comboSpells']['items']:
        comboSpellsItem['currentSpellIndex'] = 0
        context['ng_comboSpells']['items'].append(comboSpellsItem)
    context['healing'] = config['healing'].copy()
    return context
