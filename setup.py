import os.path

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
README_FILE = os.path.join(ROOT_DIR, "README.rst")

with open(README_FILE) as f:
    long_description = f.read()

setup(
    name="xutils",
    version="2.0.4",
    description="A Fragmentary Python Library, no any third-part dependencies.",
    long_description=long_description,
    author="xgfone",
    author_email="xgfone@126.com",
    maintainer="xgfone",
    maintainer_email="xgfone@126.com",
    url="https://github.com/xgfone/xutils",
    packages=["xutils"],

    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
    ],
)
