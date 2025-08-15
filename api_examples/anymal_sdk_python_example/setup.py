from setuptools import setup
from catkin_pkg.python_setup import generate_distutils_setup

d = generate_distutils_setup(
    packages=['anymal_sdk_example'],
    package_dir={'': 'src'},
    # Using a Creative Commons image, with transparent background removed (and set to white)
    # License: https://commons.wikimedia.org/wiki/File:No_photo_%282067963%29_-_The_Noun_Project.svg#filelinks
    package_data={'':['resources/*.png']}
)

setup(**d)
