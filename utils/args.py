import os, os.path as op
import subprocess as sp
import sys
from collections import OrderedDict
from .Common import BuildCommandList, exec_command

import flywheel

def build(context):
    # use Ordered Dictionary to keep the order created.
    # Default in Python 3.6 onward
    params=OrderedDict()

    context.custom_dict['params'] = params

def validate(context):
    """
    Input: gear context with parameters in context.custom_dict['params']
    Attempts to correct any violations
    Logs warning on what may cause problems
    """
    params = context.custom_dict['params']

def execute(context, dry_run=True):
        # Get Params
        params = context.custom_dict['params']

        commandD = context.custom_dict['commandD']
        environ = context.custom_dict['environ']

        # Build command-line parameters
        command = Build_Command_List(commandD['prefix'], params)

        # Extend with positional arguments
        command.extend(commandD['suffix'])

        # Execute command
        exec_command(context, command)

