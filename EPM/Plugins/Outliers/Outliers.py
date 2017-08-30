# coding=utf-8

# EPM Plugins
import Plugins as ep

import matplotlib.pyplot as plt
import matplotlib.mlab as mlab

import numpy as np


@ep.DatasetFunctionPlugin('Remover Outliers', 1)
def removeoutlier():
    if len(ep.EpmDatasetPens.SelectedPens) != 1:
        ep.showMsgBox("EPM - Histograma",
                      "Execute a consulta do Dataset Analysis \n e selecione uma pena antes de aplicar a funcao.",
                      "Warning")
        return 0

    epm_tag = ep.EpmDatasetPens.SelectedPens[0].Values
    
    FATOR = 1.5
    values = epm_tag["Value"]

    q3, q1 = np.percentile(values, [75, 25])
    iqr = q3 - q1

    lowpass = q1 - (iqr * FATOR)

    highpass = q3 + (iqr * FATOR)   


    epmarray = np.dtype([('Value','>f8'),('Timestamp','object'),('Quality','object')])


    print data 

    ep.plotValues('No_Outliers',values)