
from setuptools import setup
from Cython.Build import cythonize
from setuptools.extension import Extension

# Define the extension module for Cython
ext_modules = [
    Extension("test_comp", ["browse_annoying_site.py"])
]

# Setup configuration for building the Cython extension
setup(
    name="test_comp",
    ext_modules=cythonize(
        ext_modules,
        compiler_directives={'language_level': "3"}
    ),
    zip_safe=False,
)
