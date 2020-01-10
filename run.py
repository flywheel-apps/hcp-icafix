#!/usr/bin/env python3
import os, os.path as op
import json
import subprocess as sp
import shutil
import logging


import flywheel
from utils.args.Common import set_subject
from utils.custom_logger import get_custom_logger, log_config
from utils.args import hcp_icafix
from utils import results, validate_config, misc
from gear_utils import gear_preliminaries as gp

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
# 2 use xenial vs trusty
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
    # context.custom_dict['SCRIPT_DIR']    = '/tmp/scripts'
    # context.custom_dict['SCENE_DIR']     = '/tmp/scenes'
    context.custom_dict['HCP_DIR']       = '/flywheel/v0/hcp_dir'
    context.custom_dict['SCRIPT_DIR']    = '/flywheel/v0/scripts/scripts'
    context.custom_dict['SCENE_DIR']     = '/flywheel/v0/scripts/PostFixScenes'
    context.custom_dict['HCP_PIPELINE_DIR'] = '/opt/HCP-Pipelines'

    # Can I automate this? Do I want to?
    context.custom_dict['FreeSurfer_Version'] = '5.3.0'
    # Instantiate Environment Variables
    # This will always be '/tmp/gear_environ.json' with these
    # environments defined in the Dockerfile and exported from there.
    os.system('. /opt/HCP-Pipelines/Examples/Scripts/SetUpHCPPipeline.sh')

    # command = ". /opt/HCP-Pipelines/Examples/Scripts/SetUpHCPPipeline.sh && env'".split()
    # proc = sp.Popen(command, stdout=sp.PIPE, shell=True)
    # for line in proc.stdout:
    #     (key, _, value) = line.partition("=")
    #     os.environ[key] = value
    #     print(line)
    # proc.communicate()
    #print(os.environ['MATLAB_COMPILER_RUNTIME'])

    environ = misc.set_environment(environ_json, context.log)
    context.custom_dict['environ'] = environ

    mcr = 'v93'

    environ['LD_LIBRARY_PATH'] = '/opt/mcr/{0}/runtime/glnxa64:/opt/mcr/{0}/bin/glnxa64:/opt/mcr/{0}/sys/os/glnxa64:/opt/mcr/{0}/extern/bin/glnxa64:$LD_LIBRARY_PATH'.format(mcr)
    environ['MATLAB_COMPILER_RUNTIME'] = '/opt/mcr/{}'.format(mcr)
    environ['MY_TEST'] = 'fuck work'
    environ['FSL_FIX_MATLAB_MODE'] = '0'
    environ['FSL_FIX_MCRROOT'] = '/opt/mcr/{}'.format(mcr)

    # Set up HCP environment variables
    os.environ['DEFAULT_ENVIRONMENT_SCRIPT'] = '/flywheel/v0/scripts/SetUpHCPPipeline.sh'
    os.environ['DEFAULT_RUN_LOCAL'] = 'TRUE'
    os.environ['DEFAULT_FIXDIR'] = '/opt/fix'

    # Create a 'dry run' flag for debugging
    context.custom_dict['dry-run'] = context.config['Dry-Run']
    
    
    struct_zip = context.get_input_path('structural_zip')
    func_zip = context.get_input_path('functional_zip')
    
    
    
    cmd='${$HCPPIPEDIR}/ICAFIX/hcp_fix '
  