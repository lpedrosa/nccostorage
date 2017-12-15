"""
NCCO storage service
"""
from setuptools import setup, find_packages


def read_requirements(file):
    with open(file, 'r') as f:
        contents = f.readlines()
    return contents


tests_require = [
    'pytest==3.3.1',
    'pytest-aiohttp==0.3.0',
]

setup(
    name='nccostorage',
    version='1.0',
    long_description=__doc__,
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=read_requirements('requirements.txt'),
    setup_requires=['pytest-runner'],
    tests_require=tests_require,
)
