from setuptools import setup
from Cython.Build import cythonize
from setuptools.extension import Extension
import sys

# Define the extension for Cython
ext_modules = [
    Extension("main", ["test.py"])  # Replace 'main' with your script's name if needed
]

setup(
    name="main_executable",
    ext_modules=cythonize(ext_modules, compiler_directives={'language_level': "3"}),  # Python 3 support
    zip_safe=False,
)
