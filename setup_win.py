from distutils.core import setup
import py2exe
import gridder
setup(console=['gzilla.py'], options = { "py2exe" : {"includes" : ["gridder","reportlab","gzilla"]}})
