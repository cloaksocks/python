#!/usr/bin/python3
# -*- coding: utf-8 -*-
# packet-image-resize
# Пакетное сжатие изображений, сжимает все изображения в каталоге,
# в котором запущен скрипт, и в его подкаталогах рекурсивно,
# до указанных значений, уменьшая разрешение фото, затем применяется antialiasing.
# оригиналы фото не сохраняются, exif метки изображений переносятся на новый файл.


from PIL import Image, ExifTags
import glob, os

dir_path = os.path.dirname(os.path.realpath(__file__))

# до такой ширины будут cжаты landscape изображения:
LAND = 2000
# до такой высоты будут сжаты portrait изображения:
PORT = 2000
# изображения со сторонами, меньшими или равными чем это значение, затронуты не будут.

# определене панорамы, всё что выше значения - панорама, или очень большое изображение, и будет сжато до этого значения:
PANORAMA = 5000
# повторные проходы скрипта не затронут сжатые ранее до этого значения файлы.

def cls():
    os.system('clear')

def resize():
    i = 0
    n = 0

    cls()
    files = glob.glob(dir_path + '/**/*.*', recursive=True)
    for file in files:
        if Image: 
            try:
                img = Image.open(file)
                (width, height, format, exif) = (img.size[0], img.size[1], img.format, img.info['exif'])
      
                if width <= height:
                    if height <= LAND:
                        i += 1
                        print('correct portrait', file ,width, 'x', height, format, 'passed')
                        pass
                    
                    else:
                        wpercent = (PORT/float(height))
                        hsize = int((float(width)*float(wpercent)))
                        img = img.resize((hsize,PORT), Image.ANTIALIAS)
                        img.save(file, exif=exif)
                        i += 1
                        n += 1
                        print('usable portrait, processing file:', file , width, 'x', height, format, 'compressed to:', hsize, 'x', LAND)          
         
                else:
                    if width > PANORAMA:
                        wpercent = (PANORAMA/float(width))
                        hsize = int((float(height)*float(wpercent)))
                        img = img.resize((PANORAMA,hsize), Image.ANTIALIAS)
                        img.save(file, exif=exif)
                        i += 1
                        n += 1
                        print('usable panorama, processing file:', file , width, 'x', height, format, 'compressed to:', PANORAMA, 'x', hsize)                
                        
                    else:
                        if width <= LAND:
                            i += 1
                            print('correct landscape', file ,width, 'x', height, format, 'passed')
                            pass
                        
                        else:
                            if width == PANORAMA:
                                i += 1
                                print('correct panorama', file  ,width, 'x', height, format, 'passed')
                                pass
                            else:
                                wpercent = (LAND/float(width))
                                hsize = int((float(height)*float(wpercent)))
                                img = img.resize((LAND,hsize), Image.ANTIALIAS)
                                img.save(file, exif=exif)
                                i += 1
                                n += 1
                                print('usable landscape, processing file:', file , width, 'x', height, format, 'compressed to:', LAND, 'x', hsize)                         
                                
            except:
                pass
            
    print('\n',i, 'pictures total,', n, 'pictures compressed.')    


def main():
    cls()
    print('\nWarning images in this directory \n can be resized and rewritten, \n original files lost !!!')
    choice = input('\nConfirm with "y" input ? --> ')                  # Запрос ввода первого меню.
    if choice == 'y':
        resize()
    else:
        pass

main()
