#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''Elipse Plant Manager - Conecta em servidores EPM e busca DataObjects
Copyright (C) 2015 Elipse Software.
'''
__author__ = 'Kotres'

#para gerar logs
import logging

#para criptografia dos dados
from django.core import signing


import epmsdk
import epmsdk.communication as epmcomm
import epmsdk.dataaccess as epmda
import epmsdk.historicaldata as epmhda
from epmsdk.historicaldata.timeperiod import TimePeriod



#geração de logs
logger = logging.getLogger(__name__)

#implementar uso de cookies e sessions

class Connection(object):

    def create_connection(self, server, user, psw):
        try:
            connection = epmcomm.epmConnect(None,None, server, user, psw)

        except epmsdk.EpmException as ex:
            logger.error( 'Connection error: {}',epmsdk.EpmExceptionCode[ex.Code])
            logger.error( 'Details: {!r}',ex)
            out = 'Connection error: ', epmsdk.EpmExceptionCode[ex.Code]
            return out
        logger.info(server, 'Connection Succeeded!')
        return connection

    '''
    verificar status da session no servidor
    def status_session(self,conn):
    '''

    '''
    enviar GetDataObject para manter sessão aberta
    def preserve_session(self, conn):
    '''

class GetDataObject(object):

    #feature - filter with regex
    def get_basicvariableslist(self,connection):

        allobjects = epmda.epmGetAllBasicVariablesToSeq(connection)

        names = [item.DisplayName for item in allobjects]

        #return signing.dumps(names,compress=True) # para criptografia e compressão
        return names

    #feature -  filter with regex
    def get_expressionvariableslist(self,connection):

        allobjects = epmda.epmGetAllExpressionVariablesToSeq(connection)
        names = [item.DisplayName for item in allobjects]

        #return signing.dumps(names,compress=True) # desmarcar para usar criptografia e compressão
        return names

    #no tested
    def quality_filter(self, dataobject):

        if epmda.isGood(dataobject):
            return True
        else:
            return False


    def get_raw_data(self, connection, obj_name, init_date, end_date):

        try:
            data_object = epmda.epmGetDataObject(connection, target=obj_name)
        except epmsdk.EpmException as ex:
            logger.error( 'GetDataObject error: {}'.format(epmsdk.EpmExceptionCode[ex.Code]))
            logger.error( 'Details: {!r}'.format(ex))
            out = 'GetDataObject error: ',epmsdk.EpmExceptionCode[ex.Code]
            return out

        try:
            obj_array = epmhda.epmTagHistoryRead(data_object, init_date, end_date)
        except epmsdk.EpmException as ex:
            logger.error( 'TagHistoryRead error: {}',epmsdk.EpmExceptionCode[ex.Code])
            logger.error( 'Details: {!r}',ex)
            out = 'TagHistoryRead error: ',epmsdk.EpmExceptionCode[ex.Code]
            return out
        logger.info( obj_name,'Read!  Length:',len(obj_array))

        #return signing.dumps(obj_array,compress=True) - desmarcar para usar criptografia e compressão
        return obj_array




    def get_aggregate_data(self, connection, obj_name, aggregate_args, start_time, end_time):
        try:
            data_object = epmda.epmGetDataObject(connection, target=obj_name)
        except epmsdk.EpmException as ex:
            logger.error( 'GetDataObject error: {}',epmsdk.EpmExceptionCode[ex.Code])
            logger.error( 'Details: {!r}',ex)
            out = 'GetDataObject error: ',epmsdk.EpmExceptionCode[ex.Code]
            return out

        try:

            timeperiod = TimePeriod(start_time,end_time)


            obj_array = epmhda.epmTagHistoryReadAggregate(data_object, aggregate_args,timeperiod)
        except epmsdk.EpmException as ex:
            logger.error('TagHistoryRead error: {}',epmsdk.EpmExceptionCode[ex.Code])
            logger.error('Details: {!r}',ex)

        logger.info( obj_name,'Read!  Length:',len(obj_array))
        #return signing.dumps(obj_array,compress=True) - desmarcar para usar criptografia e compressão
        return obj_array
