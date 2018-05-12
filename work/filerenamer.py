#!/usr/bin/python

import os
import sys

def fileRenamer(photo_path, search_str, replace_str):
    for root, subFolders, files in os.walk(rootdir):
      for file in files:	
        os.rename(os.path.join(root,file), os.path.join(root, file.replace(search_str, replace_str)))
        print file, file.replace(search_str, replace_str)

rootdir = sys.argv[1]
search_str = sys.argv[2]
replace_str = sys.argv[3]

fileRenamer(rootdir, search_str, replace_str)   
