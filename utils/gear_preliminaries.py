import json
from zipfile import ZipFile
import re
import logging
import os, os.path as op
from .custom_logger import get_custom_logger

log = logging.getLogger(__name__)


def initialize_gear(context):
    """
    initialize_gear is used to initialize the gear context 'gear_dict' 
    dictionary with objects that are used by all gears in the HCP-Suite. 
    Environment variables, Manifest, Logging, dry-run.
    
    Args:
        context (flywheel.gear_context.GearContext): The gear context object to
            be initialized
    """

    # This gear will use a "gear_dict" dictionary as a custom-user field 
    # on the gear context.

    # grab environment for gear
    with open('/tmp/gear_environ.json', 'r') as f:
        context.gear_dict['environ'] = json.load(f)

    # grab the manifest for use later
    with open('/flywheel/v0/manifest.json', 'r', errors='ignore') as f:
        context.gear_dict['manifest_json'] = json.load(f)

    # get_Custom_Logger is defined in utils.py
    context.log = get_custom_logger(context)

    context.gear_dict['SCRIPT_DIR'] = '/tmp/scripts'
    context.gear_dict['SCENE_DIR'] = '/tmp/scenes'

    # Set dry-run parameter
    context.gear_dict['dry-run'] = context.config['dry-run']

    context.gear_dict['whitelist'] = []
    context.gear_dict['metadata'] = {}


def set_freesurfer_license(context):
    """
    set_freesurfer_license Sets the freesurfer license.txt file depending 
    on(in order of precedence)
    1) A license string set in the config parameters
    2) A license.txt passed as a file
    3) A license string set in the project metadata
    OR an exception is raised.
    
    Args:
        context (flywheel.gear_context.GearContext): The gear context object
            with the gear configuration to look for inputs/configs and
            containing the 'gear_dict' dictionary attribute with key/value,
            'environ': containing the FREESURFER_HOME variable

    Raises:
        Exception: If FreeSurfer license.txt not created.
    """

    config = context.config
    freesurfer_path = context.gear_dict['environ']['FREESURFER_HOME']
    fw = context.client
    project_id = fw.get_analysis(context.destination.get('id')).parents.project
    project = fw.get_project(project_id)

    license_txt = ''
    # Look for license string
    if config.get('FREESURFER_LICENSE'):
        license_txt = config.get('FREESURFER_LICENSE')
    # Look for license.txt file
    elif context.get_input_path('FreeSurferLicense'):
        with open(context.get_input_path('FreeSurferLicense'), 'r') as f:
            license_txt = f.readlines()
            license_txt = ' '.join(license_txt)
    # Look for license string in project metadata
    elif project.info.get('FREESURFER_LICENSE'):
        license_txt = project.info.get('FREESURFER_LICENSE')
    # If not found, raise descriptive exception
    else:
        raise Exception(
            'FreeSurfer license not set.\n Check submission configuration ' + \
            'or project metadata.'
        )

    with open(op.join(freesurfer_path, 'license.txt'), 'w') as fs_license:
        fs_license.write('\n'.join(license_txt.split()))


def preprocess_hcp_zip(zip_filename):
    """
    preprocess_hcp_zip uses hcp-zip output of previous hcp run to create
    a list of contents and the configuration dictionary of that hcp run
    
    Args:
        zip_filename (string): Absolute path of the zip file to examine
    
    Raises:
        Exception: If the configuration file (config.json) is not found.
    
    Returns:
        tuple: (zip_file_list, config), the list of files contained in the zip 
            file and the configuration dictionary of a previous run.
    """

    # Grab the whole file list from an exported zip,
    # put it in a list to parse through. So these will be the files 
    # that do not get compressed into the gear output.
    # While we are at it, grab the *_config.json and return the file list
    # and gear config.
    # raise an exception if zip file or struct config not found.
    zip_file_list = []
    config = {}
    zf = ZipFile(zip_filename)
    for fl in zf.filelist:
        if not (fl.filename[-1] == '/'):  # not (fl.is_dir()):
            zip_file_list.append(fl.filename)
            # grab exported hcp config
            if '_config.json' in fl.filename:
                json_str = zf.read(fl.filename).decode()
                config = json.loads(json_str)
                # This corrects for leaving the initial "config" key out
                # of previous gear versions without error
                if isinstance(config, list):
                    config = config[0]

                if 'config' not in config.keys():
                    config = {'config': config}

    if len(config) == 0:
        raise Exception(
            'Could not find a configuration within the ' + \
            'exported zip-file, {}.'.format(zip_filename)
        )

    return zip_file_list, config


