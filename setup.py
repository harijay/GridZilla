from setuptools import setup, find_packages
from distutils.core import setup
import py2exe
setup(
    name = "GridZilla",
        version = "0.2beta",
	    packages = find_packages(),
	    scripts = ["gzilla.py"],
	    author = "Hari Jayaram",
	    author_email="hari@code-itch.com",
	    license = "MIT",
	    url = "http://www.code-itch.com/gridzilla",
	    keywords = " Protein Crystallization Grid maker for 24 , 96 and 384 well lates ",
	    include_package_data = True,

	    )
