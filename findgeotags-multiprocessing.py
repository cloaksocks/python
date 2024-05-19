#!/usr/bin/python3
# -*- coding: utf-8 -*-
# find-geo-tags multiprocessing
#
# Search and display GPS geotags from images in the current directory.
#
# Поиск и отображение GPS-геотегов на изображениях в текущем каталоге.

from PIL import Image
import glob, os
from datetime import datetime
import pause
from GPSPhoto import gpsphoto
import multiprocessing
from multiprocessing import Pool

dir_path = os.path.dirname(os.path.realpath(__file__))

def search(file):
    if Image:
        try:
            img = Image.open(file)
            data = gpsphoto.getGPSData(file)
            print('in file', file, 'GPS tag was founded: ', data['Latitude'], data['Longitude']) 
        except:
            pass 
        
if __name__ == '__main__':
    cpucores = multiprocessing.cpu_count()
    files = glob.glob(dir_path + '/**/*.*', recursive=True)
    print('\n print exif gps tags recirsively, \n from current directory photos \n')
    print('Press Any Key To continue')
    startTime = datetime.now().replace(microsecond=0)
    pool = Pool(processes=cpucores + 1)
    
    pool.map(search, files)
    endTime = datetime.now().replace(microsecond=0)
