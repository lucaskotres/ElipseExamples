#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''Elipse Plant Manager - Conecta em servidores EPM e busca DataObjects
Copyright (C) 2015 Elipse Software.
'''
__author__ = 'Kotres'

import epmsdk
import epmsdk.communication as epmcomm
import epmsdk.dataaccess as epmda
import epmsdk.historicaldata as epmhda
from epmsdk.historicaldata.timeperiod import TimePeriod



class Connection(object):

    def create_connection(self, server, user, psw):
        try:
            connection = epmcomm.epmConnect(None,None, server, user, psw)

        except epmsdk.EpmException as ex:
            print 'Connection error: {}',epmsdk.EpmExceptionCode[ex.Code]
            print 'Details: {!r}',ex
            out = 'Connection error: ', epmsdk.EpmExceptionCode[ex.Code]
            return out
        print server, 'Connection Succeeded!'
        return connection


class GetDataObject(object):


    def get_basicvariableslist(self,connection):

        allobjects = epmda.epmGetAllBasicVariablesToSeq(connection)

        names = [item.DisplayName for item in allobjects]

        return names


    def get_expressionvariableslist(self,connection):

        allobjects = epmda.epmGetAllExpressionVariablesToSeq(connection)
        names = [item.DisplayName for item in allobjects]

        return names




    def get_raw_data(self, connection, obj_name, init_date, end_date):

        try:
            data_object = epmda.epmGetDataObject(connection, target=obj_name)
        except epmsdk.EpmException as ex:
            print 'GetDataObject error: {}'.format(epmsdk.EpmExceptionCode[ex.Code])
            print 'Details: {!r}'.format(ex)
            out = 'GetDataObject error: ',epmsdk.EpmExceptionCode[ex.Code]
            return out

        try:
            obj_array = epmhda.epmTagHistoryRead(data_object, init_date, end_date)
        except epmsdk.EpmException as ex:
            print 'TagHistoryRead error: {}',epmsdk.EpmExceptionCode[ex.Code]
            print 'Details: {!r}',ex
            out = 'TagHistoryRead error: ',epmsdk.EpmExceptionCode[ex.Code]
            return out
        print obj_name,'Read!  Length:',len(obj_array)

        return obj_array




    def get_aggregate_data(self, connection, obj_name, aggregate_args, start_time, end_time):
        try:
            data_object = epmda.epmGetDataObject(connection, target=obj_name)
        except epmsdk.EpmException as ex:
            print 'GetDataObject error: {}',epmsdk.EpmExceptionCode[ex.Code]
            print 'Details: {!r}',ex
            out = 'GetDataObject error: ',epmsdk.EpmExceptionCode[ex.Code]
            return out

        try:

            timeperiod = TimePeriod(start_time,end_time)


            obj_array = epmhda.epmTagHistoryReadAggregate(data_object, aggregate_args,timeperiod)
        except epmsdk.EpmException as ex:
            print 'TagHistoryRead error: {}',epmsdk.EpmExceptionCode[ex.Code]
            print 'Details: {!r}',ex

        print obj_name,'Read!  Length:',len(obj_array)

        return obj_array
