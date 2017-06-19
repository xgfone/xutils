try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(
    name="xutils",
    version="0.8.1",
    description="A Fragmentary Python Library.",
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
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
    ],
)
