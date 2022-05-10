import os
from glob import glob
import json

import pandas as pd
from tqdm import tqdm

import numpy as np
from pynwb import NWBHDF5IO
from nwb_conversion_tools.datainterfaces.icephys.abf.abfdatainterface import (
    AbfInterface,
)

from nwb_conversion_tools.tools.nwb_helpers import make_nwbfile_from_metadata
from nwb_conversion_tools.utils import dict_deep_update

from . import SRC_DATA_DIR, DEST_DATA_DIR

EXCLUDE_CELLS = ("Cell 20",)
ACTX_DIR = os.path.join(SRC_DATA_DIR, "ACtx slice recordings - Repeated stimulation")


def convert_actx_cell(cell_id, cell_df, input_metadata, dest_dir=DEST_DATA_DIR):

    file_ids = []
    timings = []
    for timing in ("75 ms", "175 ms", "575 ms"):
        for file_id in cell_df[timing].values:
            if file_id != 'N/A':
                file_ids.append(file_id)
                timings.append(timing)

    abf_filepaths = [os.path.join(ACTX_DIR, file_id + ".abf") for file_id in file_ids]
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

    nwbfile.icephys_sequential_recordings["stimulus_type"].data[:] = timings

    dest_filepath = os.path.join(dest_dir, cell_id + ".nwb")
    with NWBHDF5IO(dest_filepath, "w") as io:
        io.write(nwbfile)


def convert_all_actx(article_dir=ACTX_DIR):
    with open(os.path.join(article_dir, "metadata.json"), "r") as file:
        metadata = json.load(file)
    xlsx_filepath = glob(os.path.join(article_dir, "*.xlsx"))[0]
    df = pd.read_excel(xlsx_filepath, dtype=str, na_filter=False)
    df["Cell #"] = df["Cell #"].replace('', np.nan)
    df["Cell #"] = df["Cell #"].ffill()
    for cell_id, cell_df in tqdm(list(df.groupby("Cell #")), desc="actx"):
        if cell_id in EXCLUDE_CELLS:
            continue
        convert_actx_cell(cell_id, cell_df, metadata)