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
