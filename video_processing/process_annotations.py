import glob
import itertools
import os

import pandas as pd


class AnnotatorProcessor:

    def __init__(self, legend):
        self._legend = legend
        self._data_folders = None
        self._files = None

    @staticmethod
    def _annot_name_to_video_number(annot_name):
        video_number = annot_name.split("/")[2]
        return "den", video_number

    @staticmethod
    def _get_folders(data_path):
        folders = list(next(os.walk(data_path))[1])
        subfolders = [list(map(lambda subfolder: os.path.join(data_path, folder, subfolder), next(
            os.walk(os.path.join(data_path, folder)))[1])) for folder in folders]
        subfolders = list(itertools.chain(*subfolders))
        subsubfolders = [list(map(lambda subsubfolder: os.path.join(subfolder, subsubfolder), next(
            os.walk(subfolder))[1])) for subfolder in subfolders]
        l = filter(lambda x: "den" in x, list(itertools.chain(*subsubfolders)))
        print(list(subsubfolders))
        return list(l)
        
    def _find_name(self, name):
        name = list(filter(lambda x: "/".join(self._annot_name_to_video_number(name)) in x, self._files.keys()))[0]
        return name

    def execute(self, data_path, annotation_path):
        annotations = pd.read_csv(annotation_path, delimiter="\t", names=["video", "time", "utc", "annotation"])
        self._data_folders = self._get_folders(data_path)
        self._files = list(zip(self._data_folders, list(map(lambda x: open(os.path.join(x, "annotation.csv"), "w"), self._data_folders))))
        self._files = {key: value for (key, value) in self._files}
        for _, item in self._files.items():
            item.write("\t".join(["time", "UTC", "annotation"]) + "\n")
        print(self._files)
        for idx in range(annotations.shape[0]):
            line = annotations.iloc[idx, :]
            name = self._find_name(line[0])
            self._files[name].write("\t".join(map(str, line[1:])) + "\n")


if __name__ == "__main__":
    AnnotatorProcessor(None).execute("/media/brani/DATA/BIORIDIC_PROCESSED", "./annotation-edit.txt")
