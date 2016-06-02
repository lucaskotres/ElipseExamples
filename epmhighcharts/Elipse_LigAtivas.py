#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'Kotres'

#************************************************
#   LIGAÇÕES ATIVAS - ELIPSE                    *
#************************************************

from highcharts import Highchart
from highcharts import Highstock


###EPM
import datetime
import epmsdk.communication as epmcomm
import epmsdk.dataaccess as epmda
import epmsdk.historicaldata as epmhda
import numpy as np

connection = epmcomm.epmConnect(hostname='localhost',username='sa',password='Abcd1234')
ip = epmda.epmGetDataObject(connection,target='Lig_Sabias')

utcNow = datetime.datetime.now() #busca a data/hora atual
init_date = utcNow - datetime.timedelta(days=2000)
ip_array = epmhda.epmTagHistoryRead(ip, init_date,utcNow) #retorna os dados com valor, qualidade e timestamp do tag.



list_den = []
list_ip = []
fator_crescimento = 0
for obj in ip_array:

    lig_ativ_rand = np.random.random_integers(800,1200)*fator_crescimento
    list_ip.append([obj['Timestamp'],lig_ativ_rand])
    list_den.append([obj['Timestamp'],lig_ativ_rand/12])
    fator_crescimento = fator_crescimento + 0.08

chart = Highchart(height=830,width=1700)
chart.set_options('chart', {'zoomType': 'x'})

options = {


    'title': {
        'text': 'Ligações Ativas e Densidade(lig/km)'
    },
    'subtitle': {
        'text': ''
    },
    'xAxis': {
        'type': 'datetime',

        'reversed': False,
        'title': {
            'enabled': True,
            'text': 'Data'


        },
        'maxPadding': 0.05,
        'showLastLabel': True
    },
    'yAxis': {
        'title': {
            'text': 'Ligações'
        }
        },
    'plotOptions':{
        'line': {
            'dataLabels':{
             'enabled':True
        }
        },
    },

    'legend': {
        'enabled': True
    },
    'tooltip': {
        'headerFormat': '<b>Valor</b><br/>',
        'pointFormat': 'L:{point.y:.2f}'
    }

}

chart.set_dict_options(options)



print list_ip
print list_den
chart.add_data_set(list_den, 'area', 'Densidade', marker={'enabled': False})
chart.add_data_set(list_ip, 'spline', 'Ligações Ativas', marker={'enabled': True},visible=False)

chart.set_options('plotOptions', {
           'column': {
                'fillColor': {
                    'linearGradient': { 'x1': 0, 'y1': 0, 'x2': 0, 'y2': 1},
                    'stops': [                          [0, "Highcharts.getOptions().colors[0]"],
                         [1, "Highcharts.Color(Highcharts.getOptions().colors[0]).setOpacity(0).get('rgba')"]
                     ]},
                 'marker': {
                     'radius': 2
                 },
                 'lineWidth': 1,
                 'states': {
                     'hover': {
                         'lineWidth': 1
                    }
                 },
                'threshold': None
            }
         })



chart.save_file('Elipse_LigacoesAtivas')
