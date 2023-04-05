import os
from glob import glob
import json
from datetime import datetime

from scipy.io.wavfile import read as wavread

from nwb_conversion_tools.datainterfaces import ScanImageImagingInterface
from nwb_conversion_tools.utils import dict_deep_update
from tqdm import tqdm
from ndx_sound import AcousticWaveformSeries
from hdmf.backends.hdf5 import H5DataIO

from . import SRC_DATA_DIR, DEST_DATA_DIR, CALLS_DIR


PUP_CALL_NAMES = {
    "j5b": "j5b",
    "j6b": "J6B",
    "j6a": "j6a",
    "j1a": "J1A",
    "j8": "J8A",
    "61f": "6.1F",
    "71b": "71b"
}


def parse_fname(fname):
    pieces = fname.split("_")
    if pieces[2] in PUP_CALL_NAMES and pieces[3].isnumeric(): #e.g. "firstretrieval_r2_71b_1200_800_1400_1800_600_004"
        for version_number in pieces[3:-1]:
            path = os.path.join(CALLS_DIR, "Pup calls and morphs", pieces[2], f"{pieces[2]}_{version_number}.wav")
            assert os.path.exists(path)
            yield path
    elif pieces[2].lower() == "pc":
        for call_name in pieces[3:-1]:  # e.g. "base_r2_pc1_71b_j6a_61f_001"
            path = os.path.join(CALLS_DIR, "Pup calls", f"{PUP_CALL_NAMES[call_name]}.wav")
            assert os.path.exists(path)
            yield path

    elif pieces[2][:3] in PUP_CALL_NAMES and pieces[2][3:].isnumeric():  # e.g. "firstretrieval_r2_61f3400_71b4200_007"
        for id_ in pieces[2:-1]:
            name = id_[:3]
            version_number = id[3:]
            path = os.path.join(CALLS_DIR, "Pup calls and morphs", name, f"{name}_{version_number}.wav")
            assert os.path.exists(path)
            yield path


def convert_all_ophys(src=SRC_DATA_DIR, dest=DEST_DATA_DIR, include_audio=False):
    subject_directories = [
        dir_ for dir_ in glob(src + "/*") if len(glob(dir_ + "/*.tif"))
    ]
    for subject_directory in tqdm(subject_directories, desc="ophys"):
        subject_dir_name = os.path.split(subject_directory)[-1]
        with open(os.path.join(subject_directory, "metadata.json"), "r") as file:
            json_metadata = json.load(file)
        tiff_filepaths = glob(subject_directory + "/*.tif")
        for tiff_filepath in tqdm(tiff_filepaths, desc=subject_directory):
            print(tiff_filepath)
            fname = os.path.split(tiff_filepath)[-1][:-4]
            file_dest = os.path.join(dest, f"{subject_dir_name}_{fname}.nwb")
            imaging_interface = ScanImageImagingInterface(tiff_filepath, fallback_sampling_frequency=3.90625)

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
                    NWBFile=dict(session_description=fname),
                    Subject=dict(
                        subject_id=os.path.split(subject_directory)[1].split("_")[0],
                        species="Mus musculus",
                        genotype="C57BL/6",
                    ),
                ),
            )

            if "session_start_time" not in metadata["NWBFile"]:
                if fname == "plus24hrs_postexp1_r2_61f1150_850_1600_2200_700_005":
                    session_start_time = datetime(2018, 3, 8, 3,)
                elif fname == "plus24hr_r3_puretones_005_turbo_alignpc1":
                    session_start_time = datetime(2017, 6, 15, 1, 35, 0)
                metadata["NWBFile"].update(session_start_time=session_start_time)

            nwbfile = imaging_interface.run_conversion(metadata=metadata, save_path=file_dest)
            if include_audio:
                for waveform_path in parse_fname(fname):
                    rate, data = wavread(waveform_path)
                    nwbfile.add_stimulus_template(
                        AcousticWaveformSeries(
                            name=os.path.split(waveform_path)[-1],
                            data=H5DataIO(data, compression=True),
                            rate=float(rate),
                            description=os.path.split(waveform_path)[-1],
                        )
                    )
