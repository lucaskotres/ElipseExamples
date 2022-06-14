# -*- coding: utf-8 -*-

import win32com.client

class e3comm(object):

    def __init__(self):

        self.eComCall = win32com.client.Dispatch("E3DataAccess.E3DataAccessManager.1")

    def getValue(self,e3path):

        Timestamp = 0
        Quality = 0
        Value = 0

        read = self.eComCall.ReadValue(e3path,Timestamp,Quality,Value)

        if read[0]:
            print(e3path ,"Success read!")
            return read
        else:
            print(e3path, "Fail read!")
            return False



    def sendValue(self, e3path, Value, Timestamp, Quality):

        tagwrite = self.eComCall.WriteValue(e3path, Timestamp, Quality, Value)

        if tagwrite:
            print(e3path,"Success write!")
        else:
            print(e3path,"Fail write!")

        return tagwrite


#TODO:Callbacks


#Teste

'''
E3 = e3comm()
tagpath = "Dados.TagInterno1"
temp = E3.getValue(e3path=tagpath)
import datetime
E3.sendValue(e3path=tagpath,Value=400,Timestamp=datetime.datetime.now(),Quality=192)
'''
