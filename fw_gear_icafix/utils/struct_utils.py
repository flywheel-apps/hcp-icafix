"""
This is a module with specific functions for the HCP Functional Pipeline
"""
import subprocess as sp
import os, os.path as op

def get_freesurfer_version(context):
    """
    get_freesurfer_version returns the version of freesurfer used.
    This is need to determine which HCP/FreeSurfer.sh to run. Unless otherwise,
    we are using the latest version.
    
    Args:
        context (flywheel.gear_context.GearContext): The gear context object
            containing the stored environment in gear_dict['environ']
    
    Returns:
        string: The version of Freesurfer(e.g. 6.0.1)
    """    

    environ = context.gear_dict['environ']
    command = ['freesurfer --version']
    result = sp.Popen(
        command, 
        stdout=sp.PIPE, 
        stderr=sp.PIPE, 
        universal_newlines=True, 
        shell=True,
        env=environ
    )
    stdout, _ = result.communicate()
    start = stdout.find('-v') + 2
    end = stdout.find('-',start)
    version = stdout[start:end]
    return version

def configs_to_export(context):
    """
    configs_to_export exports HCP Functional Pipeline configuration into the 
    Subject directory. The 'RegName', 'Subject', 'GrayordinatesResolution', 
    'GrayordinatesTemplate', 'HighResMesh', 'LowResMesh' configuration 
    parameters are recorded in a dictionary.
    
    Args:
        context (flywheel.gear_context.GearContext): The gear context object 
    
    Returns:
        tuple: (hcpstruct_config, hcpstruct_config_filename), the created config
            object and the intended filename for export.
    """    

    config = {}
    hcpstruct_config={'config': config}
    for key in [
        'RegName',
        'Subject',
        'GrayordinatesResolution',
        'GrayordinatesTemplate',
        'HighResMesh',
        'LowResMesh'
    ]:
        if key in context.config.keys():
            config[key]=context.config[key]

    hcpstruct_config_filename = op.join(
        context.work_dir,
        context.config['Subject'],
        '{}_hcpstruct_config.json'.format(context.config['Subject'])
    )
    
    return hcpstruct_config, hcpstruct_config_filename