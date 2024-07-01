from src.repositories.statsBar.core import getStats
from ...typings import Context

# TODO: add unit tests
def setMapStatsBarMiddleware(context: Context) -> Context:
    stats = getStats(context['ng_screenshot'])

    if stats is not None:
      context['statsBar']['pz'] = stats['pz']
      context['statsBar']['hur'] = stats['hur']
      context['statsBar']['poison'] = stats['poison']

    return context
