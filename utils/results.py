"""
This module ecapsulates functionality that is used in preparing and saving the
output of a gear. Some reorganization may make it more "universal"
"""
import os, os.path as op
import json
import subprocess as sp
from zipfile import ZipFile, ZIP_DEFLATED
import shutil
import glob
import logging

log = logging.getLogger(__name__)

# ################################################################################
# # Clean-up and prepare outputs

def save_config(context):
    """
    save_config Uses the 'output_config' and 'output_config_filename' ecapsulated in the 
    gear_dict to save selected values from the gear config to the working 
    directory of the gear (/flywheel/v0/work).

    
    Args:
        context (flywheel.gear_context.GearContext): The gear context object 
            containing the 'gear_dict' dictionary attribute with keys/values,
            'output_config': A configuration dictionary created for downstream 
                gears in the HCP pipeline
            'output_config_filename': The absolute filepath to use for the above 
    """
    config = context.gear_dict['output_config'],
    config_filename = context.gear_dict['output_config_filename']
    with open(config_filename,'w') as f:
        json.dump(config, f, indent=4)

def preserve_whitelist_files(context):
    """
    preserve_whitelist_files Copies the files listed in the 'whitelist' gear_dict key directly to the
    output directory.  These files are to be presented directly to the user
    as well as compressed into the output zipfile.
    
    Args:
        context (flywheel.gear_context.GearContext): The gear context object 
            containing the 'gear_dict' dictionary attribute with keys/values,
            'whitelist': a list of working directory files to place directly in 
                the output directory
            'dry-run': a boolean parameter indicating whether or not to perform 
            this under a 'dry-run' scenario
    """    

    for fl in context.gear_dict['whitelist']:
        if not context.gear_dict['dry-run']:
            log.info('Copying file to output: {}'.format(fl))
            shutil.copy(fl,context.output_dir)

def zip_output(context):
    """
    zip_output Compresses the complete output of the gear (in /flywheel/v0/workdir/<Subject>)
    and places it in the output directory to be catalogued by the application.  
    Only compresses files if 'dry-run' is set to False.
    
    Args:
        context (flywheel.gear_context.GearContext): The gear context object 
            containing the 'gear_dict' dictionary attribute with keys/values,
            'dry-run': Boolean key indicating whether to actually compress or not
            'output_zip_name': output zip file to host the output
            'exclude_from_output': files to exclude from the output 
            (e.g. hcp-struct files)
    """    

    config = context.config

    outputzipname = context.gear_dict['output_zip_name']

    if 'exclude_from_output' in context.gear_dict.keys():
        exclude_from_output = context.gear_dict['exclude_from_output']
    else:
        exclude_from_output = []

    log.info('Zipping output file {}'.format(outputzipname))
    if not context.gear_dict['dry-run']:
        try:
            os.remove(outputzipname)
        except:
            pass

        os.chdir(context.work_dir)
        outzip = ZipFile(outputzipname, 'w', ZIP_DEFLATED)
        for root, _, files in os.walk(config['Subject']):
            for fl in files:
                fl_path = op.join(root,fl)
                # only if the file is not to be excluded from output
                if fl_path not in exclude_from_output:
                    outzip.write(fl_path)
        outzip.close()

def zip_pipeline_logs(context):
    """
    zip_pipeline_logs Compresses files in 
    '/flywheel/v0/work/logs' to '/flywheel/v0/output/pipeline_logs.zip'
    
    Args:
        context (flywheel.gear_context.GearContext): A gear context object 
            leveraged for the location of the "working" and "output" 
            directories of the log files. 
    """
    
    # zip pipeline logs
    logzipname=op.join(context.output_dir, 'pipeline_logs.zip')
    log.info('Zipping pipeline logs to {}'.format(logzipname))
    
    try:
        os.remove(logzipname)
    except:
        pass

    os.chdir(context.work_dir)
    logzipfile = ZipFile(logzipname, 'w', ZIP_DEFLATED)
    for root, _, files in os.walk('logs'):
        for fl in files:
            logzipfile.write(os.path.join(root, fl))

def export_metadata(context):
    """
    export_metadata  If metadata exists (in gear_dict) for this gear write to the application.
    The flywheel sdk is used to write the metadata to the destination/analysis
    object. Another manner to commit this information to the application database
    is to write the dictionary to a '.metadata' file in /flywheel/v0/output.
    
    Args:
        context (flywheel.gear_context.GearContext): The gear context object 
            containing the 'gear_dict' dictionary attribute with keys/values,
            'metadata': key that was initialized in 
            utils.args.PostProcessing.{build,set_metadata_from_csv}.  If the 
            'analysis' subkey is not present, this is an indicator that 
            PostProcessing was not executed.
    """    
   
    # Write Metadata to Analysis Object
    if 'analysis' in context.gear_dict['metadata'].keys():
        info = context.gear_dict['metadata']['analysis']['info']
        # if this metadata is not empty
        if len(info.keys())>0:
            ## TODO: The below is a work around until we get the .metadata.json 
            ## file functionality working
            # Initialize the flywheel client
            fw = context.client
            analysis_id = context.destination['id']
            # Update metadata
            analysis_object = fw.get(analysis_id)
            analysis_object.update_info(info)
    else:
        log.warn('PostProcessing has not been executed!')


def cleanup(context):
    """
    cleanup is used to complete all of the functions in 'results' and offer a simple interface
    for the main script to do so.
    
    Args:
        context (flywheel.gear_context.GearContext): The gear context object 
            containing the 'gear_dict' dictionary attribute with keys/values 
            utilized in the called helper functions.
    """    

    # Move all images to output directory
    png_files = glob.glob(context.work_dir+'/*.png ')
    for fl in png_files:
        shutil.copy(fl, context.output_dir + '/')

    save_config(context)
    zip_output(context)
    zip_pipeline_logs(context)
    preserve_whitelist_files(context)
    export_metadata(context)
    # List final directory to log
    log.info('Final output directory listing: \n')
    os.chdir(context.output_dir)
    duResults = sp.Popen(
        'du -hs *', 
        shell=True, 
        stdout=sp.PIPE, 
        stderr=sp.PIPE,
        universal_newlines=True
    )
    stdout, _ = duResults.communicate()
    log.info('\n' + stdout)           