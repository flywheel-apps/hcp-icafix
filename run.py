#!/usr/bin/env python3
import os, os.path as op
import json
import subprocess as sp
import copy
import shutil
import logging

import flywheel
from utils.args.Common import set_subject
from utils.custom_logger import get_custom_logger, log_config
from utils.args import PreFreeSurfer, FreeSurfer, PostFreeSurfer
from utils.args import hcpstruct_qc_scenes, hcpstruct_qc_mosaic
from utils.args import PostProcessing
from utils import results, validate_config, misc


# tfMRI:
# rfMRI_REST1_RL + LR
# rfMRI_REST2_RL + LR
# tfMRI_WM_RL + LR
# tfMRI_GAMBLING_RL + LR
# tfMRI_MOTOR_RL + LR
# tfMRI_LANGUAGE_RL + LR
# tfMRI_SOCIAL_RL + LR
# tfMRI_RELATIONAL_RL + LR
# tfMRI_EMOTION_RL + LR
# 7 TASKS, 2 RESTING,  18 SCANS

# 1 HCP pipelines only work with fsl 6
#


##-------- Standard Flywheel Gear Structure --------##
flywheelv0 = "/flywheel/v0"
environ_json = '/tmp/gear_environ.json'




if __name__ == '__main__':

    # Get the Gear Context
    context = flywheel.GearContext()

    # # Activate custom logger
    # context.log = get_custom_logger('[flywheel/hcp-struct]')

    #### Setup logging as per SSE best practices (Thanks Andy!)
    fmt = '%(asctime)s %(levelname)8s %(name)-8s - %(message)s'
    logging.basicConfig(level=context.config['gear-log-level'], format=fmt)

    context.log = logging.getLogger('[flywheel/MSOT-mouse-recon]')

    context.log.info('log level is ' + context.config['gear-log-level'])

    context.log_config()  # not configuring the log but logging the config

    # Validate gear configuration against gear manifest
    try:
        validate_config.validate_config_against_manifest(context)
    except Exception as e:
        context.log.fatal(e,)
        context.log.fatal(
            'Please make the prescribed corrections and try again.'
        )
        os.sys.exit(1)

    # Set up Custom Dicionary to host user variables
    context.custom_dict={}
    context.custom_dict['SCRIPT_DIR']    = '/tmp/scripts'
    context.custom_dict['SCENE_DIR']     = '/tmp/scenes'
    context.custom_dict['HCP_DIR']       = '/flywheel/v0/hcp_dir'
    # Can I automate this? Do I want to?
    context.custom_dict['FreeSurfer_Version'] = '5.3.0'
    # Instantiate Environment Variables
    # This will always be '/tmp/gear_environ.json' with these
    # environments defined in the Dockerfile and exported from there.
    with open('/tmp/gear_environ.json', 'r') as f:
        misc.set_environment(f,)
        environ = fu.set_environment(environ_json, gear_context.log)

    context.custom_dict['environ'] = environ
    # Create a 'dry run' flag for debugging
    context.custom_dict['dry-run'] = context.config['Dry-Run']

    ###########################################################################
    # Pipelines common commands
    QUEUE = ""
    LogFileDirFull = op.join(context.work_dir, 'logs')
    os.makedirs(LogFileDirFull, exist_ok=True)
    FSLSUBOPTIONS = "-l " + LogFileDirFull

    command_common = [op.join(environ['FSLDIR'], 'bin', 'fsl_sub'),
                      QUEUE, FSLSUBOPTIONS]

    context.custom_dict['command_common'] = command_common

    ###########################################################################
    # Build and Validate parameters for all stages of the pipeline before
    # attempting to execute. Correct parameters or gracefully recover where
    # possible.
    ###########################################################################
    # Ensure the subject_id is set in a valid manner (api or config)

    try:
        set_subject(context)
    except Exception as e:
        context.log.fatal(e, )
        context.log.fatal(
            'The Subject ID is not valid. Examine and try again.',
        )
        os.sys.exit(1)

    # Report on Inputs and configuration parameters to the log
    log_config(context)

    # Build and Validate Parameters for the PreFreeSurferPipeline.sh
    try:
        PreFreeSurfer.build(context)
        PreFreeSurfer.validate(context)
    except Exception as e:
        context.log.fatal(e, )
        context.log.fatal(
            'Validating Parameters for the PreFreeSurferPipeline Failed.',
        )
        os.sys.exit(1)

    ###########################################################################
    # Build and Validate Parameters for the FreeSurferPipeline.sh
    try:
        FreeSurfer.build(context)
        # These parameters need to be validated after the PreFS run
        # No user-submitted parameters to validate at this level
        # FreeSurfer.validate(context)
    except Exception as e:
        context.log.fatal(e)
        context.log.fatal(
            'Validating Parameters for the FreeSurferPipeline Failed.'
        )
        os.sys.exit(1)

        results.cleanup(context)
        
