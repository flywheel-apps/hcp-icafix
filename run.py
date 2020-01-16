#!/usr/bin/env python3
import os
import json
import pathlib
import numpy as np
import flywheel

import logging

# #### Setup logging as per SSE best practices
# try:
# 
#     FORMAT = "[ %(asctime)8s%(levelname)8s%(filename)s:%(lineno)s - %(funcName)8s() ] %(message)s"
#     logging.basicConfig(format=FORMAT)
#     log = logging.getLogger()
# except Exception as e:
#     raise Exception("Error Setting up logger") from e

##-------- Standard Flywheel Gear Structure --------##
flywheelv0 = "/flywheel/v0"
environ_json = '/tmp/gear_environ.json'

#### Setup logging as per SSE best practices
try:

    FORMAT = "[ %(asctime)5s%(levelname)10s%(pathname)5s:%(lineno)s - %(funcName)8s() ] %(message)s"
    logging.basicConfig(format=FORMAT)
    log = logging.getLogger(__name__)
except Exception as e:
    raise Exception("Error Setting up logger") from e

from utils import gear_preliminaries as gp
from utils import gear_toolkit_command_line as gtkcl
from collections import OrderedDict
from utils import results
import re

def set_environment(environment):
    """sets the environment
     
     Sets the environment based on key-value pairs present in the dictionary "environment"

    Args:
        environment (dict): the environment in a key-value pair format


    """

    # Set the current environment using the keys.  This will automatically be used with any sp.run() calls,
    # without the need to pass in env=...  Passing env= will unset all these variables, so don't use it if you do it
    # this way.
    log('Setting Environment:')
    for key in environment.keys():
        log('{}: {}'.format(key, environment[key]))
        os.environ[key] = environment[key]


def get_environment():
    """ Loads environment variables
    
    Loads environment variables saved in a .json file in the Docker container.
    
    Returns:
        environ (dict): the environment variables in a key-value pair dictionary
    """
    # If it exists, read the file in as a python dict with json.load
    with open(environ_json, 'r') as f:
        log.info('Loading gear environment')
        environ = json.load(f)

    return (environ)


def setup_icafix_environment():
    """Sets up the ICAFIX environment
    
    Args: 

    Returns:
        environment_dict: (dict) a key-value pair dictionary of environment variables and their values.

    """
    # Set up Custom Dicionary to host user variables
    environment_dict = get_environment()
    environment_dict['HCP_DIR'] = '/flywheel/v0/hcp_dir'
    environment_dict['SCRIPT_DIR'] = '/flywheel/v0/scripts/scripts'
    environment_dict['SCENE_DIR'] = '/flywheel/v0/scripts/PostFixScenes'
    environment_dict['HCP_PIPELINE_DIR'] = '/opt/HCP-Pipelines'
    mcr = 'v93'
    environment_dict['LD_LIBRARY_PATH'] = \
        '/opt/mcr/{0}/runtime/glnxa64:/opt/mcr/{0}/bin/glnxa64:/opt/mcr/{0}/sys/os/glnxa64:/opt/mcr/{0}/extern/bin/glnxa64:$LD_LIBRARY_PATH'.format(
            mcr)
    environment_dict['MATLAB_COMPILER_RUNTIME'] = '/opt/mcr/{}'.format(mcr)
    environment_dict['FSL_FIX_MATLAB_MODE'] = '0'
    environment_dict['FSL_FIX_MCRROOT'] = '/opt/mcr/{}'.format(mcr)

    # Set up HCP environment variables
    environment_dict['DEFAULT_ENVIRONMENT_SCRIPT'] = '/flywheel/v0/scripts/SetUpHCPPipeline.sh'
    environment_dict['DEFAULT_RUN_LOCAL'] = 'TRUE'
    environment_dict['DEFAULT_FIXDIR'] = '/opt/fix'
    os.system('. /opt/HCP-Pipelines/Examples/Scripts/SetUpHCPPipeline.sh')
    set_environment(environment_dict)
    return (environment_dict)


