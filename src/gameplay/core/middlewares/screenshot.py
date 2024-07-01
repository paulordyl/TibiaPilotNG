from src.utils.core import getScreenshot
from ...typings import Context


# TODO: add unit tests
def setScreenshotMiddleware(context: Context) -> Context:
    context['ng_screenshot'] = getScreenshot()
    return context
