from ...typings import Context


# TODO: add unit tests
def setCleanUpTasksMiddleware(context: Context) -> Context:
    currentTask = context['ng_tasksOrchestrator'].getCurrentTask(context)
    if currentTask is not None:
        if currentTask.isRootTask and currentTask.status == 'completed':
            context['ng_tasksOrchestrator'].reset()
        if currentTask.rootTask is not None:
            if currentTask.rootTask.status == 'completed':
                context['ng_tasksOrchestrator'].reset()
    return context
