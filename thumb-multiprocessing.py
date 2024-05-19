#!/usr/bin/python3
# -*- coding: utf-8 -*-
#  multiprocess thumbnail creator
#  Script creates thumbnail images from all files in the specified directory and its subdirectories, using multiprocessing to speed up the process.
#  Cкрипт создает миниатюры изображений (thumbnail) из всех файлов в указанной директории и ее поддиректориях, используя многопроцессорность для ускорения процесса. 

import os
from datetime import datetime
from PIL import Image, ExifTags, ImageFile
import glob 
import multiprocessing
from multiprocessing import Pool

ImageFile.LOAD_TRUNCATED_IMAGES = True

size = 128, 128
dir_path = os.path.dirname(os.path.realpath(__file__))


def fn(infile):
    outfile = os.path.splitext(infile)[0] + ".thumbnail"
    if infile != outfile:
        try:
            im = Image.open(infile)
            try:
                im.info['exif']
                im.thumbnail(size, Image.ANTIALIAS)
                im.save(outfile, "JPEG", exif=im.info['exif'])
                print("thumbnail created for: '%s'." % outfile,)
            except:
                im.thumbnail(size, Image.ANTIALIAS)
                im.save(outfile, "PNG")
                print("thumbnail created for: '%s'." % outfile,)
        except IOError:
            print("cant create thumb for: '%s'" % infile)
            pass

                
             
if __name__ == '__main__':
    cpucores = multiprocessing.cpu_count()
    files = glob.glob(dir_path + '/**/*.*', recursive=True)
    startTime = datetime.now().replace(microsecond=0)
    pool = Pool(processes=cpucores + 1) #cpu cores + 1 : best known result
    
    pool.map(fn, files)
    endTime = datetime.now().replace(microsecond=0) 

    print('\nTime used: ', endTime - startTime)
    print('\nCPU Cores: ', cpucores)
    print('\nFlows used: ', cpucores + 1)
