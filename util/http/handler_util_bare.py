import logging


def startup_init(config, dbPool):
    '''
    ENTRY POINT: perform any pre-loading/caching of objects or anything else before server startup in here (if any)
    '''
    logging.info('startup init ...')


def shutdown_cleanup(config, dbPool):
    '''
    ENTRY POINT: perform any cleaning up of objects or anything else before server shutdown in here (if any)
    '''
    logging.info('shutdown cleanup ...')


def register_handlers(config, dbPool):
    '''
    ENTRY POINT: register all handlers in here
    '''
    logging.info('register all handlers ...')
