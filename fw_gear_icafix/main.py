"""Main module."""

import logging

log = logging.getLogger(__name__)


def run(text):
    """[summary]

    Returns:
        [type]: [description]
    """
    log.info("This is the beginning of the run file")
    log.info(text)

    return 0
