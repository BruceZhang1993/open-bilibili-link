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
    requires=['aiohttp', 'rsa', 'pydantic', 'aiocache'],
    extras_require={
        'gui': ['asyncqt', 'pyqt5'],
    },
    python_requires=">=3.7",
    keywords=['obl', 'bilibili', 'live'],
    classifiers=[
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3 :: Only',
        'Environment :: X11 Applications :: Qt',
        "Operating System :: MacOS",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: POSIX :: Linux",
        "License :: OSI Approved :: GNU Lesser General Public License v3 (LGPLv3)"
    ],
    entry_points={
        'console_scripts': [
            "open-bilibili-link=open_bilibili_link.__main__:main",
        ]
    },
    package_data={
        '': ['*.yaml']
    }
)
