#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'Kotres'

#*************************************
#   LINE CHART VD-VU - ELIPSE        *
#*************************************

from highcharts import Highchart
from highcharts import Highstock


###EPM
import datetime
import epmsdk.communication as epmcomm
import epmsdk.dataaccess as epmda
import epmsdk.historicaldata as epmhda
import numpy as np
from scipy import stats

connection = epmcomm.epmConnect(hostname='localhost',username='sa',password='Abcd1234')
vd_fernandes1 = epmda.epmGetDataObject(connection,target='VD_Fernandes1')
vu_fernandes1 = epmda.epmGetDataObject(connection,target='VU_Fernandes1')
utcNow = datetime.datetime.now() #busca a data/hora atual
init_date = utcNow - datetime.timedelta(days=2000)
vd_array = epmhda.epmTagHistoryRead(vd_fernandes1, init_date,utcNow) #retorna os dados com valor, qualidade e timestamp do tag.
vu_array  = epmhda.epmTagHistoryRead(vu_fernandes1, init_date,utcNow)


list_vd = []
list_vu = []
list_vs = []
list_vf = []
list_vp = []
list_dif = []


rand_vd = 0
rand_vu = 0
rand_vs = 0
total_vf = 0
total_vp = 0

for obj in vd_array:
    rand_vd = np.random.random_integers(10000,14000)
    rand_vu = np.random.random_integers(6000,9000)
    rand_vs = np.random.random_integers(500,1500)

    total_vf = total_vf + ((rand_vu - rand_vs)*7.87)
    total_vp = total_vp + (rand_vu * 7.87)
    list_vd.append([obj['Timestamp'], rand_vd])
    list_vu.append([obj['Timestamp'], rand_vu])
    list_vs.append([obj['Timestamp'], rand_vs])
    list_vf.append([obj['Timestamp'], (rand_vu - rand_vs)*7.87])
    list_vp.append([obj['Timestamp'], (rand_vu)*7.87])
    list_dif.append([obj['Timestamp'], total_vp - total_vf])



data_pie = [{'name': "Total Faturado", 'y':total_vf},
            {'name': "Total Perdido",  'y':total_vp-total_vf,'sliced': True},
            ]


chart = Highchart(height=830,width=1700)
chart.set_options('chart', {'zoomType': 'x'})

options = {


    'title': {
        'text': 'Faturamento Estimado e Real'
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
            'text': 'R$()'
        }
        },
    'plotOptions':{
        'line': {
            'dataLabels':{
             'enabled':True
        }
        }

    },

    'legend': {
        'enabled': True
    },
    'tooltip': {
        'headerFormat': '<b>Valor</b><br/>',
        'pointFormat': 'R$:{point.y:.2f}'
    }
}

chart.set_dict_options(options)



print list_vu
print list_vd
print list_vs
print list_vf
print list_vp
#chart.add_data_set(value, 'spline', 'Temperatura', marker={'enabled': False})
#chart.add_data_set(list_vd, 'area', 'Volume Distribuido Total', marker={'enabled': True})
#chart.add_data_set(list_vu, 'area', 'Volume Consumido', marker={'enabled': True})
#chart.add_data_set(list_vs, 'area', 'Volume Social', marker={'enabled': True})
chart.add_data_set(list_vf, 'column', 'Valor Faturado(R$)', marker={'enabled': True})
chart.add_data_set(list_vp, 'column', 'Faturamento Estimado(R$)', marker={'enabled': True})
chart.add_data_set(list_dif, 'spline', 'Total Perdas(R$)', marker={'enabled': True},visible=False)
#chart.add_data_set(data_pie, 'pie', 'Faturamento Estimado(R$)', marker={'enabled': True})

chart.save_file('Elipse_ValorFaturado')

