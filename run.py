#!/usr/bin/env python3
import json
import os, os.path as op
from utils import args, results

import flywheel
from utils.custom_logger import get_custom_logger
import custom_gear_utils as cgu

if __name__ == '__main__':
    # Preamble: take care of all gear-typical activities.
    context = flywheel.GearContext()
    #get_Custom_Logger is defined in utils.py
    context.log = get_custom_logger('[flywheel:hcp-func]')

    context.log_config()

    # This gear will use a "custom_dict" dictionary as a custom-user field 
    # on the gear context.
    context.custom_dict ={}

    # grab environment for gear
    with open('/tmp/gear_environ.json', 'r') as f:
        environ = json.load(f)

    context.custom_dict['environ'] = environ

    try: # To Build/Validate/Execute CPAC commands
        args.build(context)
        args.validate(context)
        args.execute(context)
        os.sys.exit(0)
    
    except Exception as e:
        context.log.fatal(e)
        context.log.fatal('The Pipeline Failed.')
        if context.config['save-on-error']:
            results.cleanup(context)
        os.sys.exit(1)

    finally:
        ###########################################################################
        # Clean-up and output prep
        results.cleanup(context)
        
