"""Parser module to parse gear config.json."""
from typing import Tuple
from zipfile import ZipFile
from flywheel_gear_toolkit import GearToolkitContext
import os
import logging
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

        # setup enviornment for python system commands
        if env_file:
            with open(env_file, "r") as f:
                self.environ = json.load(f)
        else:
            self.environ = os.environ

        # pull input filepaths
        self.debug = gtk_context.config.get("debug")
        self.fslicense = gtk_context.config_json["inputs"].get("freesurfer_license")
        self.hcpfunc_zipfile = gtk_context.get_input_path("hcpfunc_zip")
        self.hcpstruct_zipfile = gtk_context.get_input_path("hcpstruct_zip")

        # pull config settings
        self.options = gtk_context.config
        self.gtk_context = gtk_context
        self.work_dir = gtk_context.work_dir

        # unzip HCPpipeline files
        self.unzip_hcp(self.hcpstruct_zipfile)
        self.unzip_hcp(self.hcpfunc_zipfile)

        # with open(
        #     gtk_context.get_input_path("freesurfer_license"), "r", encoding="utf8"
        # ) as text_file:
        #     self.fslicense_text = " ".join(text_file.readlines())





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
        if not self.options.get("gear_dry_run"):
            hcp_zip.extractall(self.work_dir)
            log.debug(f'Unzipped the file to {self.work_dir}')