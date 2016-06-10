
import numpy as np

def removeoutlier(values):
    sd = 6
    q3 = np.floor(sd * np.sqrt(values.std()))
    qmin = values.mean() - q3
    qmax = values.mean() + q3

    outlier = np.argwhere(values > qmax)
    values = np.delete(values, outlier)

    outlier = np.argwhere(values < qmin)
    values = np.delete(values, outlier)

    return values