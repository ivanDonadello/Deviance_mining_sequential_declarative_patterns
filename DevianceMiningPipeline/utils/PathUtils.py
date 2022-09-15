"""
Utility functions for path operations

@author: Giacomo Bergami
"""

import os
from pathlib import Path
from DevianceMiningPipeline.utils import FileNameUtils


def mkdir_test(dest1):
    Path(dest1).mkdir(parents=True, exist_ok=True)

def move_files(inp_folder, output_folder, split_nr, base):
    source = inp_folder
    dest1 = FileNameUtils.embedding_path(split_nr - 1, output_folder, base)
    files = os.listdir(source)
    for f in files:
        dstFile = os.path.join(dest1, f)
        if (os.path.exists(dstFile)): os.remove(dstFile)
        print("moving "+os.path.join(source, f)+" to "+dstFile+"...")
        os.rename(os.path.join(source, f), dstFile)
    return dest1