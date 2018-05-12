#!/usr/bin/python

import os
from PIL import Image
from PIL.ExifTags import TAGS

photo_path = "/home/mr_bin/Photo/"

def dateTimeGetter(photo_path):    
    fileDates = {}
    for filename in os.listdir(photo_path):        
        i = Image.open(photo_path + filename)
        if i:
            info = i._getexif()
            for tag,value in info.items():
                decoded = TAGS.get(tag,tag)
                if decoded == "DateTimeDigitized":     
                    fileDates[filename] = value                    
        else:
            continue
            
    return fileDates

def fileRenamer(photo_path, fileDates):
    for filename in os.listdir(photo_path):
        print photo_path + filename, photo_path + fileDates[filename]+"_"+filename
        os.rename(photo_path + filename, photo_path + fileDates[filename]+"_"+filename)        
     
fileDates = dateTimeGetter(photo_path)
fileRenamer(photo_path, fileDates)   

    