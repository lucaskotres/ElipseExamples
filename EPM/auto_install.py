import urllib2
import os
import datetime

PATH = 'C:\Program Files\Elipse Software\EpmServer\Pythonx64\\'
PIP_PATH = 'C:\Program Files\Elipse Software\EpmServer\Pythonx64\Scripts\\'

URL_GETPIP = "https://bootstrap.pypa.io/get-pip.py"
URL_NUMPYMKL = "https://github.com/ryanbaumann/NMEA_GPS_Server/raw/master/python_wheels/numpy-1.11.0+mkl-cp27-cp27m-win_amd64.whl"
URL_SCIPY = "https://github.com/timmwagener/general_purpose_nodes_vendor/raw/master/scipy-0.18.1-cp27-cp27m-win_amd64.whl"

if str.upper(raw_input('Tem certeza que deseja prosseguir? S/N\n')) == 'N':
    exit(1)

begin_time = datetime.datetime.now()

def downloader(path, url):
    file_name = path + url.split('/')[-1]
    u = urllib2.urlopen(url)
    f = open(file_name, 'wb')
    meta = u.info()
    file_size = int(meta.getheaders("Content-Length")[0])
    print "Downloading: %s Bytes: %s" % (file_name, file_size)

    file_size_dl = 0
    block_sz = 8192
    while True:
        buffer = u.read(block_sz)
        if not buffer:
            break

        file_size_dl += len(buffer)
        f.write(buffer)
        status = r"%10d  [%3.2f%%]" % (file_size_dl, file_size_dl * 100. / file_size)
        status = status + chr(8) * (len(status) + 1)
        print status,
    f.close()

#download and install pip
print('\ndownloading pip...')
downloader(PATH,URL_GETPIP)
print('\nInstalling pip...')
os.chdir(PATH)
os.system("python.exe "+URL_GETPIP.split('/')[-1])

#uninstall numpy
print('\nuninstalling numpy...')
os.chdir(PIP_PATH)
os.system('pip uninstall numpy')

#download and install numpy+mkl
print('\ndownloading numpy+mkl...')
downloader(PIP_PATH,URL_NUMPYMKL)
print('\ninstalling numpy+mkl...')
os.system('pip install '+URL_NUMPYMKL.split('/')[-1])

#download and install scipy
print('\ndownloading scipy...')
downloader(PIP_PATH,URL_SCIPY)
print('\ninstalling scipy...')
os.system('pip install '+URL_SCIPY.split('/')[-1])

elapsed = datetime.datetime.now() - begin_time
print('\nEnd auto install. Elapsed: ' + str(elapsed))