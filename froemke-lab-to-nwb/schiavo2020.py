import os
from nwb_conversion_tools.datainterfaces import TiffImagingInterface
from datetime import datetime
from glob import glob
from tqdm import tqdm

SRC_DATA_DIR = "/Users/bendichter/Desktop/Froemke data"

tiff_filepaths = list(glob(SRC_DATA_DIR + "/*/*.tif"))
for tiff_filepath in tqdm(tiff_filepaths):
    fname = os.path.split(tiff_filepath)[-1][:-4] + ".nwb"
    imaging_interface = TiffImagingInterface(tiff_filepath, sampling_frequency=4.0)

    metadata = imaging_interface.get_metadata()
    metadata.update(NWBFile=dict(session_start_time=datetime.now()))

    imaging_interface.run_conversion(metadata=metadata, save_path=fname)