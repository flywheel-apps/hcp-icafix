"""Main module."""

import logging
import os
import os.path as op
import pathlib
import subprocess as sp
import sys
import re
import shutil
from collections import OrderedDict
from zipfile import ZIP_DEFLATED, ZipFile

from flywheel_gear_toolkit import GearToolkitContext
from flywheel_gear_toolkit.interfaces.command_line import (
    build_command_list,
    exec_command,
)

log = logging.getLogger(__name__)


def run(gear_args):
    """Main script to launch hcp_fix using configuration set by user and zip results for storage.

    Returns:
        file: hcpfix_results.zip
    """
    log.info("This is the beginning of the run file")

    # pull list of func files for analysis (at this time only setup for single run mode **not multirun**)
    try:
        funcfiles = check_input_files(gear_args.work_dir, gear_args.hcpfunc_zipfile)
    except Exception as e:
        log.exception(e)
        log.fatal('Unable to locate correct functional file')
        sys.exit(1)

    # add a loop here**
    for f in funcfiles:
        # generate the hcp_fix command options from gear contex
        generate_ica_command(f, gear_args)

        # execute hcp_fix command (inside this method checks for gear-dry-run)
        execute(gear_args)

    # cleanup gear and store outputs and logs...
    cleanup(gear_args)

    return 0


def check_input_files(workdir, zip_files):
    # Look for tasks in HCP preprocessed file list
    taskdirs = sp.Popen(
        "ls -d " + workdir.absolute().as_posix() + "/*/MNINonLinear/Results/*task*", shell=True, stdout=sp.PIPE,
        stderr=sp.PIPE, universal_newlines=True
    )

    stdout, _ = taskdirs.communicate()
    log.info("Running HCP Fix for the following directories: ")
    log.info("\n %s", stdout)

    # quick manipulation to pull the task name (same as preprocessed image name)
    matches = []
    for f in stdout.splitlines():
        pp = f.split('/')
        pp.append(pp[-1])
        matches.append("/" + os.path.join(*pp) + ".nii.gz")

    return matches


def generate_ica_command(input_file, context):
    training_file = context.config['TrainingFile']
    highpass = context.config['HighPassFilter']
    mot_reg = context.config['do_motion_regression']
    fix_threshold = context.config['FixThreshold']
    del_intermediates = context.config['DeleteIntermediates']

    context.icafix["params"] = OrderedDict(
        [('input', input_file), ('highpass', highpass), ('mot_reg', str(mot_reg).upper()),
         ('training_file', training_file), ('fix_threshold', fix_threshold),
         ('del_intermediate', str(del_intermediates).upper())])


def execute(gear_args):
    command = []
    command.append(gear_args.icafix["common_command"])
    command = build_command_list(command, gear_args.icafix["params"], include_keys=False)

    stdout_msg = (
            "hcp_fix logs (stdout, stderr) will be available "
            + 'in the file "pipeline_logs.zip" upon completion.'
    )
    if gear_args.config["dry-run"]:
        log.info("hcp_fix command:\n{command}")
    try:
        stdout, stderr, returncode = exec_command(
            command,
            dry_run=gear_args.config["dry-run"],
            environ=gear_args.environ,
            stdout_msg=stdout_msg,
        )
        if "error" in stderr.lower() or returncode != 0:
            gear_args["errors"].append(
                {"message": "hcp_fix failed. Check log", "exception": stderr}
            )
    except Exception as e:
        if gear_args.config["dry_run"]:
            # Error thrown due to non-iterable stdout, stderr, returncode
            pass
        else:
            log.exception(e)
            log.fatal('Unable to run hcp_fix')
            sys.exit(1)


def cleanup(gear_args: GearToolkitContext):
    """
    Execute a series of steps to store outputs on the proper containers.

    Args:
        gear_args: The gear context object
            containing the 'gear_dict' dictionary attribute with keys/values
            utilized in the called helper functions.
    """
    # look for output files...
    # Following HCP directory structure, input fMRI should be preprocessed and in the MNINonLinear/Results directory
    # Look for tasks in HCP preprocessed file list
    searchfiles = sp.Popen(
        "cd " + gear_args.work_dir.absolute().as_posix() + "; ls -d  */MNINonLinear/Results/*task*/*task*clean*", shell=True,
        stdout=sp.PIPE,
        stderr=sp.PIPE, universal_newlines=True
    )
    stdout, _ = searchfiles.communicate()

    # quick manipulation to pull the task name (same as preprocessed image name)
    outfiles = []
    for f in stdout.splitlines():
        outfiles.append(f)

    # check if intermediate files should be saved (recommended)
    if not gear_args.config["DeleteIntermediates"]:
        # add the ica folders to zipped output...
        searchfiles = sp.Popen(
            "cd " + gear_args.work_dir.absolute().as_posix() + "; ls -d */MNINonLinear/Results/*task*/*task*.ica", shell=True,
            stdout=sp.PIPE,
            stderr=sp.PIPE, universal_newlines=True
        )
        stdout, _ = searchfiles.communicate()

        # quick manipulation to pull the task name (same as preprocessed image name)
        for f in stdout.splitlines():
            outfiles.append(f)
    newline = "\n"
    log.info("The following output files will be saved: \n %s", newline.join(outfiles))

    # zip output files
    os.chdir(gear_args.work_dir)
    output_zipname = gear_args.outputs_dir.absolute().as_posix() + "/hcpfix_results.zip"
    outzip = ZipFile(output_zipname, "w", ZIP_DEFLATED)

    for fl in outfiles:
        if os.path.isdir(fl):
            for root, _, files in os.walk(fl):
                for ff in files:
                    ff_path = op.join(root, ff)
                    outzip.write(ff_path)
        else:
            outzip.write(fl)

    outzip.close()

    # log final results size
    os.chdir(gear_args.outputs_dir)
    duResults = sp.Popen(
        "du -hs *", shell=True, stdout=sp.PIPE, stderr=sp.PIPE, universal_newlines=True
    )
    stdout, _ = duResults.communicate()
    log.info("\n %s", stdout)

    return 0
