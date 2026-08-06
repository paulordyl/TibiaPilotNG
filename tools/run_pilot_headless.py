"""Run a headless PilotNG loop without the GUI for smoke testing movement/attack/healing.

Usage:
  PYTHONPATH=$(pwd) python3 tools/run_pilot_headless.py

This will instantiate the Context and run the PilotNGThread.mainloop for a limited number of iterations
and print/log actions. Use ARDUINO_SIMULATE_WITH_PYAUTOGUI=1 to simulate mouse/keyboard.
"""
import time
import sys
import os

PY_PATH = os.getcwd()
if PY_PATH not in sys.path:
    sys.path.insert(0, PY_PATH)

from src.gameplay.context import context as default_context
from src.ui.context import Context as UIContext
from src.gameplay.threads.pilotNG import PilotNGThread


class SmokeContext(UIContext):
    def __init__(self, context):
        super().__init__(context)


def main(iterations=200):
    ctx = SmokeContext(default_context)
    # attempt to load an imported script if present
    import_path = os.path.join('src', 'data', 'imported', 'current-repo', 'sample_waypoints.json')
    alt_index = os.path.join('src', 'data', 'imported', 'current-repo', 'waypoints.json')
    try:
        if os.path.isfile(import_path):
            import json
            with open(import_path, 'r') as fh:
                data = json.load(fh)
                if isinstance(data, list):
                    print('Loading sample_waypoints.json into profile')
                    ctx.loadScript(data)
        elif os.path.isfile(alt_index):
            import json
            with open(alt_index, 'r') as fh:
                idx = json.load(fh)
                # if index references files, attempt to load first json waypoint file
                found = idx.get('found', [])
                for p in found:
                    if p.lower().endswith('.json') and os.path.isfile(p):
                        try:
                            with open(p, 'r') as fh2:
                                data = json.load(fh2)
                                if isinstance(data, list):
                                    print('Loaded', p, 'into profile via index')
                                    ctx.loadScript(data)
                                    break
                        except Exception:
                            continue
    except Exception as e:
        print('Error while loading imported scripts:', e)

    pilot = PilotNGThread(ctx)
    print('Starting headless pilot loop for', iterations, 'iterations')
    # run limited loop by calling handleGameData/handleGameplayTasks and observers manually
    for i in range(iterations):
        if ctx.context['ng_pause']:
            time.sleep(0.1)
            continue
        try:
            # Use same loop steps as PilotNGThread
            ctx.context = pilot.handleGameData(ctx.context)
            ctx.context = pilot.handleGameplayTasks(ctx.context)
            # execute tasks orchestrator step
            ctx.context = ctx.context['ng_tasksOrchestrator'].do(ctx.context)
            # healing observers (imported from module) are invoked inside PilotNGThread; for smoke, assume they run
            # Small sleep to avoid busy loop
            time.sleep(0.05)
        except Exception as e:
            print('Exception during smoke loop:', e)
            import traceback
            traceback.print_exc()
            break
    print('Smoke run complete')


if __name__ == '__main__':
    main()
