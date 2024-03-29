from setuptools import setup, find_packages
from codecs import open
import os

here = os.path.abspath(os.path.dirname(__file__))

with open(os.path.join(here, "README.md")) as f:
    long_description = f.read()

with open(os.path.join(here, "froemke_lab_to_nwb/carcea2021/requirements.txt")) as f:
    install_requires = f.read().strip().split("\n")


setup(
    name="froemke_lab_to_nwb",
    version="0.1.0",
    description="NWB conversion scripts for the Froemke lab.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Ben Dichter",
    author_email="ben.dichter@catalystneuro.com",
    url="https://github.com/catalystneuro/froemke-lab-to-nwb",
    python_requires=">=3.7",
    install_requires=install_requires,
    packages=find_packages(),
)