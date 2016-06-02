import epmsdk.communication as epmcomm
import epmsdk.dataaccess as epmda
import epmsdk.historicaldata as epmhda

import datetime

TAGNAME = 'wb_Tin'
SERVER = 'localhost'
USER = 'sa'
PSW = 'admin'

conexao = epmcomm.epmConnect(hostname=SERVER, username=USER, password=PSW)

data_object = epmda.epmGetDataObjectAnnotation(conexao, TAGNAME)

dataInicial = datetime.datetime(year=2016, month=3, day=1)
dataFinal = datetime.datetime(year=2016, month=4, day=1)

array = epmhda.epmTagHistoryRead(data_object, dataInicial, dataFinal)

print array
