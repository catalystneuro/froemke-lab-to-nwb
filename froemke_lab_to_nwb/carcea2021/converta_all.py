import os
from pathlib import Path

from natsort.natsort import natsort

from neuroconv.utils import dict_deep_update
from neuroconv.utils.dict import DeepDict

from .converter import Carcea2021EphysConverter, Carcea2021OphysConverter

ephys_sessions = [
    # subject, session
    ("V110", "03032018"),
    ("V111", "03032018"),
    ("V111", "03052018"),
    ("V111", "03062018"),
    ("V116", "03082018"),
    ("V118", "03182018"),
    ("V118", "03192018"),
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
)


root = "/Users/bendichter/Downloads/Carcea et al., 2021_data"
nev_files = Path(root).rglob("*.nev")


out = "~/Downloads/Carcea2021/out"

for subject_id, session_id in ephys_sessions:

    ns5_path = os.path.join(root, "ns5", f"{subject_id}_{session_id}.ns5")
    source_data = DeepDict()
    source_data["recording"]["file_path"] = ns5_path

    for x in nev_files:
        if f"{subject_id}_{session_id}" in x:
            source_data["sorting"]["file_path"] = x

    audio_files = natsort((Path(root) / "ns5" / "Audio files" / f"{subject_id}_{session_id}").rglob("*.WAV"))


    converter = Carcea2021EphysConverter(source_data)
    metadata = converter.get_metadata()
    metadata["NWBFile"]["session_id"] = session_id
    metadata["Subject"] = {**dict(subject_id=subject_id), **subject_metadata}

    converter.run_conversion(
        os.path.join(out, subject_id + "_" + session_id + ".nwb"), metadata=metadata,
    )


for subject_id, session_id in photometry_sessions:
    behav_path = os.path.join(root, "behavior", f"{subject_id}_{session_id}.xlsx")
    photometry_path = os.path.join(root, "photometry", subject_id, session_id)
    source_data = dict(
        behavior=dict(file_path=behav_path),
        photometry=dict(folder_path=photometry_path),
    )

    Carcea2021OphysConverter(source_data)

    converter = Carcea2021OphysConverter(source_data)
    metadata = converter.get_metadata()

    metadata = dict_deep_update(
        metadata,
        dict(
            NWBFile=dict(session_id=session_id),
            Subject={**dict(subject_id=subject_id), **subject_metadata},
        ),
    )

    converter.run_conversion(
        os.path.join(out, subject_id + "_" + session_id + ".nwb"),
        metadata=metadata,
    )
