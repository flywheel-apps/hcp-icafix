"""
This module, hosts the functionality for streamline the execution of 
command-line utilities called from the subprocess library.
"""

import os, os.path as op
import subprocess as sp
import re
import logging

log = logging.getLogger(__name__)

def build_command_list(command, ParamList, include_keys=True):
    """
    build_command_list builds a list to be used by subprocess.Popen with the 
    ParamList providing key/value pairs for command-line parameters.
    ParamList is a dictionary of key:value pairs to be put into the command 
    list as such 
    
    Args:
        command (list): A list containing the base command (e.g. ['ls']) with 
            parameters that are always used.

        ParamList (dict): An dictionary (usually ordered) of key/value pairs
            representing command-line parameters/switches for the command in 
            question. Results in ("-k value" or "--key=value")
            
        include_keys (bool, optional): A flag to indicate whether or not to 
            include the keys in the command list. Defaults to True.
    
    Returns:
        list: returns the completed command-list expected by subprocess.Popen
    """     

    for key in ParamList.keys():
        # Single character command-line parameters are preceded by a single '-'
        if len(key) == 1:
            if include_keys:
                command.append('-' + key)
            if len(str(ParamList[key]))!=0:
                command.append(str(ParamList[key]))
        # Multi-Character command-line parameters are preceded by a double '--'
        else:
            # If Param is boolean and true include, else exclude
            if type(ParamList[key]) == bool:
                if ParamList[key] and include_keys:
                    command.append('--' + key)
            else:
                # If Param not boolean, but without value include without value
                # (e.g. '--key'), else include value (e.g. '--key=value')
                item = ""
                if include_keys:
                    item='--' + key
                if len(str(ParamList[key])) > 0:
                    if include_keys:
                        item = item + "="
                    item = item + str(ParamList[key])
                command.append(item)
    return command


def exec_command(command, dry_run=False, environ={}, shell=False,
                 stdout_msg=None, cont_output=False):
    """
    exec_command is a generic abstraction to execute shell commands using the 
    subprocess module.
    
    Args:
        command (list): list of command-line parameters, starting with the 
            command to run

        dry_run (bool, optional): a boolean flag to indicate a dry-run without 
            executing anythingj. Defaults to False

        environ (dict, optional): a dictionary of key/value pairs representing
            the environment variables necessary for running the command-line
            utility. Defaults to an empty dictionary {}.

        shell (bool, optional): whether or not to execute as a single 
            shell string. This facilitates output redirects. Defaults to False.

        stdout_msg (string, optional): A string to notify the user where the
            stdout/stderr has been redirected to. Defaults to None.

        cont_output (bool, optional): Used to provide continuous output of 
            stdout without waiting until the completion of the shell command. 
            Defaults to False.
    
    Raises:
        Exception: If the return value from the command-line function is not
            zero, return an Exception with the message from the returned stderr.
    """

    log.info('Executing command: \n' + ' '.join(command)+'\n\n')
    if not dry_run:
        # The 'shell' parameter is needed for bash output redirects 
        # (e.g. >,>>,&>)
        if shell:
            run_command = ' '.join(command)
        else:
            run_command = command

        result = sp.Popen(run_command, stdout=sp.PIPE, stderr=sp.PIPE,
                        universal_newlines=True, env=environ, shell=shell)

        # log that we are using an alternate stdout message
        if stdout_msg!=None:
            log.info(stdout_msg)

        # if continuous stdout is desired... and we are not redirecting output
        if cont_output and not (shell and ('>' in command)) \
            and (stdout_msg==None):
            while True:
                stdout = result.stdout.readline()
                if stdout == '' and result.poll() is not None:
                    break
                if stdout:
                    log.info(stdout)
            returncode = result.poll()
            
        else:
            stdout, stderr = result.communicate()
            returncode = result.returncode
            if stdout_msg==None:
                log.info(stdout)

        log.info('Command return code: {}'.format(returncode))

        if result.returncode != 0:
            log.error('The command:\n ' +
                              ' '.join(command) +
                              '\nfailed.')
            raise Exception(stderr)