from .typings import Context


# TODO: add unit tests
def hasCreaturesToAttack(context: Context) -> bool:
    context['ng_targeting']['hasIgnorableCreatures'] = False
    if len(context['gameWindow']['monsters']) == 0:
        context['ng_targeting']['canIgnoreCreatures'] = True
        return False
    if context['ng_targeting']['canIgnoreCreatures'] == False:
        return True
    ignorableGameWindowCreatures = []
    for gameWindowCreature in context['gameWindow']['monsters']:
        shouldIgnoreCreature = context['ng_targeting']['creatures'].get(gameWindowCreature['name'], { 'ignore': True if gameWindowCreature['name'] in context['ignorable_creatures'] else False })['ignore']
        if shouldIgnoreCreature:
            context['ng_targeting']['hasIgnorableCreatures'] = True
            ignorableGameWindowCreatures.append(gameWindowCreature)
    return len(ignorableGameWindowCreatures) < len(context['gameWindow']['monsters'])
