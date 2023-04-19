from typing import Optional

import pandas as pd
from neuroconv.basedatainterface import BaseDataInterface
from neuroconv.utils import FilePathType
from pynwb import NWBFile
from pynwb.epoch import TimeIntervals


class BehaviorDataInterface(BaseDataInterface):

    def __init__(self, file_path: FilePathType):
        super().__init__(file_path=file_path)
        self.df = pd.read_excel("Downloads/behavior/ROV40_day1_obs.xlsx")

    def get_metadata(self):
        session_start_time = self.df["Observation date"].iloc[0]
        return dict(NWBFile=dict(session_start_time=session_start_time))

    def run_conversion(self, nwbfile: NWBFile, metadata: Optional[dict] = None):

        ti_table = TimeIntervals(
            name="pup_events",
            description="events and states of pups",
        )
        ti_table.add_column("behavior", "type of event")
        for i, row in self.df.iterrows():
            ti_table.add_interval(
                start_time=row["Start (s)"],
                stop_time=row["Stop (s)"],
                behavior=row["Behavior"],
            )


        nwbfile.add_invalid_time_interval(ti_table)