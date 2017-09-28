import logging


def set_up(debug):
    if debug:
        logging_level = logging.DEBUG
    else:
        logging_level = logging.INFO

    logging.basicConfig(format='%(asctime)s ~ %(levelname)-10s %(name)-25s %(message)s',
                        datefmt='%Y-%m-%d %H:%M',
                        level=logging_level)

    logging.getLogger('telegram').setLevel(logging.INFO)
    logging.getLogger('requests').setLevel(logging.INFO)
    logging.getLogger('JobQueue').setLevel(logging.INFO)

    logging.addLevelName(logging.DEBUG, '🐛 DEBUG')
    logging.addLevelName(logging.INFO, '📑 INFO')
    logging.addLevelName(logging.WARNING, '🤔 WARNING')
    logging.addLevelName(logging.ERROR, '🚨 ERROR')
