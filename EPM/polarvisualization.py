# -*- coding: utf-8 -*-


import numpy as np
import datetime
import matplotlib.pyplot as plt
import pandas as pd

import epm_connection

#tools
def np2pd(epmarray):
    '''Return Pandas dataframe for EPM numpy array'''
    return pd.DataFrame({'value':epmarray['Value'], 'timestamp':epmarray['Timestamp'],'quality':epmarray['Quality']})


conn = epm_connection.Connection()
conn = conn.create_connection(server='dili',user='minicurso',psw='minicurso')

object = epm_connection.GetDataObject()

now = datetime.datetime.utcnow()
begin = now - datetime.timedelta(days=60)

data = np2pd(object.get_raw_data(connection=conn, obj_name='EPMDev_Temperature', init_date=begin, end_date=now))


print data

number_of_days = int((data['timestamp'].iloc[-1] - data['timestamp'].iloc[0])/ datetime.timedelta(days=1))

print number_of_days



##http://pandas.pydata.org/pandas-docs/stable/timeseries.html

dateLength = 31
dates = pd.date_range('20160501',periods=dateLength, freq='D')

print dates

hours = ['0:00', '1:00','2:00','3:00','4:00','5:00','6:00','7:00','8:00','9:00','10:00','11:00','12:00','13:00','14:00','15:00','16:00','17:00','18:00','19:00','20:00','21:00','22:00','23:00']


# Compute pie slices
N = 20
theta = np.linspace(0.0, 2 * np.pi, N, endpoint=False)
width = np.pi / 4 * np.random.rand(N)
radii = 10 * np.random.rand(N)

ax = plt.subplot(111, projection='polar')
ax.set_yticklabels(hours)
bars = ax.bar(theta, radii, width=width, bottom=0.0)

for r, bar in zip(radii, bars):
# Use custom colors and opacity
    bar.set_facecolor(plt.cm.viridis(r / 10.))


    bar.set_alpha(0.5)

plt.show()