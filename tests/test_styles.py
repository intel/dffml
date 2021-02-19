"""
This file contains styles tests for checking at the end of source files.
"""
import os
from os import path
import mimetypes
from pathlib import Path
import unittest
from dffml.util.asynctestcase import IntegrationCLITestCase

ROOT_DIR = os.path.dirname(os.path.abspath(os.path.dirname(__file__)))

class TestML(unittest.TestCase):
    def walk(self,top, topdown=True, onerror=None, followlinks=False, maxdepth=None):
        
        islink, join, isdir = path.islink, path.join, path.isdir

        try:
            names = os.listdir(top)
        except Exception as err:
            if onerror is not None:
                onerror(err)
            return

        dirs, nondirs = [], []
        for name in names:
            if isdir(join(top, name)) and not name.startswith('.') and '.egg-info' not in name:
                dirs.append(name)
            elif not isdir(join(top, name)) and not os.path.getsize(join(top,name)) == 0 and not '.sh' in join(top, name) :
                nondirs.append(name)

        if topdown:
            yield top, dirs, nondirs

        if maxdepth is None or maxdepth > 1:
            for name in dirs:
                new_path = join(top, name)
                if followlinks or not islink(new_path):
                    for x in self.walk(new_path, topdown, onerror, followlinks, None if maxdepth is None else maxdepth-1):
                        yield x
        if not topdown:
            yield top, dirs, nondirs

    def test_styles(self):
        for root, dirnames, filenames in self.walk(ROOT_DIR, maxdepth=None):
            for file in filenames:
                with open(root + '/' +  file ,"r") as f:
                    mime = mimetypes.guess_type(f.name)[0]
                    if mime is not None:
                        if "text" in mime:
                            f.seek(0, 2)                            
                            f.seek(f.tell() - 1, 0)
                            self.assertEqual(f.read(), "\n", "Newline required at the end in"+root+"/"+file)
