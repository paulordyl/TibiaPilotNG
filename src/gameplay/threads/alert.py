from threading import Thread
import winsound
import pathlib
from time import sleep

class AlertThread(Thread):
    # TODO: add typings
    def __init__(self, context):
        Thread.__init__(self, daemon=True)
        self.context = context
        self.runCount = 0

    def run(self):
        currentPath = pathlib.Path(__file__).parent.resolve()
        soundsPath = f'{currentPath}/sounds'        

        while True:
          players = self.context.context['gameWindow']['players']
          if players and self.context.context['alert']['enabled'] == True and self.context.context['ng_pause'] == False:
            if self.context.context['ng_cave']['waypoints']['currentIndex'] is None:
              self.runCount = 0
              sleep(1)
              continue
            refillCheckerIndex = next((index for index, item in enumerate(self.context.context['ng_cave']['waypoints']['items']) if item['type'] == 'refillChecker'), None)
            if refillCheckerIndex is not None and self.context.context['ng_cave']['waypoints']['currentIndex'] > refillCheckerIndex:
              self.runCount = 0
              sleep(1)
              continue
            if self.context.context['alert']['cave'] == True and self.context.context['ng_cave']['enabled'] == False:
              self.runCount = 0
              sleep(1)
              continue
            self.runCount = self.runCount + 1
            if self.runCount > 2:
              winsound.PlaySound(f"{soundsPath}/alert.wav", winsound.SND_FILENAME)
          else:
              self.runCount = 0
          sleep(1)
