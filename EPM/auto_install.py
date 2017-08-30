import urllib2
import os
import datetime

begin_time = datetime.datetime.now()

if str.upper(raw_input('Tem certeza que deseja prosseguir? S/N')) == 'N':
    exit(1)


PATH = 'C:\Program Files\Elipse Software\EpmServer\Pythonx64\\'
PIP_PATH = 'C:\Program Files\Elipse Software\EpmServer\Pythonx64\Scripts\\'

URL_GETPIP = "https://bootstrap.pypa.io/get-pip.py"

URL_NUMPYMKL = "https://github.com/ryanbaumann/NMEA_GPS_Server/raw/master/python_wheels/numpy-1.11.0+mkl-cp27-cp27m-win_amd64.whl"
URL_SCIPY = "https://github.com/timmwagener/general_purpose_nodes_vendor/raw/master/scipy-0.18.1-cp27-cp27m-win_amd64.whl"

#download pip
print('downloading pip...\n')

file_name = PATH+URL_GETPIP.split('/')[-1]
u = urllib2.urlopen(URL_GETPIP)
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
    status = status + chr(8)*(len(status)+1)
    print status,

f.close()

#execute install pip
print('Installing pip...\n')
os.chdir(PATH)
os.system("python.exe "+URL_GETPIP.split('/')[-1])


#uninstall numpy
print('uninstalling numpy...\n')
os.chdir(PIP_PATH)
os.system('pip uninstall numpy')


#download numpy+mkl
print('downloading numpy+mkl...\n')

file_name = PIP_PATH+URL_NUMPYMKL.split('/')[-1]
u = urllib2.urlopen(URL_NUMPYMKL)
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
    status = status + chr(8)*(len(status)+1)
    print status,

f.close()

#install numpy+mkl
print('installing numpy+mkl...\n')
os.system('pip install '+URL_NUMPYMKL.split('/')[-1])


#download scipy
print('downloading scipy...\n')

file_name = PIP_PATH+URL_SCIPY.split('/')[-1]
u = urllib2.urlopen(URL_SCIPY)
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
    status = status + chr(8)*(len(status)+1)
    print status,

f.close()


#install scipy
print('installing scipy...\n')
os.system('pip install '+URL_SCIPY.split('/')[-1])

end_time = datetime.datetime.now() - begin_time
print('End auto install. Elapsed: '+ str(end_time))


