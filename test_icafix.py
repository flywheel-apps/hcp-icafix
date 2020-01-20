#!/usr/bin/env python3
import os
from utils import gear_preliminaries as gp

# tfMRI:
# rfMRI_REST1_RL + LR
# rfMRI_REST2_RL + LR
# tfMRI_WM_RL + LR
# tfMRI_GAMBLING_RL + LR
# tfMRI_MOTOR_RL + LR
# tfMRI_LANGUAGE_RL + LR
# tfMRI_SOCIAL_RL + LR
# tfMRI_RELATIONAL_RL + LR
# tfMRI_EMOTION_RL + LR
# 7 TASKS, 2 RESTING,  18 SCANS

# 1 HCP pipelines only work with fsl 6
# 2 use xenial vs trusty
#

struct_zip = '/flywheel/v0/input/TOME_3024_hcpstruct.zip'
func_zip = '/flywheel/v0/input/TOME_3024_rfMRI_REST1_RL_hcpfunc.zip'


class context():
    def __init__(self):
        self.gear_dict={}
        self.work_dir = '/flywheel/v0/work'

cmd='${HCPPIPEDIR}/ICAFIX/hcp_fix /flywheel/v0/work/TOME_3024/MNINonLinear/Results/rfMRI_REST1_RL/rfMRI_REST1_RL.nii.gz 2000 TRUE HCP_hp2000.RData 10'
work_dir = '/flywheel/v0/work'
if not os.path.exists(work_dir):
    os.mkdir(work_dir)
    
zip_file_list, config = gp.preprocess_hcp_zip(struct_zip)
context = context()
context.gear_dict['dry-run'] = False
gp.unzip_hcp(context,struct_zip)
gp.unzip_hcp(context,func_zip)

