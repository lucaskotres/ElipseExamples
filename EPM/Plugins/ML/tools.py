# coding=utf-8

# Tools for Statistics/Machine Learning

import numpy as np
from sklearn import linear_model
import matplotlib.pyplot as plt
import pandas as pd
import statsmodels.api as sm
import statsmodels.formula.api as smf 


def plot(data):

    plt.plot(data)
    plt.show()
    


def np2pd(epmarray):
    '''Return Pandas dataframe for EPM numpy array'''
    return pd.DataFrame({'value':epmarray['Value'], 'timestamp':epmarray['Timestamp'],'quality':epmarray['Quality']})

from statsmodels.tsa.stattools import adfuller


def test_stationarity(timeseries):

    # Determing rolling statistics
    rolmean = pd.rolling_mean(timeseries, window=12)
    rolstd = pd.rolling_std(timeseries, window=12)

    # Plot rolling statistics:
    orig = plt.plot(timeseries, color='blue', label='Original')
    mean = plt.plot(rolmean, color='red', label='Rolling Mean')
    std = plt.plot(rolstd, color='black', label='Rolling Std')
    plt.legend(loc='best')
    plt.title('Rolling Mean & Standard Deviation')
    plt.show(block=False)

    # Perform Dickey-Fuller test:
    print 'Results of Dickey-Fuller Test:'
    dftest = adfuller(timeseries, autolag='AIC')
    dfoutput = pd.Series(dftest[0:4], index=[
                         'Test Statistic', 'p-value', '#Lags Used', 'Number of Observations Used'])
    for key, value in dftest[4].items():
        dfoutput['Critical Value (%s)' % key] = value
    print dfoutput


def print_OLS(data):
    '''Show ordinary least squares'''
    results = sm.OLS(data).fit()
    return results.summary()








