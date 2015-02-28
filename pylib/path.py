#!/usr/bin/env python
"""

Version:

"""
import os
import pylib.osscripts as oss

#-------------------------------------------------------------------------------
if __name__ == "__main__":
#-------------------------------------------------------------------------------
    p = oss.path("C:/tmp/cool.bob")
    print p, p.ext, p.name, p.path, p.drive, p.fpath, p.basename
    print p.drive_path, p.drive_path_name, p.name_ext



