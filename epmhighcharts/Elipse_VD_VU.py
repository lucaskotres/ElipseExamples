__author__ = 'Kotres'
from highcharts import Highchart
import datetime
import epmsdk.communication as epmcomm
import epmsdk.dataaccess as epmda
import epmsdk.historicaldata as epmhda
import numpy as np

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

rand_vd = 0
rand_vu = 0
rand_vs = 0
for obj in vd_array:
    rand_vd = np.random.random_integers(10000,14000)
    rand_vu = np.random.random_integers(6000,9000)
    rand_vs = np.random.random_integers(500,1500)

    list_vd.append(rand_vd)
    list_vu.append(rand_vu)
    list_vs.append(rand_vs)
    list_vf.append((rand_vu - rand_vs)*0.06)

H = Highchart(height=830,width=1700)


options = {
	'chart': {
        'zoomType': 'xy'
    },
    'title': {
        'text': 'VD e VU (m3)'
    },
    'subtitle': {
        'text': 'Volume disponibilizado e Volume utilizado'
    },
    'xAxis': [{
        'categories': ['Jul''12', 'Ago''12', 'Set''12', 'Out''12', 'Nov''12', 'Dez''12',
            'Jan''13', 'Fev''13', 'Mar''13', 'Abr''13', 'Mai''13', 'Jun''13','Jul''13', 'Ago''13', 'Set''13', 'Out''13', 'Nov''13', 'Dez''13',
            'Jan''14', 'Fev''14', 'Mar''14', 'Abr''14', 'Mai''14', 'Jun''14','Jul''14', 'Ago''14', 'Set''14', 'Out''14', 'Nov''14', 'Dez''14',
            'Jan''15', 'Fev''15', 'Mar''15', 'Abr''15', 'Mai''15', 'Jun''15','Jul''15'
            ],
        'crosshair': True
    }],
    'yAxis': [{
        'labels': {
            'format': 'R$ {value}',
            'style': {
                'color': 'Highcharts.getOptions().colors[3]'
            }
        },
        'title': {
            'text': 'Valor Faturado',
            'style': {
                'color': 'Highcharts.getOptions().colors[3]'
            }
        },
        'opposite': True

    }, {
        'gridLineWidth': 0,
        'title': {
            'text': 'Volume',
            'style': {
                'color': 'Highcharts.getOptions().colors[1]'
            }
        },
        'labels': {
            'format': '{value} m3',
            'style': {
                'color': 'Highcharts.getOptions().colors[1]'
            }
        }

    }],
    'tooltip': {
        'shared': True,

    },
    'legend': {
        'enabled':True
    },
}
H.set_dict_options(options)

H.add_data_set(list_vd, 'area', 'Volume Distribuido', yAxis=1, tooltip={
                'valueSuffix': ' m3'})
H.add_data_set(list_vu, 'area', 'Volume Utilizado', yAxis=1 ,marker={
                'enabled': False
            },
            tooltip={
                'valueSuffix': ' m3'
            })

H.add_data_set(list_vs, 'area', 'Volume Social',yAxis=1, tooltip={
                'valueSuffix': ' m3'
            })
H.add_data_set(list_vf, 'spline', 'Total Faturado', tooltip={
                'valueSuffix': ' $'
            })


H.save_file('Elipse_VD_VU')

