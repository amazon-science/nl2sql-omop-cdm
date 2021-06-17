import sys
import os
from os import path as osp

current_folder = osp.dirname(osp.abspath(__file__))
sys.path.append(current_folder)
sys.path.append(osp.join(current_folder, ".."))
