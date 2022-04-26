import os
from glob import glob
from typing import Optional

from nwb_conversion_tools.datainterfaces.icephys.abf.abfdatainterface import (
    AbfInterface,
)
from nwb_conversion_tools.tools.nwb_helpers import make_nwbfile_from_metadata
from pynwb.file import TimeSeries
from pynwb import NWBHDF5IO
from tqdm import tqdm


def convert_abf_file(abf_filepath, save_path: Optional[str] = None):
    save_path = save_path or os.path.split(abf_filepath)[-1][:-4] + ".nwb"

    abf_interface = AbfInterface([abf_filepath,])
    metadata = abf_interface.get_metadata()
    metadata["Icephys"]["Electrode"] = metadata["Icephys"]["Electrode"][:1]

    nwbfile = make_nwbfile_from_metadata(metadata)

    abf_interface.run_conversion(nwbfile=nwbfile, metadata=metadata, skip_electrodes=(1,))

    neo_reader = abf_interface.readers_list[0]
    if neo_reader.signal_channels_count(0) == 2:
        rate = neo_reader.get_signal_sampling_rate()
        for i_segment in range(neo_reader.segment_count(block_index=0)):
            nwbfile.add_stimulus(
                TimeSeries(
                    name=f"auditory_stimulus{i_segment+1:02}",
                    description="auditory stimulus recorded inline in ABF file.",
                    data=neo_reader.get_analogsignal_chunk(block_index=0, seg_index=i_segment)[:, 1],
                    starting_time=neo_reader.get_signal_t_start(seg_index=i_segment, block_index=0),
                    rate=rate,
                    unit="n.a.",
                )
            )

    with NWBHDF5IO(save_path, "w") as io:
        io.write(nwbfile)


abf_filepaths = list(glob("/Users/bendichter/Desktop/Froemke data/*/*.abf"))

for abf_filepath in tqdm(abf_filepaths):
    print(abf_filepath)
    convert_abf_file(abf_filepath)