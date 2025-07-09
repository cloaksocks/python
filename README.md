# python
**python scripts**

**findgeotags-multiprocessing.py** -- Поиск и отображение GPS-геотегов на изображениях в текущем каталоге. / Search and display GPS geotags from images in the current directory. 

**packetimageresizer.py** -- Пакетное сжатие изображений, сжимает все изображения в каталоге. / Batch image compression, compresses all images in the catalog.

**thumb-multiprocessing.py** -- Cкрипт создает миниатюры изображений (thumbnail) из всех файлов в указанной директории и ее поддиректориях, используя многопроцессорность для ускорения процесса. / Script creates thumbnail images from all files in the specified directory and its subdirectories, using multiprocessing to speed up the process.

**update_sudo_package_1.9.17p1.py** -- обновляет версию sudo мультипоточно на списке хостов, тянет пакеты с официального https://github.com/sudo-project/sudo/releases

работает с:
debian11
debian12 
rocky9
ubuntu20.04
ubuntu22.04
ubuntu24.04
- другие дистрибутивы, пропишите в скрипте соответственно имеющимся.

для debian10 пакет отсутствует в оф. github sudo - скомпилируйте deb пакет sudo_1.9.17p1-1_amd64.deb самостоятельно и положите рядом со скриптом

файл hosts.csv дожен содержать ip хостов в виде
IP address,Hostname
192.168.1.1
192.168.2.2
...

проставьте pip модули, запустите 
python3 update_sudo_package.py
