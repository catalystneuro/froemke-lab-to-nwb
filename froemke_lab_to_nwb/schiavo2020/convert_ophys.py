import os
from datetime import datetime
from glob import glob
import json

from nwb_conversion_tools.datainterfaces import TiffImagingInterface
from nwb_conversion_tools.utils import dict_deep_update
from tqdm import tqdm

from . import SRC_DATA_DIR, DEST_DATA_DIR


def convert_all_ophys(src=SRC_DATA_DIR, dest=DEST_DATA_DIR):
    subject_directories = [
        dir_ for dir_ in glob(src + "/*") if len(glob(dir_ + "/*.tif"))
    ]
    for subject_directory in tqdm(subject_directories, desc="ophys"):
        subject_dir_name = os.path.split(subject_directory)[-1]
        with open(os.path.join(subject_directory, "metadata.json"), "r") as file:
            json_metadata = json.load(file)
        tiff_filepaths = glob(subject_directory + "/*.tif")
        for tiff_filepath in tqdm(tiff_filepaths, desc=subject_directory):
            fname = os.path.split(tiff_filepath)[-1][:-4]
            file_dest = os.path.join(dest, f"{subject_dir_name}_{fname}.nwb")
            imaging_interface = TiffImagingInterface(
                tiff_filepath, sampling_frequency=4.0
            )

            metadata = imaging_interface.get_metadata()
            metadata["Ophys"]["ImagingPlane"][0].update(excitation_lambda=900.0, indicator="GCaMP6f")
            metadata["Ophys"]["Device"] = [
                dict(
                name="multiphoton imaging system",
                manufacturer="Sutter Instruments",
                ),
                dict(
                    name="Ti:Sapphire laser",
                    manufacturer="MaiTai, Spectra-Physics"
                )
            ]

            metadata = dict_deep_update(metadata, json_metadata)
            metadata = dict_deep_update(
                metadata,
                dict(
                    NWBFile=dict(session_start_time=datetime(1900, 1, 1),),
                    Subject=dict(
                        subject_id=os.path.split(subject_directory)[1].split("_")[0],
                        species="Mus musculus",
                        genotype="C57BL/6",
                    ),
                ),
            )

            imaging_interface.run_conversion(metadata=metadata, save_path=file_dest)