def validate_config_against_manifest(context):
    """
    validate_config_against_manifest compares the automatically produced 
    configuration file (config.json) to the contstraints listed in the manifest
    (manifest.json). This adds a layer of redundancy and transparency to that 
    the process in the web-gui and the SDK.
    This function:
    - checks for the existence of required inputs and the file type of all inputs
    - checks for the ranges of values on config parameters
    - checks for the length of arrays submitted
    - prints out a description of all errors found through a raised Exception.
    
    Args:
        context (flywheel.gear_context.GearContext): The gear context object 
            containing the 'gear_dict' dictionary attribute with keys/values,
            'manifest_json': dictionary representation of the manifest.json file
    
    Raises:
        Exception: An Exception object that lists all of the errors encountered
            in its message string.
    """

    c_config = context.config
    manifest = context.gear_dict['manifest_json']
    m_config = manifest['config']
    errors = []
    if 'config' in manifest.keys():
        for key in m_config.keys():
            m_item = m_config[key]
            # Check if config value is optional
            if key not in c_config.keys():
                if 'optional' not in m_item.keys():
                    errors.append(
                        'The config parameter, {}, is not optional.'.format(key)
                    )
                elif not m_item['optional']:
                    errors.append(
                        'The config parameter, {}, is not optional.'.format(key)
                    )
            else:
                c_val = c_config[key]
                if 'maximum' in m_item.keys():
                    if c_val > m_item['maximum']:
                        errors.append(
                            'The value of {}, {}, exceeds '.format(key, c_val) + \
                            'the maximum of {}.'.format(m_item['maximum'])
                        )
                if 'minimum' in m_item.keys():
                    if c_val < m_item['minimum']:
                        errors.append(
                            'The value of {}, {}, is less than '.format(key, c_val) + \
                            'the minimum of {}.'.format(m_item['minimum'])
                        )
                if 'items' in m_item.keys():
                    if 'maxItems' in m_item['items'].keys():
                        maxItems = m_item['items']['maxItems']
                        if len(c_val) > maxItems:
                            errors.append(
                                'The array {} has {} '.format(key, len(c_val)) + \
                                'elements. More than the {} '.format(maxItems) + \
                                'required.'
                            )
                    if 'minItems' in m_item['items'].keys():
                        minItems = m_item['items']['minItems']
                        if len(c_val) > minItems:
                            errors.append(
                                'The array {} has {} '.format(key, len(c_val)) + \
                                'elements. Less than the {} '.format(minItems) + \
                                'required.'
                            )
                if 'enum' in m_item.keys():
                    # This means the value of the config MUST be one of the 
                    # enumerated values.
                    if c_val not in m_item['enum']:
                        errors.append(
                            'The {} configuration value of {} '.format(key, c_val) + \
                            'is not in the list: {}'.format(m_item['enum'])
                        )
    if 'inputs' in manifest.keys():
        c_inputs = context._invocation['inputs']
        m_inputs = manifest['inputs']
        for key in m_inputs.keys():
            # if a manifest input is not in the invocation inputs
            # check if it needs to be
            if key not in c_inputs.keys():
                m_input = m_inputs[key]
                if 'optional' not in m_input.keys():
                    errors.append(
                        'The input, {}, is not optional.'.format(key)
                    )
                elif not m_input['optional']:
                    errors.append(
                        'The input, {}, is not optional.'.format(key)
                    )
            # Or if it is there, check to see if it is the right type
            elif 'type' in m_inputs[key].keys():
                m_f_type = m_inputs[key]['type']['enum'][0]  ##??
                c_f_type = c_inputs[key]['object']['type']
                if m_f_type != c_f_type:
                    errors.append(
                        'The input, {}, '.format(key) + \
                        ' is a "{}" file.'.format(c_f_type) + \
                        ' It needs to be a "{}" file.'.format(m_f_type)
                    )
    if len(errors) > 0:
        raise Exception(
            'Your gear is not configured correctly: \n{}'.format('\n'.join(errors))
        )


def set_subject(context):
    """
    set_subject queries the subject from the current gear configuration,
    the previous hcp-struct gear configuration, or session container (SDK) in
    that order, depending on the failure of the first two.
    Exits ensuring the value of the subject is valid or raises an Exception.
    
    Args:
        context (flywheel.gear_context.GearContext): The gear context object
            with gear configuration attribute that is interrogated.
    Raises:
        Exception: Zero-length subject
        Exception: If the current analysis container does not have a subject
            container as a parent.
    """

    subject = ''
    # Subject in the gear configuration overides everything else
    if 'Subject' in context.config.keys():
        # Correct for non-friendly characters
        subject = re.sub('[^0-9a-zA-Z./]+', '_', context.config['Subject'])
        if len(subject) == 0:
            raise Exception('Cannot have a zero-length subject.')
    # Else, if we have the subject in the hcp-struct config
    elif 'hcp_struct_config' in context.gear_dict.keys():
        if 'Subject' in context.gear_dict['hcp_struct_config']['config'].keys():
            hcp_struct_config = context.gear_dict['hcp_struct_config']['config']
            subject = hcp_struct_config['Subject']
    # Else Use SDK to query subject
    else:
        # Assuming valid client
        fw = context.client
        # Get the analysis destination ID
        dest_id = context.destination['id']
        # Assume that the destination object has "subject" as a parent
        # This will raise an exception otherwise
        dest = fw.get(dest_id)
        if 'subject' in dest.parents:
            subj = fw.get(dest.parents['subject'])
            subject = subj.label
        else:
            raise Exception(
                'The current analysis container does not have a subject ' + \
                'container as a parent.'
            )

    context.config['Subject'] = subject
    log.info('Using {} as Subject ID.'.format(subject))


def unzip_hcp(context, zip_filename):
    """
    unzip_hcp unzips the contents of zipped gear output into the working 
    directory.  All of the files extracted are tracked from the 
    above preprocess_hcp_zip.
    
    Args:
        context (flywheel.gear_context.GearContext): The gear context object
            containing the 'gear_dict' dictionary attribute with key/value,
            'dry-run': boolean to enact a dry run for debugging
            
        zip_filename (string): The file to be unzipped
    """

    hcp_struct_zip = ZipFile(zip_filename, 'r')
    log.info(
        'Unzipping hcp output file, {}'.format(zip_filename)
    )
    if not context.gear_dict['dry-run']:
        hcp_struct_zip.extractall(context.work_dir)
