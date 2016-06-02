
import epmsdk.communication as epmcomm
import epmsdk.dataaccess as epmda
import epmsdk.historicaldata as epmhda

import datetime

TAGNAME = 'wb_Tin'
SERVER = 'localhost'
USER = 'sa'
PSW = 'admin'


conexao = epmcomm.epmConnect(hostname=SERVER, username=USER, password=PSW)

data_object = epmda.epmGetDataObject(conexao, target=TAGNAME)

dataInicial = datetime.datetime(year=2016, month=3, day=1)
dataFinal = datetime.datetime(year=2016, month=4, day=1)

array = epmhda.epmTagHistoryRead(data_object, dataInicial, dataFinal)


valores = array['Value']

print valores

print "Numero de pontos:", len(array['Value'])

#media
print "Media:", valores.mean()

#desvio padrao
print "Desvio padrao:", valores.std()

#valor maximo
print "Max:", valores.max()

#valor minimo
print "Min:",valores.min()