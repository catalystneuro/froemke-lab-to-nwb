import os
from pathlib import Path
from typing import Optional

from neuroconv.basedatainterface import BaseDataInterface

import numpy as np

from pynwb import NWBFile
from pynwb.core import DynamicTableRegion
from pynwb.ophys import RoiResponseSeries
from ndx_photometry import (
    FibersTable,
    CommandedVoltageSeries,
    PhotodetectorsTable,
    ExcitationSourcesTable,
    FiberPhotometry,
    FluorophoresTable
)
from scipy.io import loadmat


class PhotometryInterface(BaseDataInterface):

    def __init__(self, folder_path):
        super().__init__(folder_path=folder_path)

    def run_conversion(
        self,
        nwbfile: Optional[NWBFile] = None,
        metadata: Optional[dict] = None,
        overwrite: bool = False,
        **conversion_options,
    ):
        ctrl_path = os.path.join(self.source_data["folder_path"], "Ctrl.mat")
        if Path(ctrl_path).is_file():
            command_data = loadmat(ctrl_path)["Ctrl"].ravel()
        else:
            command_data = None

        timestamps = loadmat(
            os.path.join(self.source_data["folder_path"], "time.mat")
        )["x"].ravel()

        resp_data = loadmat(
            os.path.join(self.source_data["folder_path"], "Ca.mat")
        )["Ca"].ravel()

        if command_data is not None:
            commandedvoltage_series = CommandedVoltageSeries(
                name="commanded_voltage",
                data=command_data,
                frequency=400.0,
                power=30.0,  # micro-watts
                timestamps=timestamps,
                unit="uW",
                description="Power is in uW."
            )

            nwbfile.add_acquisition(commandedvoltage_series)
        else:
            commandedvoltage_series = None

        excitationsources_table = ExcitationSourcesTable(
            description="excitation sources table"
        )

        # Add one row to the table per excitation source
        excitationsources_table.add_row(
            peak_wavelength=np.nan,
            source_type="LED",
            commanded_voltage=commandedvoltage_series,
        )

        photodetectors_table = PhotodetectorsTable(
            description="photodetectors table"
        )

        # Add one row to the table per photodetector
        photodetectors_table.add_row(
            peak_wavelength=np.nan,
            type="unknown",
            gain=np.nan,
        )

        fluorophores_table = FluorophoresTable(
            description='fluorophores'
        )

        fluorophores_table.add_row(
            label='unknown',
            location='unknown',
            coordinates=(np.nan, np.nan, np.nan),
        )

        fibers_table = FibersTable(
            description="fibers table"
        )

        fibers_table.add_fiber(
            excitation_source=0,  # integers indicated rows of excitation sources table
            photodetector=0,
            fluorophores=[0],  # potentially multiple fluorophores, so list of indices
            location='unknown',
            notes='unknown',
        )

        fibers_ref = DynamicTableRegion(
            name="rois",
            data=[0],
            description="source fibers",
            table=fibers_table
        )

        # Here we add the metadata tables to the metadata section
        nwbfile.add_lab_meta_data(
            FiberPhotometry(
                fibers=fibers_table,
                excitation_sources=excitationsources_table,
                photodetectors=photodetectors_table,
                fluorophores=fluorophores_table,
            )
        )

        roi_response_series = RoiResponseSeries(
            timestamps=timestamps,
            data=resp_data,
            unit="W",
            rios=fibers_ref,
        )

        nwbfile.add_acquisition(roi_response_series)



