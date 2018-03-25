# -*- coding: utf-8 -*-

import win32com.client
import datetime as dt
import numpy as np


eComCall = win32com.client.Dispatch("E3DataAccess.E3DataAccessManager.1")
print eComCall
eComCall.Server = "localhost"

tagpath = 'data.InternalTag.Value'

Timestamp = dt.datetime.now()
Quality = 192
Value = int(np.random.random_integers(0, 100, 1))

tagwrite = eComCall.WriteValue(tagpath, Timestamp, Quality, Value)

tagread = eComCall.ReadValue(tagpath, Timestamp, Quality, Value)



