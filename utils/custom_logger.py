import logging
import sys
import time

def log_config(context):
    config = context.config
    inputs = context._invocation['inputs']
    context.log.info('\n\nThe following inputs are used:')
    for key in inputs.keys():
        if key == 'api-key':
            context.log.info('{}: *********'.format(key))
        else:
            context.log.info(
                '{}: {}'.format(key,context.get_input_path(key))
            )
    context.log.info('\n\nThe following configuration parameters are set:')
    for key in config.keys():
        context.log.info(
            '{}: {}'.format(key,context.config[key])
        )
    context.log.info('\n')

def get_custom_logger(log_name):
    # Initialize Custom Logging
    # Timestamps with logging assist debugging algorithms
    # With long execution times
    handler = logging.StreamHandler(stream=sys.stdout)
    formatter = logging.Formatter(
                fmt='%(levelname)s - %(name)-8s - %(asctime)s -  %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S')
    handler.setFormatter(formatter)
    logger = logging.getLogger(log_name)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)

    return logger