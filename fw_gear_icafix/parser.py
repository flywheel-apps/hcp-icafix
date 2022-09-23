"""Parser module to parse gear config.json."""
from typing import Tuple
from zipfile import ZipFile
from flywheel_gear_toolkit import GearToolkitContext
import os
import logging
from pathlib import Path
log = logging.getLogger(__name__)

# This function mainly parses gear_context's config.json file and returns relevant
# inputs and options.
class GearArgs:
    def __init__(
        self, gtk_context: GearToolkitContext, env_file=None
    ):
        """[Summary]

        Returns:
            [type]: [description]
        """

        # setup enviornment for python system commands - all enviornment variables should be
        #    defined in the manifest and attached to the docker image via flywheel engine
        #    if a static ENV is desired, an env file can be generated and attached to project
        if env_file:
            with open(env_file, "r") as f:
                self.environ = json.load(f)
        else:
            self.environ = os.environ

        # pull input filepaths
        self.debug = gtk_context.config.get("debug")
        self.hcpfunc_zipfile = gtk_context.get_input_path("functional_zip")
        log.info("Inputs file path, %s", self.hcpfunc_zipfile)
        self.hcpstruct_zipfile = gtk_context.get_input_path("structural_zip")
        log.info("Inputs file path, %s", self.hcpstruct_zipfile)

        # pull config settings
        self.icafix = {
            "common_command": "/opt/HCP-Pipelines/ICAFIX/hcp_fix",
            "params": ""
        }
        self.config = gtk_context.config
        self.gtk_context = gtk_context
        self.work_dir = Path("/flywheel/v0/work")
        self.outputs_dir = Path("/flywheel/v0/output")

        # unzip HCPpipeline files
        self.unzip_hcp(self.hcpstruct_zipfile)
        self.unzip_hcp(self.hcpfunc_zipfile)




    def unzip_hcp(self, zip_filename):
        """
        unzip_hcp unzips the contents of zipped gear output into the working
        directory.  All of the files extracted are tracked from the
        above process_hcp_zip.
        Args:
            self: The gear context object
                containing the 'gear_dict' dictionary attribute with key/value,
                'dry-run': boolean to enact a dry run for debugging
            zip_filename (string): The file to be unzipped
n        """
        hcp_zip = ZipFile(zip_filename, "r")
        log.info("Unzipping hcp outputs, %s", zip_filename)
        if not self.config.get("dry_run"):
            hcp_zip.extractall(self.work_dir)
            log.debug(f'Unzipped the file to {self.work_dir}')