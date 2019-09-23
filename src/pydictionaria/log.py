import logging
from functools import partial

_logger = None


def colored(msg, *args, **kw):
    return msg


def get_logger():
    global _logger
    if _logger is None:
        _logger = logging.getLogger('pydictionaria')
    return _logger


def emit(method, entry, msg, marker=None, content=None):
    if marker:
        msg = '{0}: {1}'.format(
            msg, colored('\\{0} {1}'.format(marker, content or ''), 'green'))
    getattr(get_logger(), method, print)(
        '{0: <12} {1}'.format(
            colored(
                '\\lx {0}:'.format(getattr(entry, 'id', entry)), 'blue', attrs=['bold']),
            msg))


info = partial(emit, 'info')
warn = partial(emit, 'warn')
error = partial(emit, 'error')
pprint = partial(emit, 'xxx')