def check_input_files(workdir, zip_files):
    # Look for the fMRI file in the specified location
    example = pathlib.Path(zip_files[0])
    base = example.parts[0]

    # Following HCP directory structure, input fMRI should be preprocessed and in the MNINonLinear/Results directory
    rx = '.*MNINonLinear\/Results\/([a-zA-Z0-9_]+)\/.*'

    # Find any paths in the zip files that are in this directory
    locate_match = [bool(re.match(rx, path)) for path in zip_files]
    inds = np.where(locate_match)
    sub_files = np.array(zip_files)[inds]

    # Now take the directory name just after MNINonLinear/Results.  There should only be one functional scan directory
    locate_match = [pathlib.Path(a).parts[3] for a in sub_files]
    matches = np.unique(locate_match)

    # If there's more than one, how do we know which one to do ICA on?  
    if len(matches) > 1:
        log.error('Multiple functional scans found.  For single run HPC-ICAFIX, only provide one functional run')
        # TODO: This can look in the functional config.json settings to look for a scan name
        raise Exception('Multiple functional scans - unable to determine which scan to run on')

    # HCP expects the functional file to have the same name as it's parent directory (MNINonLinear/Results/func_scan/func_scan.nii.gz)
    func_base = matches[0]
    func_file = pathlib.PurePath(base, '/MNINonLinear', '/Results', '/{}'.format(func_base),
                                 '/{}.nii.gz'.format(func_base))

    # If it's not there, you're not following HCP protocols.  This is an HCP gear, it runs on HCP directories, not your
    # Poorly organized garbage.
    if not func_file.as_posix() in zip_files:
        log.error('Unable to locate functional scan: expected file {} missing'.format(func_file))
        raise Exception('Unable to locate expected functional scan {}'.format(func_file))
    
    
    # Return the functional file to work on
    func_file = pathlib.Path(workdir).joinpath(func_file)
    func_name = func_file.parts[-2]
    
    log.info('Working on file {}'.format(func_file))
    return (func_file, func_name)


def generate_ica_call_dict(input_file, context):
    
    training_file = context.config['TrainingFile']
    highpass = context.config['HighPassFilter']
    mot_reg = context.config['do_motion_regression']
    fix_threshold = context.config['FixThreshold']
    del_intermediates = context.config['DeleteIntermediates']

    call_dict = OrderedDict([('input', input_file), ('highpass', highpass), ('mot_reg', mot_reg),
                             ('training_file', training_file), ('fix_threshold', fix_threshold),
                             ('del_intermediate', del_intermediates)])

    return (call_dict)

def generage_postica_call_dict(study_folder, subject, fMRIname, highpass):
    """
    
    Args:
        study_folder (str): Should be the gear working directory, location of the <subject>/MNINonlinear/Results... dir
        subject (str): the folder name where MNINonlinear/Results is stored in (value of <subject> in above example)
        fMRIname (str): the name of the fMRI scan to run postfix.sh on (<subject>/MNINonlinear/Results/<fMRIname>)
        highpass (str): the value of the highpass filter used in the desired FIX run

    Returns:

    """
    
    
    reuse_high_pass = "NO"  # Use YES if running on output from multi-run FIX, otherwise use NO
    dual_scene = '${HCPPIPEDIR}/ICAFIX/PostFixScenes/ICA_Classification_DualScreenTemplate.scene'
    single_scene = '${HCPPIPEDIR}/ICAFIX/PostFixScenes/ICA_Classification_SingleScreenTemplate.scene'    
    matlab_mode = "0"  # Mode=0 compiled Matlab, Mode=1 interpreted Matlab, Mode=2 octave
    
    call_dict = OrderedDict([('study-folder', study_folder), ('subject', subject), ('fmri-name',fMRIname),
                             ('high-pass', highpass), ('template-scene-dual-screen', dual_scene),
                             ('template-scene-single-screen', single_scene), ('reuse-high-pass', reuse_high_pass),
                             ('matlab-run-mode', matlab_mode)])
    
    return(call_dict)


def post_fix_cleanup():
    pass
    

def support_geardict(context, subid, funcname, output_zip_name, exclude_from_output):
    context.gear_dict = {}
    context.gear_dict['output_config'] = context.config
    context.gear_dict['output_config_filename'] = '/flywheel/v0/output/{}_{}_hcpicafix_config.json'.format(subid,funcname)
    context.gear_dict['whitelist'] = []
    context.gear_dict['dry-run'] = False
    context.gear_dict['output_zip_name'] = output_zip_name
    context.gear_dict['exclude_from_output'] = exclude_from_output
    context.gear_dict['metadata'] = {}


