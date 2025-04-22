from setuptools import setup, find_packages

setup(
    name="jun24_cde_job_market",  # Package name
    version="0.1",  # Package version
    packages=find_packages(where="."),  # Finds all the packages in the current directory (i.e., the root "jun24" folder)
    package_dir={'': '.'},  # Indicates that the root package is in the current directory
)
