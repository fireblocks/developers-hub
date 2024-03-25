import sys

logging_config = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'callbackLogFormatter': {
            'format': '%(name)s: %(asctime)s | %(filename)s:%(lineno)d | %(levelname)s: %(message)s',
        },
    },
    'handlers': {
        'consoleHandler': {
            'class': 'logging.StreamHandler',
            'level': 'DEBUG',
            'formatter': 'callbackLogFormatter',
            'stream': sys.stdout,
        },
        'consoleErrorHandler': {
            'class': 'logging.StreamHandler',
            'level': 'ERROR',
            'formatter': 'callbackLogFormatter',
            'stream': sys.stderr,
        },
    },
    'loggers': {
        '': {  # root logger
            'handlers': ['consoleHandler', 'consoleErrorHandler'],
            'level': 'DEBUG',
            'propagate': True,
        },
    }
}