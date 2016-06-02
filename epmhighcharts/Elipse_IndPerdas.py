#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
Indice de Perdas - Elipse
'''
from highcharts import Highchart
import datetime

import epmsdk
import epmsdk.communication as epmcomm
import epmsdk.dataaccess as epmda
import epmsdk.historicaldata as epmhda

def create_epm_connection(server, user, psw):
    try:
        connection = epmcomm.epmConnect(None, None, server, user, psw)

    except epmsdk.EpmException as ex:
        print 'Connection error: {}'.format(epmsdk.EpmExceptionCode[ex.Code])
        print 'Details: {!r}'.format(ex)
        exit(1)
    print 'Connection Succeeded!'
    return connection

def get_epm_dataobject(conn, obj_name, time_days):
    try:
        data_object = epmda.epmGetDataObject(conn, target=obj_name)
    except epmsdk.EpmException as ex:
        print 'GetDataObject error: {}'.format(epmsdk.EpmExceptionCode[ex.Code])
        print 'Details: {!r}'.format(ex)
        exit(1)
    print 'GetDataObject Succeeded!'

    utcNow = datetime.datetime.now()
    init_date = utcNow - datetime.timedelta(days=time_days)

    try:
        obj_array = epmhda.epmTagHistoryRead(data_object, init_date, utcNow)
    except epmsdk.EpmException as ex:
        print 'TagHistoryRead error: {}'.format(epmsdk.EpmExceptionCode[ex.Code])
        print 'Details: {!r}'.format(ex)
        exit(1)
    print 'TagHistoryRead Succeeded!'
    return obj_array


dt_obj='IP_Ipero'

server = 'localhost'
user = 'sa'
psw = 'Abcd1234'
ConnectionArgs = (server, user, psw)

connection = create_epm_connection(*ConnectionArgs)

indice_perdas = get_epm_dataobject(connection, dt_obj, 2000)


list_indice_perdas = []
for obj in indice_perdas:
    list_indice_perdas.append([obj['Timestamp'],obj['Value']])

chart = Highchart(height=830,width=1700)
chart.set_options('chart', {'zoomType': 'x'})

options = {
    'title': {
        'text': 'Indice de Perdas(L/lig.dia)'
    },
    'subtitle': {
        'text': ''
    },
    'xAxis': {
        'type': 'datetime',

        'reversed': False,
        'title': {
            'enabled': True,
            'text': 'Meses'
        },
        'maxPadding': 0.05,
        'showLastLabel': True
    },
    'yAxis': {
        'title': {
            'text': 'L/lig.dia'
        }
        },
    'plotOptions':{
        'line': {
            'dataLabels':{
             'enabled':True,
             'format':'{point.y:.2f}'
        }
        }
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

chart.add_data_set(list_indice_perdas, 'line', 'Indice de Perdas', marker={'enabled': True})

try:
    chart.save_file('Elipse_IndicePerdas')
except:
    print 'Html file error!'
print 'Html created!'

