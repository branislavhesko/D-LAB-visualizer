import os
import glob

import pandas as pd
from tqdm import tqdm

path = "/media/brani/DATA/BIORIDIC_PROCESSED"

folders = next(os.walk(path))[1]
not_with = []
for folder in tqdm(folders):
    subfolders = next(os.walk(os.path.join(path, folder)))[1]

    for subfolder in subfolders:
        subsubfolders = next(os.walk(os.path.join(path, folder, subfolder)))[1]

        for subsubfolder in subsubfolders:
            p = os.path.join(path, folder, subfolder, subsubfolder)
            print(p)
            can = pd.read_csv(p + "/CAN2.csv")
            if not any(list(map(lambda x: "Dikablis" in x, can.columns))):
                not_with.append(p + "/CAN2.csv")


with open("dikablis_missing.txt", "w") as fp:
    for n in not_with:
        fp.write(n + "\n")