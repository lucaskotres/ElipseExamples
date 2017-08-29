import urllib2
import os

if str.upper(raw_input('Tem certeza que deseja prosseguir? S/N')) == 'N':
    exit(1)

PATH = 'ç
PIP_PATH =

#download pip
url = "https://bootstrap.pypa.io/get-pip.py"

file_name = url.split('/')[-1]
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
    status = status + chr(8)*(len(status)+1)
    print status,

f.close()

#execute install pip
os.system('python polarvisualization.py') #TODO:substituir por get-pip.py


#uninstall numpy
os.system('pip uninstall numpy')








