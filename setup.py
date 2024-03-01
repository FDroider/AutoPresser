from setuptools import setup
from Cython.Build import cythonize

setup(
    name="UI_app",
    ext_modules=cythonize(module_list="UI_C.py")
)