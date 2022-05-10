import json
import os

import numpy as np
import pandas as pd
from nwb_conversion_tools.datainterfaces.icephys.abf.abfdatainterface import (
    AbfInterface,
)
from nwb_conversion_tools.tools.nwb_helpers import make_nwbfile_from_metadata
from nwb_conversion_tools.utils import dict_deep_update
from pynwb import NWBHDF5IO
from tqdm import tqdm
from tqdm.notebook import tqdm

from . import DEST_DATA_DIR, SRC_DATA_DIR

WHOLE_CELL_OXT_DIR = os.path.join(SRC_DATA_DIR, "In vitro recordings_oxytocin")


def convert_oxt_cell(cell_name, df, input_metadata, dest_dir=DEST_DATA_DIR):
    file_ids = df["File #s"].values
    abf_filepaths = [os.path.join(WHOLE_CELL_OXT_DIR, file_id + ".abf") for file_id in file_ids]
    abf_interface = AbfInterface(abf_filepaths)
    metadata = abf_interface.get_metadata()

    metadata = dict_deep_update(metadata, input_metadata)

    metadata.update(
        Subject=dict(
            subject_id=file_ids[0][:5],
            species="Mus musculus",
        )
    )

    nwbfile = make_nwbfile_from_metadata(metadata)
    abf_interface.run_conversion(nwbfile=nwbfile, metadata=metadata)

    nwbfile.icephys_sequential_recordings.add_column(
        name="notes", description="notes from excel spreadsheet", data=df["Notes"].values.tolist()
    )

    with NWBHDF5IO(os.path.join(dest_dir, cell_name + ".nwb"), "w") as io:
        io.write(nwbfile)


def convert_all_oxt(article_directory, metadata):
    df_oxt = pd.read_excel(
        os.path.join(article_directory, "In vitro whole-cell recordings_Oxytocin experiments.xlsx"),
        header=1,
        usecols=(0, 1, 2, 3),
        na_filter=False,
    )
    df_oxt["Cell Name"] = df_oxt["Cell Name"].replace("", np.nan)
    df_oxt["Cell Name"] = df_oxt["Cell Name"].ffill()
    for cell_name, df in tqdm(list(df_oxt.groupby("Cell Name")), desc="OXT icephys"):
        convert_oxt_cell(cell_name, df, metadata)


def convert_all_control(article_directory, metadata):
    df_control = pd.read_excel(
        os.path.join(article_directory, "In vitro whole-cell recordings_Oxytocin experiments.xlsx"),
        header=1,
        usecols=(6, 7, 8, 9),
        na_filter=False,
    )
    df_control = df_control.rename(
        {
            "Cell Name.1": "Cell Name",
            "Folder/Date.1": "Folder/Date",
            "File #s.1": "File #s",
            "Notes.1": "Notes"
        },
        axis=1,
    )

    keep_rows = ~np.all(df_control.values == "", axis=1)
    df_control = df_control[keep_rows]

    df_control["Cell Name"][df_control["Cell Name"] == ""] = np.nan
    df_control["Cell Name"] = df_control["Cell Name"].ffill()
    for cell_name, df in tqdm(list(df_control.groupby("Cell Name")), "control icephys"):
        convert_oxt_cell(cell_name, df, metadata)


def convert_all_oxt_and_control(article_directory=WHOLE_CELL_OXT_DIR):
    with open(os.path.join(article_directory, "metadata.json"), "r") as file:
        metadata = json.load(file)

    convert_all_oxt(article_directory, metadata)
    convert_all_control(article_directory, metadata)