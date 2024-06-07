#!/usr/bin/python3
# -*- coding: utf-8 -*-
# find-geo-tags multiprocessing
#
# Поиск и отображение GPS-геотегов на изображениях в текущем каталоге.

from PIL import Image
import glob, os
from datetime import datetime
from GPSPhoto import gpsphoto
import multiprocessing
from multiprocessing import Pool

# Получаем путь к директории, где находится скрипт
dir_path = os.path.dirname(os.path.realpath(__file__))

def search(file):
    if Image:
        try:
            # Открываем файл изображения
            img = Image.open(file)
            # Получаем GPS-данные из изображения
            data = gpsphoto.getGPSData(file)
            print('В файле', file, 'найден GPS-тег: ', data['Latitude'], data['Longitude'])
        except:
            pass

if __name__ == '__main__':
    # Получаем количество ядер процессора
    cpucores = multiprocessing.cpu_count()
    # Получаем список всех файлов в текущей директории и поддиректориях
    files = glob.glob(dir_path + '/**/*.*', recursive=True)
    print('\n Выводим EXIF GPS теги рекурсивно, \n из фотографий в текущей директории \n')
    print('Нажмите любую клавишу для продолжения')
    
    startTime = datetime.now().replace(microsecond=0)
    # Создаем пул процессов
    pool = Pool(processes=cpucores + 1)
    # Применяем функцию поиска к списку файлов
    pool.map(search, files)
    endTime = datetime.now().replace(microsecond=0)

    # Выводим время, затраченное на обработку
    print(f"Затраченное время: {endTime - startTime}")
