import re
import ast
from glob import glob
from os.path import basename, splitext

from setuptools import find_packages
from setuptools import setup

_version_re = re.compile(r'__version__\s+=\s+(.*)')

with open('src/nbsnapshot/__init__.py', 'rb') as f:
    VERSION = str(
        ast.literal_eval(
            _version_re.search(f.read().decode('utf-8')).group(1)))

REQUIRES = [
    'click',
    'papermill',
    'ploomber-core>=0.0.4',
    # we need it to use papermill
    'ipykernel',
    'sklearn-evaluation',
]

DEV = [
    'pytest',
    'flake8',
    'nbformat',
    'ipykernel',
    'invoke',
]

setup(
    name='nbsnapshot',
    version=VERSION,
    description=None,
    license=None,
    author=None,
    author_email=None,
    url=None,
    packages=find_packages('src'),
    package_dir={'': 'src'},
    py_modules=[splitext(basename(path))[0] for path in glob('src/*.py')],
    include_package_data=True,
    classifiers=[],
    keywords=[],
    install_requires=REQUIRES,
    extras_require={
        'dev': DEV,
    },
    entry_points={
        'console_scripts': ['nbsnapshot=nbsnapshot.cli:cli'],
    },
)
