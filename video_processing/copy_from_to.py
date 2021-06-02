import pathlib
import os
import glob
import shutil
import subprocess


class CopyFromTo:

    @staticmethod
    def execute(path_in, path_out, file_pattern):
        files = pathlib.Path(path_in).rglob(file_pattern)
        print(files)
        for file in files:
            start_index = file.parts.index("BIORIDIC_PROCESSED_BP")
            path = os.path.join(path_out, *file.parts[start_index+1:])
            print("cp {} {}".format(file, path))
            print(subprocess.call('cp "{}" "{}"'.format(file, path), shell=True))


if __name__ == "__main__":
    CopyFromTo.execute("/media/brani/DATA/BIORIDIC_PROCESSED_BP", "/media/brani/DATA/BIORIDIC_PROCESSED", "eyetracker_positions.csv")
    # CopyFromTo.execute("/media/brani/DATA/BIORIDIC_PROCESSED_BP", "/run/user/1000/gvfs/smb-share:server=nas2.ubmi.feec.vutbr.cz,share=svozilova/BIORIDIC_PROCESSED/", "eyetracker_positions.csv")