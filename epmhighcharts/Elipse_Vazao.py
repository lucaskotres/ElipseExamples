#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'Kotres'

#*****************************************************
#  VAZAO - ELIPSE                               *
#*****************************************************

from highcharts import Highchart
from highcharts import Highstock


###EPM
import datetime
import epmsdk.communication as epmcomm
import epmsdk.dataaccess as epmda
import epmsdk.historicaldata as epmhda

connection = epmcomm.epmConnect(hostname='localhost',username='sa',password='Abcd1234')
ip = epmda.epmGetDataObject(connection,target='Vazao_NovaTrabalhadores')

utcNow = datetime.datetime.now() #busca a data/hora atual
init_date = utcNow - datetime.timedelta(days=2000)
fin_date = utcNow - datetime.timedelta(days=112)
ip_array = epmhda.epmTagHistoryRead(ip, init_date,fin_date) #retorna os dados com valor, qualidade e timestamp do tag.




list_ip = []
for obj in ip_array:
    list_ip.append([obj['Timestamp'],obj['Value']])




chart = Highstock(height=830,width=1700)
chart.set_options('chart', {'zoomType': 'x'})

options = {
        'rangeSelector' : {
            'buttons':[{'type':'day', 'count':1,'text':'1d'},
                       {'type':'week', 'count':1,'text':'1w'},
                       {'type':'month', 'count':1,'text':'1m'},
                       {'type':'all', 'text':'All'}
                       ],

            'selected' : 3
    },

    'title': {
        'text': 'Gráfico de Vazão '
    },
    'subtitle': {
        'text': 'm3/s'
    },
    'xAxis': {
        'type': 'datetime',

        'reversed': False,
        'title': {
            'enabled': True,
            'text': 'Data/Hora'


        },
        'maxPadding': 0.05,
        'showLastLabel': True
    },
    'yAxis': {
        'title': {
            'text': 'Vazão'
        }
        },
    'plotOptions':{
        'line': {
            'dataLabels':{
             'enabled':False
        }
        }

    },

    'legend': {
        'enabled': False
    },
    'tooltip': {
        'headerFormat': '<b>Vazão</b><br/>',
        'pointFormat': '{point.y:.2f} m3'
    }
}

chart.set_dict_options(options)



print list_ip
#chart.add_data_set(value, 'spline', 'Temperatura', marker={'enabled': False})
chart.add_data_set(list_ip, 'spline', 'Vazão', marker={'enabled': True})


chart.save_file('Elipse_Vazao')

