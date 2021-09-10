"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.  

SPDX-License-Identifier: CC-BY-NC-4.0
"""

import sys
import os
from os import path as osp

# initialize recursion
current_folder = osp.dirname(osp.abspath(__file__))
folder_list = [current_folder]

# BF
while len(folder_list) > 0:
    folder = folder_list.pop(0)
    sys.path.append(folder)
    for fn in os.listdir(folder):
        fp = osp.join(folder, fn)
        if (fn not in (".ipynb_checkpoints", "__pycache__")) and (osp.isdir(fp)):
            folder_list.append(fp)
