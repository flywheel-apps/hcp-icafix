import os, os.path as op
import subprocess as sp

def BuildCommandList(command, ParamList):
    """
    command is a list of prepared commands
    ParamList is a dictionary of key:value pairs to be put into the command list as such ("-k value" or "--key=value")
    """
    for key in ParamList.keys():
        # Single character command-line parameters are preceded by a single '-'
        if len(key) == 1:
            command.append('-' + key)
            if len(str(ParamList[key]))!=0:
                command.append(str(ParamList[key]))
        # Multi-Character command-line parameters are preceded by a double '--'
        else:
            # If Param is boolean and true include, else exclude
            if type(ParamList[key]) == bool:
                if ParamList[key]:
                    command.append('--' + key)
            else:
                # If Param not boolean, but without value include without value
                # (e.g. '--key'), else include value (e.g. '--key=value')
                if len(str(ParamList[key])) == 0:
                    command.append('--' + key)
                else:
                    command.append('--' + key + '=' + str(ParamList[key]))
    return command

def exec_command(context,command,shell=False,stdout_msg=None):
    environ = context.custom_dict['environ']
    context.log.info('Executing command: \n' + ' '.join(command)+'\n\n')
    if not context.custom_dict['dry-run']:
        # The 'shell' parameter is needed for bash output redirects 
        # (e.g. >,>>,&>)
        if shell:
            command = ' '.join(command)
        result = sp.Popen(command, stdout=sp.PIPE, stderr=sp.PIPE,
                        universal_newlines=True, env=environ, shell=shell)

        stdout, stderr = result.communicate()
        context.log.info('Command return code: {}'.format(result.returncode))

        if stdout_msg==None:
            context.log.info(stdout)
        else:
            context.log.info(stdout_msg)

        if result.returncode != 0:
            context.log.error('The command:\n ' +
                              ' '.join(command) +
                              '\nfailed.')
            raise Exception(stderr)