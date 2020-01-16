"""
This is a module with specific functions for the HCP Diffusion pipeline
"""
import os, os.path as op
import glob

def configs_to_export(context):
    """
    configs_to_export exports HCP Diffusion Pipeline configuration into the 
    Subject directory
    
    Args:
        context (flywheel.gear_context.GearContext): The gear context object 
    
    Returns:
        tuple: (hcpdiff_config, hcpdiff_config_filename), The created config 
            object and the intended filename for export.
    """    

    config = {}
    hcpdiff_config={'config': config}
    for key in [
        'RegName',
        'Subject',
        'DWIName'
    ]:
        if key in context.config.keys():
            config[key]=context.config[key]
    
    hcpdiff_config_filename = op.join(
            context.work_dir,context.config['Subject'],
            '{}_{}_hcpfunc_config.json'.format(
                context.config['Subject'],
                context.config['DWIName']
            )
    )

    return hcpdiff_config, hcpdiff_config_filename

def make_sym_link(src, dest):
    """
    make_sym_link Make a symbolic link, if 'src' exists.  Do nothing, otherwise.
    
    Args:
        src (string): full path of the source file
        dest (string): full path of the destination symbolic link
    """    

    if src:
        os.symlink(src, dest)