from setuptools import setup, find_packages
from os import path

here = path.abspath(path.dirname(__file__))

with open('README.md') as readme:
    documentation = readme.read()

setup(
    name="bindfs",
    version="0.0.0",
    description="bind fs",
    author="Omar AKHARAZ",
    author_email="omar.akharaz@gmail.com",
    license="ISC",
    url="TODO",
    package_dir={
        '': 'src',
    },
    packages=find_packages(
        path.join(here, 'src'),
        exclude=(
            "*.test*",
            "*.test.*",
        ),
    ),
    install_requires=(
      'fusepy >= 2.0.4',
    ),
    entry_points={
        'console_scripts': (
            'bindfspy = bindfs.bin.bindfs:main',
        ),
    },
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: ISC License (ISCL)',
        'Operating System :: MacOS',
        'Operating System :: POSIX',
        'Operating System :: Unix',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 3',
        'Topic :: System :: Filesystems',
    ]
)
