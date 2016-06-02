import numpy as np

def getdata(file):
    array = np.loadtxt(file)
    return array

#testes
array = getdata('d00.dat')

print array
out = array[:,0]
print out.shape

