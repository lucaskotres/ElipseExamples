#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unicodecsv as csv
import datetime
import epmsdk.communication as epmcomm
import epmsdk.dataaccess as epmda
import epmsdk.historicaldata as epmhda
import numpy as np

connection = epmcomm.epmConnect(hostname='localhost',username='sa',password='Abcd1234')
vv_fernandes1 = epmda.epmGetDataObject(connection,target='Vazao_NovaTrabalhadores')
vs_fernandes1 = epmda.epmGetDataObject(connection,target='Succao_NovaTrabalhadores')
vr_fernandes1 = epmda.epmGetDataObject(connection,target='Recalque_NovaTrabalhadores')
vp_fernandes1 = epmda.epmGetDataObject(connection,target='PontoCritico_NovaTrabalhadores')

utcNow = datetime.datetime.now() #busca a data/hora atual
init_date = utcNow - datetime.timedelta(days=2000)
vv_array = epmhda.epmTagHistoryRead(vv_fernandes1, init_date,utcNow) #retorna os dados com valor, qualidade e timestamp do tag.
vs_array  = epmhda.epmTagHistoryRead(vs_fernandes1, init_date,utcNow)
vr_array  = epmhda.epmTagHistoryRead(vr_fernandes1, init_date,utcNow)
vp_array  = epmhda.epmTagHistoryRead(vp_fernandes1, init_date,utcNow)


list_vv = []
list_vs = []
list_vr = []
list_vp = []
list_dt = []

for obj in vv_array:
    list_vv.append(obj['Value'])

for obj in vs_array:
    list_vs.append(obj['Value'])

for obj in vr_array:
    list_vr.append(obj['Value'])

for obj in vp_array:
    list_vp.append(obj['Value'])


for obj in vv_array:
    list_dt.append(obj['Timestamp'])


list_titulo = []
list_titulo.append('   Data')
list_titulo.append('   Vazao (L/s)')
list_titulo.append('   Succao (mca)')
list_titulo.append('   Recalque (mca)')
list_titulo.append('   Ligacoes ')






with open('ElipseTable.csv', 'wb') as myfile:
    wr = csv.writer(myfile, quoting=csv.QUOTE_ALL)
    wr.writerow(list_titulo)
    i = 0
    while i < len(list_vv):
        wr.writerow([list_dt[i],list_vv[i],list_vs[i],list_vr[i],list_vp[i]])
        i = i + 1




csvFile = open('ElipseTable.csv')#enter the csv filename
csvReader = csv.reader(csvFile)
csvData = list(csvReader)


with open('ElipseTable.html', 'w') as html: #enter the output filename
    html.write('''<!-- Latest compiled and minified CSS -->
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/bootstrap-table/1.8.1/bootstrap-table.min.css">

<!-- Latest compiled and minified CSS -->
<link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.5/css/bootstrap.min.css">
''')
    html.write('<table data-toggle = "table" data-pagination = "true">\r')
    r = 0
    for row in csvData:
        if r == 0:
            html.write('\t<thead>\r\t\t<tr>\r')
            for col in row:
                html.write('\t\t\t<th data-sortable="true">' + col + '</th>\r')
            html.write('\t\t</tr>\r\t</thead>\r')
            html.write('\t<tbody>\r')
        else:
            html.write('\t\t<tr>\r')
            for col in row:
                html.write('\t\t\t<td>' + col + '</td>\r')
            html.write('\t\t</tr>\r')

        r += 1
    html.write('\t</tbody>\r')
    html.write('</table>\r')

    html.write('''
<!-- jQuery (necessary for Bootstrap's JavaScript plugins) -->
<script src="https://ajax.googleapis.com/ajax/libs/jquery/2.1.0/jquery.min.js"></script>

<!-- Latest compiled and minified JavaScript -->
<script src="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.5/js/bootstrap.min.js"></script>

<!-- Latest compiled and minified JavaScript -->
<script src="https://cdnjs.cloudflare.com/ajax/libs/bootstrap-table/1.8.1/bootstrap-table.min.js"></script>
''')