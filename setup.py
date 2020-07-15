from distutils.core import setup

from setuptools import find_packages

from open_bilibili_link.__meta__ import PACKAGE, VERSION, URL, LICENSE, AUTHOR, AUTHOR_EMAIL, DESCRIPTION, DATA_FILES

setup(
    name=PACKAGE,
    version=VERSION,
    packages=find_packages(),
    url=URL,
    license=LICENSE,
    author=AUTHOR,
    author_email=AUTHOR_EMAIL,
    description=DESCRIPTION,
    data_files=DATA_FILES,
)
