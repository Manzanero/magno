import traceback


def get_stacktrace_str(e):
    return ''.join(traceback.format_exception(etype=type(e), value=e, tb=e.__traceback__))