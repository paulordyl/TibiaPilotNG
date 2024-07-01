from src.repositories.radar.core import getClosestWaypointIndexFromCoordinate, getCoordinate
from ...typings import Context


# TODO: add unit tests
def setRadarMiddleware(context: Context) -> Context:
    context['ng_radar']['coordinate'] = getCoordinate(
        context['ng_screenshot'], previousCoordinate=context['ng_radar']['previousCoordinate'])
    return context


# TODO: add unit tests
def setWaypointIndexMiddleware(context: Context) -> Context:
    if context['ng_cave']['waypoints']['currentIndex'] is None:
        context['ng_cave']['waypoints']['currentIndex'] = getClosestWaypointIndexFromCoordinate(
            context['ng_radar']['coordinate'], context['ng_cave']['waypoints']['items'])
    return context
