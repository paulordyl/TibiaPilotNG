from src.gameplay.context import context
from src.gameplay.threads.legacy_game_loop import LegacyGameLoopThread
from src.gameplay.threads.ui import UIThread
from src.gameplay.threads.alert import AlertThread
from src.ui.context import Context

def main():
    contextInstance = Context(context)
    uiThreadInstance = UIThread(contextInstance)
    uiThreadInstance.start()
    alertThreadInstance = AlertThread(contextInstance)
    alertThreadInstance.start()
    legacyGameLoopThreadInstance = LegacyGameLoopThread(contextInstance)
    legacyGameLoopThreadInstance.mainloop()

if __name__ == '__main__':
    main()
