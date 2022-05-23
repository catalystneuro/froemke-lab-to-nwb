import os
from glob import glob
import json

import numpy as np
import pandas as pd
from nwb_conversion_tools.datainterfaces.icephys.abf.abfdatainterface import (
    AbfInterface,
)
from nwb_conversion_tools.tools.nwb_helpers import make_nwbfile_from_metadata
from nwb_conversion_tools.utils import dict_deep_update
from pynwb import NWBHDF5IO
from pynwb import TimeSeries
from tqdm import tqdm

from ndx_sound import AcousticWaveformSeries

from . import DEST_DATA_DIR, SRC_DATA_DIR

IN_VIVO_DIRS = [
    "In vivo whole-cell recordings_Experienced females",
    "In vivo whole-cell recordings_Naive females",
]


def convert_in_vivo(cell_name, df, input_metadata, article_dir, dest_dir):
    file_ids = df["file #"].values
    file_ids = [x.replace("193260007", "19326007") for x in file_ids]  # correct typo
    abf_filepaths = [os.path.join(article_dir, file_id + ".abf") for file_id in file_ids]
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
    abf_interface.run_conversion(nwbfile=nwbfile, metadata=metadata, skip_electrodes=(1,))

    # add auditory stimulus
    neo_reader = abf_interface.readers_list[0]
    if neo_reader.signal_channels_count(0) == 2:
        rate = neo_reader.get_signal_sampling_rate()
        for i_segment in range(neo_reader.segment_count(block_index=0)):
            nwbfile.add_stimulus(
                AcousticWaveformSeries(
                    name=f"auditory_stimulus{i_segment+1:02}",
                    description="auditory stimulus recorded inline in ABF file.",
                    data=neo_reader.get_analogsignal_chunk(block_index=0, seg_index=i_segment)[:, 1],
                    starting_time=neo_reader.get_signal_t_start(seg_index=i_segment, block_index=0),
                    rate=rate,
                )
            )

    nwbfile.icephys_sequential_recordings.add_column(
        name="stimiulus set", description="stimiulus set", data=df["stimulus set"].values.tolist()
    )
    nwbfile.icephys_sequential_recordings.add_column(
        name="holding", description="holding (mV)", data=df["holding"].values.tolist()
    )
    nwbfile.icephys_sequential_recordings.add_column(
        name="notes", description="notes", data=df["notes"].values.tolist()
    )

    with NWBHDF5IO(os.path.join(dest_dir, cell_name + ".nwb"), "w") as io:
        io.write(nwbfile)


def convert_all_in_vivo(dest_dir=DEST_DATA_DIR):
    for in_vivo_dir in IN_VIVO_DIRS:
        article_dir = os.path.join(SRC_DATA_DIR, in_vivo_dir)
        with open(os.path.join(article_dir, "metadata.json"), "r") as file:
            metadata = json.load(file)

        xlsx_filepath = glob(os.path.join(article_dir, "*.xlsx"))[0]
        df = pd.read_excel(xlsx_filepath, header=1, dtype={"file #": str, "notes": str}, na_filter=False)
        df["cell name"] = df["cell name"].replace('', np.nan)
        df["cell name"] = df["cell name"].ffill()
        for cell_name, cell_df in tqdm(list(df.groupby("cell name")), desc=in_vivo_dir):
            convert_in_vivo(cell_name, cell_df, metadata, article_dir, dest_dir)