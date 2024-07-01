from src.shared.typings import GrayImage
from .locators import getStopIconPosition, getStatsPz, getStatsHur, getStatsPoison

def getStats(screenshot: GrayImage):
  stopIcon = getStopIconPosition(screenshot)

  if stopIcon is not None:
    statsBarPosition = (
      stopIcon[0] - 117,          # x_inicio
      stopIcon[1] + 1,            # y_inicio
      stopIcon[0] - 11,           # x_fim
      stopIcon[1] + 12            # y_fim
    )

    statsBarImg = screenshot[statsBarPosition[1]:statsBarPosition[3], statsBarPosition[0]:statsBarPosition[2]]

    statsPz = getStatsPz(statsBarImg)
    statsHur = getStatsHur(statsBarImg)
    statsPoison = getStatsPoison(statsBarImg)

    return {
      'pz': statsPz,
      'hur': statsHur,
      'poison': statsPoison
    }