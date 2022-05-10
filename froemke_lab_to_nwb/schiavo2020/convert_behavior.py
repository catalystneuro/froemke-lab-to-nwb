import os
from glob import glob
import datetime
import uuid
from ndx_events import Events
from pynwb import NWBFile, NWBHDF5IO
from pynwb.file import Subject
import pandas as pd
from tqdm import tqdm
import json

from . import SRC_DATA_DIR, DEST_DATA_DIR

BEHAVIOR_DIR = os.path.join(SRC_DATA_DIR, "Behavior files")


def convert_all_behavior(src: str = BEHAVIOR_DIR, dest: str = DEST_DATA_DIR) -> None:
    behavior_files = glob(os.path.join(src, "*.csv"))
    with open(os.path.join(BEHAVIOR_DIR, "metadata.json"), "r") as file:
        json_metadata = json.load(file)

    for behavior_file in tqdm(behavior_files, desc="behavior files"):
        times = pd.read_csv(behavior_file, names=("times",)).values.ravel()
        fname = os.path.split(behavior_file)[-1]
        subject_id = fname.split('_')[0]
        nwbfile = NWBFile(
            session_start_time=datetime.datetime(1900, 1, 1),
            session_description=fname,
            session_id=fname,
            identifier=str(uuid.uuid4()),
            subject=Subject(subject_id=subject_id, species="Mus musculus"),
            experiment_description=json_metadata["NWBFile"]["experiment_description"],
        )

        nwbfile.add_acquisition(Events(name="level_pulls", description="level pulls", timestamps=times))
        dest_filepath = os.path.join(dest, fname[:-4] + ".nwb")
        with NWBHDF5IO(dest_filepath, "w") as io:
            io.write(nwbfile)