def main():
    with flywheel.gear_context.GearContext() as context:

        context.custom_dict = {}

        # Log the config settings
        try:
            context.log_config()  # not configuring the log but logging the config
        except Exception as e:
            log.exception(e)
            log.warning('logging context failed')
            # os.sys.exit(1)

        # Setup the environment
        try:
            environment = setup_icafix_environment()
        except Exception as e:
            log.exception(e)
            log.warning('setting environment failed')

        # Set the subject ID
        try:
            gp.set_subject(context)
        except Exception as e:
            log.exception(e)
            log.warning('setting subject failed')

        # Check the input files
        try:
            struct_zip = context.get_input_path('structural_zip')
            func_zip = context.get_input_path('functional_zip')

            zip_contents = []
            config_files = []

            log.info('Checking structural zip files')
            contents, config = gp.preprocess_hcp_zip(struct_zip)
            zip_contents.extend(contents)
            config_files.append(config_files)

            log.info('Checking functional zip files')
            contents, config = gp.preprocess_hcp_zip(func_zip)
            zip_contents.extend(contents)
            config_files.append(config_files)
        except Exception as e:
            log.exception(e)
            log.fatal('Checking zip files failed')
            os.sys.exit(1)

        # Make sure the correct file is in the zipped archives 
        try:
            work_file, func_name = check_input_files(context.work_dir, zip_contents)
        except Exception as e:
            log.exception(e)
            log.fatal('Unable to locate correct functional file')
            os.sys.exit(1)

        # Unzip the files
        try:
            log.info('Unzipping structural files')
            gp.unzip_hcp(context, struct_zip)
            log.info('Unzipping functional files')
            gp.unzip_hcp(context, func_zip)
        except Exception as e:
            log.exception(e)
            log.fatal('Unzipping HCP scruct and func zips failed')
            os.sys.exit(1)

        # Generate the run command
        try:
            command = [environment['HCPPIPEDIR'] + '/ICAFIX/hcp_fix']
            call_dict = generate_ica_call_dict(work_file, context)
            command = gtkcl.build_command_list(command, call_dict, include_keys=False)
            log.info('The following command will be executed:')
            log.info(' '.join(command))
        except Exception as e:
            log.exception(e)
            log.fatal('Generating command call failed')
            os.sys.exit(1)

        # Execute the run command
        try:
            gtkcl.exec_command(command, env=environment)
        except Exception as e:
            log.exception(e)
            log.fatal('HCP-ICAFIX failed')
            os.sys.exit(1)

        # Generate post-fix scene command
        try:
            command = ['${HCPPIPEDIR}/ICAFIX/PostFix.sh']
            call_dict = generage_postica_call_dict(context.work_dir, context.config['Subject'], func_name,
                                                   context.config['HighPassFilter'])
            command = gtkcl.build_command_list(command, call_dict, include_keys=True)
            log.info('The following command will be executed:')
            log.info(' '.join(command))
        except Exception as e:
            log.exception(e)
            log.error('Generating post-fix command failed')

        # Execute the run command
        try:
            gtkcl.exec_command(command, env=environment)
        except Exception as e:
            log.exception(e)
            log.error('POST-HCP-ICAFIX failed')

        # Set the output zip name
        output_zip_name = pathlib.Path(context.output_dir).joinpath(
            '{}_hcpicafix.zip'.format(context.config['Subject']))

        # Needs to be run to support context.custom_dict bullshit 
        try:
            support_geardict(context, context.config['Subject'], func_name, output_zip_name, zip_contents)
        except Exception as e:
            log.exception(e)
            log.error('Legacy context.custom_dict support failed')
            os.sys.exit(1)

        # Now we can the gear cleanup and file zipping
        try:
            results.cleanup(context)
        except Exception as e:
            log.exception(e)
            log.error('Output file zipping failed')
            os.sys.exit(1)

        log.info('Finished')


if __name__ == '__main__':
    
    main()
    

