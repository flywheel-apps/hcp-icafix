import json
import logging
import os.path as op
from pathlib import Path

log = logging.getLogger(__name__)

FWV0 = Path.cwd()


def get_and_log_environment():
    """Grab and log environment to use when executing command lines.

    The shell environment is saved into a file at an appropriate place in the Dockerfile.

    Returns: environ (dict) the shell environment variables
    """

    environment_file = FWV0 / "gear_environ.json"
    log.debug("Grabbing environment from %s", environment_file)

    with open(environment_file, "r") as f:
        environ = json.load(f)

        # Add environment to log if debugging
        kv = ""
        for k, v in environ.items():
            kv += k + "=" + v + " "
        log.debug("Environment: " + kv)

    return environ


def set_freesurfer_license(gtk_context):
    """
    set_freesurfer_license Sets the freesurfer license.txt file depending
    on(in order of precedence)
    1) A license string set in the config parameters
    2) A license.txt passed as a file
    3) A license string set in the project metadata
    OR an exception is raised.
    Args:
        gtk_context (flywheel.gear_context.GearContext): The gtk_context object
            with the gear configuration to look for inputs/configs and
            containing the 'gear_dict' dictionary attribute with key/value,
            'environ': containing the FREESURFER_HOME variable
    Raises:
        Exception: If FreeSurfer license.txt not created.
    """

    config = gtk_context.config
    freesurfer_path = gtk_context.manifest["environment"]["FREESURFER_HOME"]
    fw = gtk_context.client
    project_id = fw.get_analysis(gtk_context.destination.get("id")).parents.project
    project = fw.get_project(project_id)

    license_txt = ""
    # Look for license string
    if config.get("FREESURFER_LICENSE"):
        license_txt = config.get("FREESURFER_LICENSE")
    # Look for license.txt file
    elif gtk_context.get_input_path("FreeSurferLicense"):
        with open(gtk_context.get_input_path("FreeSurferLicense"), "r") as f:
            license_txt = f.readlines()
            license_txt = " ".join(license_txt)
    # Look for license string in project metadata
    elif project.info.get("FREESURFER_LICENSE"):
        license_txt = project.info.get("FREESURFER_LICENSE")
    # If not found, raise descriptive exception
    else:
        log.exception(
            "FreeSurfer license not set.\n Check submission configuration "
            + "or project metadata."
        )

    with open(op.join(freesurfer_path, "license.txt"), "w") as fs_license:
        fs_license.write("\n".join(license_txt.split()))
