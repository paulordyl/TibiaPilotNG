from typing import Union, Dict, Any
from src.repositories.gameWindow.creatures import hasTargetToCreature
from .core.tasks.attackClosestCreature import AttackClosestCreatureTask
from .core.tasks.common.base import BaseTask
from .core.tasks.buyBackpack import BuyBackpackTask
from .core.tasks.depositGold import DepositGoldTask
from .core.tasks.depositItems import DepositItemsTask
from .core.tasks.depositItemsHouse import DepositItemsHouseTask
from .core.tasks.dropFlasks import DropFlasksTask
from .core.tasks.move import MoveTask # Assuming 'move.py' contains MoveTask for 'walk'
from .core.tasks.moveDown import MoveDownTask
from .core.tasks.moveUp import MoveUpTask
from .core.tasks.openDoorWaypoint import OpenDoorWaypointTask # Assuming for 'openDoor'
from .core.tasks.refill import RefillTask
from .core.tasks.refillChecker import RefillCheckerTask
from .core.tasks.rightClickDirectionWaypoint import RightClickDirectionWaypointTask # For 'rightClickDirection'
from .core.tasks.rightClickUseWaypoint import RightClickUseWaypointTask # For 'rightClickUse'
from .core.tasks.useLadderWaypoint import UseLadderWaypointTask # For 'useLadder'
from .core.tasks.useRopeWaypoint import UseRopeWaypointTask # For 'useRope'
from .core.tasks.useShovelWaypoint import UseShovelWaypointTask # For 'useShovel'
from .core.tasks.travel import TravelTask
from .core.tasks.executeSpellSequenceTask import ExecuteSpellSequenceTask # New Task
from .typings import Context
import logging


# TODO: add unit tests

# This function will now be responsible for deciding the next task based on the current waypoint
def resolveCavebotTasks(context: Context) -> Context:
    if context['ng_cave']['enabled'] == False:
        return context

    # 전투 중이거나, 현재 작업이 없거나, 현재 작업이 완료된 경우에만 새 작업을 결정합니다.
    # Always prioritize combat if engaged
    if context['ng_cave']['isAttackingSomeCreature']:
        if context['ng_cave']['targetCreature'] is not None and \
           hasTargetToCreature(context['gameWindow']['monsters'], context['ng_cave']['targetCreature'], context['ng_radar']['coordinate']):
            if context['ng_tasksOrchestrator'].getCurrentTaskName(context) != 'attackClosestCreature':
                logging.info("Cavebot: Target is valid, ensuring AttackClosestCreatureTask.")
                context['ng_tasksOrchestrator'].setRootTask(context, AttackClosestCreatureTask())
        elif context['ng_cave']['closestCreature'] is not None:
            logging.info("Cavebot: No specific target or target lost, attacking closest creature.")
            context['ng_tasksOrchestrator'].setRootTask(context, AttackClosestCreatureTask())
        # If isAttackingSomeCreature is true but no target and no closest, implies combat just ended or state is weird.
        # Let it fall through to waypoint logic or clear isAttackingSomeCreature.
        # For now, if in combat mode but no valid target, let current task (if any) continue or get next waypoint task.
        # This prevents immediately overriding a non-combat task if combat flag isn't cleared fast enough.
        if context['ng_tasksOrchestrator'].getCurrentTask(context) is not None and \
           not context['ng_tasksOrchestrator'].getCurrentTask(context).finished:
            return context


    # If no current task or current task is finished, get next waypoint task
    if context['ng_tasksOrchestrator'].getCurrentTask(context) is None or \
       context['ng_tasksOrchestrator'].getCurrentTask(context).finished:

        current_waypoint_index = context['ng_cave']['waypoints'].get('currentIndex', 0)
        waypoints = context['ng_cave']['waypoints']['items'] # These are already filtered executable waypoints

        if not (0 <= current_waypoint_index < len(waypoints)):
            logging.info("Cavebot: All waypoints processed or invalid index.")
            context['ng_cave']['enabled'] = False # Stop cavebot if all waypoints are done
            context['ng_tasksOrchestrator'].setRootTask(context, None) # Clear tasks
            return context

        waypoint = waypoints[current_waypoint_index]
        new_task = get_task_from_waypoint(context, waypoint)

        if new_task:
            logging.info(f"Cavebot: Setting new task: {new_task.name} from waypoint {current_waypoint_index} ({waypoint.get('type')})")
            context['ng_tasksOrchestrator'].setRootTask(context, new_task)
        else:
            logging.warning(f"Cavebot: Could not determine task for waypoint: {waypoint}")
            # Optionally, advance waypoint index to avoid getting stuck, or handle error
            context['ng_cave']['waypoints']['currentIndex'] = current_waypoint_index + 1


    return context

