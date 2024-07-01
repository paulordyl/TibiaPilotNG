from src.repositories.chat.core import getTabs
from ...typings import Context


# TODO: add unit tests
def setChatTabsMiddleware(context: Context) -> Context:
    context['ng_chat']['tabs'] = getTabs(context['ng_screenshot'])
    return context
