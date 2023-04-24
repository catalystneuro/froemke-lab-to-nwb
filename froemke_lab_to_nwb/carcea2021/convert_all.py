import os
from pathlib import Path

from neuroconv.utils.dict import DeepDict
from tqdm import tqdm

from .converter import Carcea2021EphysConverter, Carcea2021OphysConverter


ephys_sessions = [
    # subject, session
    ("V85",  "12102017"),
    ("V85",  "12102017_2"),
    ("V110", "03032018"),
    ("V111", "03032018"),
    ("V111", "03052018"),
    ("V111", "03062018"),
    ("V116", "03082018"),
    ("V116", "03092018"),
    ("V116", "03102018"),
    ("V116", "03122018"),
    ("V118", "03182018"),
    ("V118", "03192018"),
    ("V118", "03212018"),
    ("V118", "03222018"),
]

photometry_sessions = [
    # subject, session
    ("ROV40", "Day 1_obs"),
    ("ROV40", "Day 1_retrieval"),
    ("ROV40", "Day 2_obs"),
    ("ROV40", "Day 2_retrieval"),
    ("ROV40", "Day 3_obs"),
    ("ROV40", "Day 3_retrieval"),
    ("ROV41", "Day 1_obs"),
    ("ROV41", "Day 1_retrieval"),
    ("ROV41", "Day 2_obs"),
    ("ROV41", "Day 2_retrieval"),
    ("ROV41", "Day 3_obs"),
    ("ROV41", "Day 3_retrieval"),
    ("ROV43", "Day 1_obs"),
    ("ROV44", "Day 1_obs"),
    ("ROV45", "Day 1_obs"),
    ("ROV49", "Day 1_obs"),
]

subject_metadata = dict(
    sex="F",
    age="P8W/P10W",
    genotype="Oxy-IRES-Cre het",
    strain="mixed C57BL/6 x 129S",
    description="Virgin female co-housed with dam and pups",
    species="Mus musculus",
)


root = "/Volumes/Extreme Pro/neural_data/Froemke/Carcea2021"


def convert_all(data_dir=root, stub_test=False, ephys_session=True, ophys_session=True):

    nev_files = list(Path(data_dir).rglob('[!.]*.nev'))
    os.mkdir(os.path.join(data_dir, "nwb"))

    if ephys_session:
        for subject_id, session_id in tqdm(ephys_sessions, desc="ecephys sessions"):
            out_path = os.path.join(data_dir, "nwb", subject_id + "_" + session_id + ".nwb")
            if os.path.exists(out_path):
                continue

            ns5_path = os.path.join(data_dir, "ns5", f"{subject_id}_{session_id}.ns5")
            source_data = DeepDict()
            source_data["recording"]["file_path"] = ns5_path

            for x in nev_files:
                if f"{subject_id}_{session_id}" in str(x):
                    source_data["sorting"]["file_path"] = str(x)
                    source_data["sorting"]["sampling_frequency"] = 30_000.
                    continue

            behav_path = Path(data_dir) / "ephys_behavior_curated" / f"{subject_id}_{session_id}.xlsx"
            if behav_path.is_file():
                source_data["behavior"]["file_path"] = str(behav_path)

            #audio_files = natsort((Path(root) / "ns5" / "Audio files" / f"{subject_id}_{session_id}").rglob("*.WAV"))

            print(source_data, flush=True)

            converter = Carcea2021EphysConverter(source_data, verbose=True)
            metadata = converter.get_metadata()
            metadata["NWBFile"]["session_id"] = session_id
            metadata["Subject"] = subject_metadata
            metadata["Subject"]["subject_id"] = subject_id

            conversion_options = dict(
                recording=dict(
                    iterator_opts=dict(
                        display_progress=True
                    ),
                    stub_test=stub_test,
                ),
            )

            converter.run_conversion(
                out_path,
                metadata=metadata,
                conversion_options=conversion_options,
            )

    if ophys_session:
        for subject_id, session_id in tqdm(photometry_sessions, "ophys sessions"):

            out_path = os.path.join(data_dir, "nwb", subject_id + "_" + session_id + ".nwb")
            if os.path.exists(out_path):
                continue

            behav_path = os.path.join(data_dir, "ophys_behavior", f"{subject_id}_{session_id}.xlsx".lower().replace(" ",
                                                                                                                ""))
            photometry_path = os.path.join(data_dir, "photometry", subject_id, session_id)
            source_data = dict(
                behavior=dict(file_path=behav_path),
                photometry=dict(folder_path=photometry_path),
            )

            Carcea2021OphysConverter(source_data)

            converter = Carcea2021OphysConverter(source_data)
            metadata = converter.get_metadata()

            metadata["NWBFile"]["session_id"] = session_id
            metadata["Subject"] = subject_metadata
            metadata["Subject"]["subject_id"] = subject_id

            converter.run_conversion(
                out_path,
                metadata=metadata,
            )


if __name__ == "__main__":
    convert_all(data_dir=root, stub_test=True, ephys_session=False, ophys_session=True)
