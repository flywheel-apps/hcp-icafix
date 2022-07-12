import json
import os
import os.path as op
from collections import defaultdict

from flywheel_gear_toolkit import GearToolkitContext

from utils import gear_arg_utils, helper_funcs


class GearArgs:
    def __init__(
        self, gtk_context: GearToolkitContext, env_file=None
    ):
        """
        Sets up the structure of the GearArgs class that will be passed to many of the
        BIDS HCP methods. While parts of the class mimic the GearToolkitContext,
        many of the additional arguments, such as the template locations, are better
        organized and more transparent when placed here. This class should be extended
        to include additional attributes specific to HCP processing as necessary.

        General conceptual layout is that variables (e.g., "Subject") that are used
        across modality are stored in .common. Each main modality, which has its own
        subgear (i.e., "fw_gear_hcp_{modality}" folder), has specific variables for that modality stored
        in the .{modality} attribute.
        .processing defines where the scripts are to be found by the algorithm, when invoked
        from subprocess
        .templates details where the common spaces are to be found, saving repetitive definitions
        within each modality's main.py script
        .fw_specific holds "gear-" prefixed arguments that define behavior for the analysis
        on the platform.

        Args:
            gtk_context: GearContext information.
            env_file: The env variables that are set up during the Docker build stage
            are stored in the json file to keep the paths clear with the introduction
            of poetry. These declarations are essential for any of the subprocess calls to
            work properly.
        """
        # with open(env_file, "r") as f:
        #     self.environ = json.load(f)
        # if env_file loaded use that... otherwise use docker environment
        if env_file:
            with open(env_file, "r") as f:
                self.environ = json.load(f)
        else:
            self.environ = os.environ
        self.templates = defaultdict()
        self.add_templates()
        self.dirs = {
            "work_dir": gtk_context.work_dir,
            "output_dir": gtk_context.output_dir,
            "bids_dir": op.join(gtk_context.work_dir, "bids"),
            "script_dir": "/tmp/scripts",
            "scenes_dir": "/tmp/scenes",
        }
        self.structural = defaultdict()
        # Need a default 'fmri_name', as the value is not set for structural
        # or diffusion processing, but needed for QC processing
        self.functional = {"fmri_name": None}
        self.diffusion = defaultdict()
        self.common = defaultdict()
        # Add the script path for each stage
        self.processing = defaultdict()
        self.add_processing_steps()
        self.fw_specific = {"gear_dry_run": False}
        # Basically, parse the config.json
        self.add_context_info(gtk_context)
        self.run_updates(gtk_context)

    def run_updates(self, gtk_context: GearToolkitContext):
        """
        A few specific fields need to be instantiated with default values to allow the
        gear to progress through the series of subgear methods. This method defines the
        current subject being analysed and the initial processing stage that is requested,
        since not all analyses will begin with FreeSurfer anatomical methods.
        Args:
            gtk_context: Gear information
        Returns:
            Updated class with populated .common attribute
        """
        # Make sure that the Subject label is super clear. Either the individual that
        # the gear was launched from or the subject(s) specified at the project-level launch
        # should be defined here.
        self.common.update(
            {
                "subject": gear_arg_utils.set_subject(gtk_context),
                "current_stage": self.common["stages"].split()[0],
                "exclude_from_output": None,
                "errors": [],
                "safe_list": [],
            }
        )

    def add_templates(self):
        """
        Most of the existing gears rely on the environ variable for HCPPIPEDIR locations.
        This method will replace the need to keep passing the environ variable by adding the
        locations to the gear_args dictionary.
        """
        tmplt_dir = self.environ["HCPPIPEDIR_Templates"]
        for msr in ["0.7mm", "0.8mm", "1mm"]:
            for mod in ["t1", "t2"]:
                tmp = op.join(
                    tmplt_dir, "MNI152_" + mod.upper() + "_" + msr + ".nii.gz"
                )
                if op.isfile(tmp):
                    self.templates[mod + "template" + msr] = tmp
                tmp_brain = op.join(
                    tmplt_dir, "MNI152_" + mod.upper() + "_" + msr + "_brain.nii.gz"
                )
                if op.isfile(tmp_brain):
                    self.templates[mod + "templatebrain" + msr] = tmp_brain
                tmp_brain_mask = op.join(
                    tmplt_dir,
                    "MNI152_" + mod.upper() + "_" + msr + "_brain_mask.nii.gz",
                )
                if op.isfile(tmp_brain_mask):
                    self.templates["templatemask" + msr] = tmp_brain_mask
        self.templates["template2mmmask"] = op.join(
            tmplt_dir, "MNI152_T1_2mm_brain_mask_dil.nii.gz"
        )
        self.templates["fnirt_config"] = op.join(
            self.environ["HCPPIPEDIR_Config"], "T1_2_MNI152_2mm.cnf"
        )
        self.templates["surf_atlas_dir"] = op.join(tmplt_dir, "standard_mesh_atlases")
        self.templates["grayordinates_template"] = op.join(tmplt_dir, "*_Greyordinates")
        self.templates["subcort_gray_labels"] = op.join(
            self.environ["HCPPIPEDIR_Config"], "FreeSurferSubcorticalLabelTableLut.txt"
        )
        self.templates["freesurfer_labels"] = op.join(
            self.environ["HCPPIPEDIR_Config"], "FreeSurferAllLut.txt"
        )
        self.templates["ref_myelin_maps"] = op.join(
            tmplt_dir,
            "standard_mesh_atlases",
            "Conte69.MyelinMap_BC.164k_fs_LR.dscalar.nii",
        )

    def add_processing_steps(self):
        """
        Each of the stages has an official HCP-provided script to
        reference within the HCPPIPEDIR path. Select the correct script
        in a maintainable way, when called by the individual stage's .py
        method.
        Do not change these keys as they are directly tied to how HCP uses
        the names.
        """
        step_dict = {
            "PreFreeSurfer": "PreFreeSurferPipeline.sh",
            "FreeSurfer": "FreeSurferPipeline.sh",
            "PostFreeSurfer": "PostFreeSurferPipeline.sh",
            "fMRIVolume": "GenericfMRIVolumeProcessingPipeline.sh",
            "fMRISurface": "GenericfMRISurfaceProcessingPipeline.sh",
            "DiffusionPreprocessing": "DiffPreprocPipeline.sh",
        }
        for step, script in step_dict.items():
            self.processing[step] = op.join(self.environ["HCPPIPEDIR"], step, script)

        # Set the command that prepends each stage's processing script
        # self.dirs["bids_dir"] is defined, but log redirection is going to \ /flywheel/v0/work/bids
        LogFileDirFull = op.join(self.dirs["work_dir"], "bids", "logs")
        os.makedirs(LogFileDirFull, exist_ok=True)
        self.processing.update(
            {
                "common_command": [
                    op.join(self.environ["FSLDIR"], "bin", "fsl_sub"),
                    "-l",
                    LogFileDirFull,
                ]
            }
        )

        # qc_dict = {}
        # for step, script in step_dict.items():
        #    self.processing = op.join("/tmp/scripts", step, script)

    def add_context_info(self, gtk_context: GearToolkitContext):
        """
        Arguments from the user input/config are sorted based on subscripts on the
        variable names in the manifest. The sorted values are returned to this method
        to be placed into their respective GearArgs attributes, rather than maintaining
        the values as a dictionary.
        Args:
            gtk_context: Gear information. The config and inputs, specifically,
            are sent to be sorted and then added to GearArgs.

        Returns:
            Populated GearArgs attributes.
        """
        org_dict = {
            "struct": "structural",
            "func": "functional",
            "dwi": "diffusion",
            "fw_param": "fw_specific",
        }
        # configs is a nested dictionary
        configs = gear_arg_utils.sort_gear_args(gtk_context.config_json["config"])
        inputs = gear_arg_utils.sort_gear_args(gtk_context.config_json["inputs"])
        for k, v in inputs.items():
            if v:
                configs[k].update(v)
        for category, params in configs.items():
            if category in org_dict.keys():
                attrbt = [v for k, v in org_dict.items() if category == k][0]

                # If the field is already populated, then we need to grab those values, add
                # them to the params, and reset the attrbt to contain the full set of params.
                check = getattr(self, attrbt)
                if check:
                    for k, v in check.items():
                        if k not in params.keys():
                            params.update(check.items())

                # The params should be a dictionary of all parameters for that category
                setattr(self, attrbt, params)
            else:
                if self.common:
                    params.update(self.common.items())
                setattr(self, "common", params)
