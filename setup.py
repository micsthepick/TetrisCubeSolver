from setuptools import setup
from Cython.Build import cythonize

setup(
    ext_modules=cythonize(
        ['AX.pyx'],                  # Cython code
        annotate=True),                 # enables generation of the html annotation file
)