from typing import Optional

import pandas as pd
from neuroconv.basedatainterface import BaseDataInterface
from neuroconv.utils import FilePathType
from pynwb import NWBFile
from pynwb.epoch import TimeIntervals


class PhotometryBehaviorDataInterface(BaseDataInterface):

    def __init__(self, file_path: FilePathType):
        """

        Parameters
        ----------
        file_path: FilePathType
            e.g. "Downloads/behavior/ROV40_day1_obs.xlsx"
        """
        super().__init__(file_path=file_path)
        self.df = pd.read_excel(file_path)

    def get_metadata(self):
        metadata = super().get_metadata()
        metadata["NWBFile"]["session_start_time"] = self.df["Observation date"].iloc[0]
        return metadata

    def align_timestamps(self):
        pass

    def get_original_timestamps(self):
        pass

    def get_timestamps(self):
        pass

    def run_conversion(self, nwbfile: NWBFile, metadata: Optional[dict] = None):

        ti_table = TimeIntervals(name="behavioral_events", description="events and states of pups")
        ti_table.add_column("behavior", "type of event")
        for i, row in self.df.iterrows():
            ti_table.add_interval(
                start_time=row["Start (s)"],
                stop_time=row["Stop (s)"],
                behavior=row["Behavior"],
            )

        behavior_module = nwbfile.processing.get("behavior", nwbfile.create_processing_module("behavior", "behavior"))
        behavior_module.add(ti_table)


class EcephysBehaviorDataInterface(BaseDataInterface):

    def __init__(self, file_path: FilePathType):
        """

        Parameters
        ----------
        file_path: FilePathType
            e.g. "Downloads/behavior/ROV40_day1_obs.xlsx"
        """
        super().__init__(file_path=file_path)
        self.df = pd.read_excel(file_path)

    def run_conversion(self, nwbfile: NWBFile, metadata: Optional[dict] = None):

        ti_table = TimeIntervals(name="behavioral_events", description="events and states of pups")

        behavior_module = nwbfile.processing.get("behavior", nwbfile.create_processing_module("behavior", "behavior"))

        ti_table.add_column("behavior", "type of behavior")
        for i, row in self.df.iterrows():
            ti_table.add_interval(
                start_time=row["START"],
                stop_time=row["STOP"],
                behavior=row["Behavior"],
            )

        behavior_module.add(ti_table)

    def align_timestamps(self):
        pass

    def get_original_timestamps(self):
        pass

    def get_timestamps(self):
        pass