def get_task_from_waypoint(context: Context, waypoint: Dict[str, Any]) -> Union[BaseTask, None]:
    waypoint_type = waypoint['type']
    options = waypoint.get('options', {})
    coordinate = waypoint.get('coordinate') # Not all tasks use coordinate directly from waypoint root

    # TODO: Ensure all task constructors are correctly mapped and receive necessary args
    # Many tasks below are placeholders and might need specific arguments from waypoint or context
    if waypoint_type == 'walk': # 'walk' type often implies moving towards 'coordinate'
        # Assuming MoveTask is for a single direction, and 'walk' means pathfinding.
        # The orchestrator or a specific pathfinding task would handle multiple moves.
        # For now, if 'walk' means "go to this coordinate", a more complex task is needed.
        # Let's assume 'walk' here means a single step towards the coordinate if not already there,
        # or it's handled by a parent task that decomposes it.
        # This mapping needs to align with how the orchestrator and specific tasks work.
        # For this iteration, let's assume 'walk' waypoints are handled by a task that sets sub-tasks (like multiple Moves)
        # Or, if single 'walk' means one SQM, it might be a specific 'WalkToCoordinateTask'
        # For now, let's return None for 'walk' as it's usually handled by setNextWaypointTask and a movement task.
        # The existing 'setNextWaypoint.py' task is likely what handles advancing and then a movement task is set.
        # This function is more for action-oriented waypoints.
        # However, if the orchestrator expects a task for every waypoint type including 'walk':
        # return WalkTask(coordinate) # Needs proper WalkTask
        return None # Let setNextWaypoint handle it, then a movement task will be chosen by orchestrator

    elif waypoint_type == 'singleMove': # This seems to imply a direct single step
        direction = options.get('direction')
        if direction:
            # MoveTask might need the actual current coordinate to step from, or just the direction
            return MoveTask(direction) # Assuming MoveTask takes direction
        return None

    elif waypoint_type == 'rightClickDirection':
        return RightClickDirectionWaypointTask(waypoint)
    elif waypoint_type == 'useRope':
        return UseRopeWaypointTask(coordinate)
    elif waypoint_type == 'useShovel':
        return UseShovelWaypointTask(coordinate)
    elif waypoint_type == 'rightClickUse':
        return RightClickUseWaypointTask(waypoint)
    elif waypoint_type == 'openDoor':
        return OpenDoorWaypointTask(waypoint)
    elif waypoint_type == 'useLadder':
        return UseLadderWaypointTask(waypoint)
    elif waypoint_type == 'moveUp':
        return MoveUpTask(waypoint) # Assuming it takes the full waypoint
    elif waypoint_type == 'moveDown':
        return MoveDownTask(waypoint) # Assuming it takes the full waypoint

    elif waypoint_type == 'depositGold':
        return DepositGoldTask()
    elif waypoint_type == 'depositItems':
        return DepositItemsTask(options.get('city'))
    elif waypoint_type == 'depositItemsHouse':
        return DepositItemsHouseTask(options.get('city')) # City is optional here
    elif waypoint_type == 'dropFlasks':
        return DropFlasksTask()

    elif waypoint_type == 'travel':
        return TravelTask(waypoint)
    elif waypoint_type == 'refill':
        return RefillTask(waypoint)
    elif waypoint_type == 'buyBackpack':
        return BuyBackpackTask(waypoint)
    elif waypoint_type == 'refillChecker':
        return RefillCheckerTask(waypoint)

    elif waypoint_type == 'executeSpellSequence':
        sequence_label = options.get('sequenceLabel')
        if sequence_label:
            return ExecuteSpellSequenceTask(sequenceLabel=sequence_label)
        else:
            logging.error(f"Waypoint 'executeSpellSequence' is missing 'sequenceLabel' in options.")
            return None

    # Add other explicit task mappings here as they are created/confirmed
    # e.g., attackClosestCreature, attackMonstersBox, etc. are usually set by combat logic, not directly by waypoint type.

    logging.warning(f"No specific task mapped for waypoint type: {waypoint_type}")
    return None


# TODO: add unit tests
def shouldAskForCavebotTasks(context: Context) -> bool:
    if context['way'] != 'ng_cave' or context['ng_cave']['enabled'] == False : # Check if cavebot is enabled
        return False
    # If currently in combat, let combat logic handle tasks (e.g. AttackClosestCreatureTask)
    if context['ng_cave']['isAttackingSomeCreature']:
        return False

    currentTask = context['ng_tasksOrchestrator'].getCurrentTask(context)
    if currentTask is None or currentTask.finished: # If no task or current is finished
        return True

    # This list was to prevent re-triggering cavebot task resolution for tasks that are part of a sequence
    # or are themselves managing sub-tasks. With the new get_task_from_waypoint,
    # the main condition is simply if currentTask is None or finished.
    # The new ExecuteSpellSequenceTask will manage its own sub-actions.
    # return (currentTask.name not in ['dropFlasks', 'lootCorpse', 'moveDown', 'moveUp', 'singleMove', 'rightClickDirection', 'refillChecker', 'singleWalk', 'refillChecker', 'useRopeWaypoint', 'useShovelWaypoint', 'rightClickUseWaypoint', 'openDoor', 'useLadderWaypoint'])
    return False # Only ask for new task if current is None or finished
