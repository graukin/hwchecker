import logging

__all__ = ['mbhandler', 'mhandle', 'sending']


def init_logger(verbosity):
    logging.basicConfig(format='[%(asctime)s] %(levelname).3s: %(message)s', datefmt='%d.%m.%Y %H:%M:%S')
    if verbosity > 0:
        logging.getLogger().setLevel(logging.INFO if verbosity == 1 else logging.DEBUG)
