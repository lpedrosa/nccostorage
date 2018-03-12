"""
NCCO storage service
"""
from setuptools import setup, find_packages


def read_requirements(file):
    with open(file, 'r') as f:
        contents = f.readlines()
    return contents

setup(
    name='nccostorage',
    version='1.0',
    long_description=__doc__,
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=read_requirements('requirements.txt'),
    setup_requires=['pytest-runner<=3.0.1'],
    tests_require=read_requirements('requirements-test.txt'),
)
