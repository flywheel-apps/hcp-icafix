import sys
import time
import logging

log = logging.getLogger(__name__)

def get_custom_logger(context):
    """
    get_custom_logger is a customizable template for creating a logger.
    
    Args:
        context (flywheel.gear_context.GearContext): The gear context object
            containing the 'gear_dict' dictionary attribute with keys/values,
            'manifest_json': The complete manifest dictionary. Must be 
            initialized elsewhere. The manifest keys are used to configure the 
            log configuration and how it displays.
    
    Returns:
        logger: The log created with the logging configuration set accordingly
    """    

    # Initialize Custom Logging
    # Timestamps with logging assist debugging algorithms
    # With long execution times
    manifest = context.gear_dict['manifest_json']

    # Set suite (default to flywheel)
    try:
        suite = manifest['custom']['flywheel']['suite']
    except KeyError:
        suite = 'flywheel'

    # Set gear_name
    gear_name = manifest['name']

    log_name = '/'.join([suite, gear_name])

    log_level = logging.INFO


    # Tweak the formatting
    fmt = '%(asctime)s.%(msecs)03d %(levelname)-8s [%(name)s %(funcName)s()]: %(message)s'
    dtfmt = '%Y-%m-%d %H:%M:%S'
    logging.basicConfig(level=log_level, format=fmt, datefmt=dtfmt)
    log = logging.getLogger(log_name)
    log.critical('{} log level is {}'.format(log_name, log_level))

    return log