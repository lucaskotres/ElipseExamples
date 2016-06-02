# -*- coding: utf-8 -*-

import pandas as pd
import numpy as np
from datareader import getdata



##Módulos do EPM SDK para linguagem Python
import epmsdk
import epmsdk.communication as epmcomm
import epmsdk.dataaccess as epmda
import epmsdk.historicaldata as epmhda

from epmsdk.dataaccess.valuequality import ValueQuality

#variáveis

coluna = []

##Conexão ao EPM
SrvEntryName = 'localhost'
UserAuthName = 'sa'
UserAuthPass = 'admin'
ConnectionArgs = (None, None, SrvEntryName, UserAuthName, UserAuthPass,)
try:

    epmserver = epmcomm.epmConnect(*ConnectionArgs)
except epmsdk.EpmException as ex:
    print 'Connection error: {}'.format(epmsdk.EpmExceptionCode[ex.Code])
    print 'Details: {!r}'.format(ex)
    raw_input('Program should stop now!')
    exit(1)
print 'Connection Succeeded!'

##Escolha das datas
##http://pandas.pydata.org/pandas-docs/stable/timeseries.html
dayLength = 24*60  # em minutos
dateLength = 31*dayLength
dates = pd.date_range('20160501',periods=dateLength, freq='1min')


##Leitura do DAT
desc = np.dtype([('Value','>f8'),('Timestamp','object'),('Quality','object')])
dataTmp = np.empty([2], dtype=desc) #quantidade de dados

values = getdata('d00.dat') #busca valores - datareader.py
#values = values[np.logical_not(np.isnan(values))] #remove nans
j = 0
for j in range(3):
    line = values[j,:]


    for item in column:
        dataTmp['Value'] = item
        dataTmp['Timestamp'] = dates[i].to_datetime()
        dataTmp['Quality'] = ValueQuality(192)

        print dataTmp
        print 'gravando...', str(j)

        try:
            basic_variable = epmda.epmGetDataObject(epmserver,'coluna'+str(j))
        except epmsdk.EpmException as ex:
            print'Erro ao buscar a Basic Variable no EPM!{}'.format(ex)
            exit(1)

        try:
            epmhda.epmTagHistoryUpdate(basic_variable,dataTmp)
        except epmsdk.EpmException as ex:
            print'Erro ao gravar os dados no EPM!{}'.format(ex)
            exit(2)
        print 'Escrita OK!'


