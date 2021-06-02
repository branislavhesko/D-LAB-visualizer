

import os
import glob

import pandas as pd
from tqdm import tqdm

path = "/media/brani/DATA/BIORIDIC_PROCESSED"

folders = next(os.walk(path))[1]
not_with = pd.DataFrame([], columns=["date", "time", "ride_id", "annotation", "dist[m]", "utc"])
for folder in tqdm(folders):
    subfolders = next(os.walk(os.path.join(path, folder)))[1]

    for subfolder in subfolders:
        subsubfolders = next(os.walk(os.path.join(path, folder, subfolder)))[1]

        for subsubfolder in subsubfolders:
            p = os.path.join(path, folder, subfolder, subsubfolder)
            annotation_path = os.path.join(p, "infrastructure_annotations.csv")
            if not os.path.isfile(annotation_path):
                continue
            print("Processing annotation: {}".format(annotation_path))
            annotation = pd.read_csv(annotation_path, delimiter="\t")
            annotation_bad = annotation[annotation["dist[m]"] > 15]

            for row in annotation_bad.iterrows():
                not_with = pd.concat([not_with, pd.DataFrame([[folder, subfolder[-3:], subsubfolder, row[1]["mark"], row[1]["dist[m]"], row[1]["utc"]]], columns=["date", "time", "ride_id", "annotation", "dist[m]", "utc"])])

not_with.to_csv("bad_annotations.csv", index=False)