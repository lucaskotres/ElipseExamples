# -*- coding: utf-8 -*-
import epmsdk
import epmsdk.communication as epmcomm
import epmsdk.dataaccess as epmda
import epmsdk.historicaldata as epmhda
import epmsdk.opcua.core as core

import datetime


def status_air():
    try:
       conn01 = epmcomm.epmConnect(hostname='kotres', username='sa', password='admin')
       print "Conectado ao EPM Server!"
    except epmsdk.EpmException as ex:
        print 'Failed on connection to EPM with error\n{}\n'.format(ex)
        exit(1)


        #Leitura das annotations
    tagTeste = epmda.epmGetDataObjectAnnotation(conn01, 'wb_Tin')

    dataInicial = datetime.datetime(year=2016, month=3, day=1)
    dataFinal = datetime.datetime(year=2016, month=4, day=1)

    try:
        hG = epmhda.epmTagHistoryRead(tagTeste, dataInicial, dataFinal)
        print unicode(hG.size)
    except epmsdk.EpmException as ex:
        print 'Failed when getting Tag with error\n{}\n'.format(ex)
        raw_input("Error on historyread")
        exit(1)
    print 'Succeeded!' 
   
    ok = []
    down=[]
    up=[]

    acc_day_OK=0.0
    acc_day_UP=0.0
    acc_day_DOWN=0.0

    days = []
    acc_days = []
    current_day=-1
    acc_day = 0
    for i in range(1,hG.size):
        date = hG[i][0]-datetime.timedelta(hours=3)
        comfort, setpoint, statusAir, T_OUT, WorkTime, NUser = hG[i][1].split(',')

        print date.day
        print statusAir.split(':')[1]
        print WorkTime.split(':')[1]

        if current_day != date.day:
            days.append(date.day)
            acc_days.append(acc_day)
            current_day = date.day
            acc_day=0
            
            if statusAir.split(':')[1] == 'ON' and WorkTime.split(':')[1]=='n':
                acc_day =1
        else:
            if statusAir.split(':')[1] == 'ON' and WorkTime.split(':')[1]=='n':
                acc_day =acc_day+1



    return days, acc_days 








def comfort_workTime_totalMonth():
    days, up, down, ok = comfort_workTime()
    
    total_up = sum(up)
    total_down = sum(down)
    total_ok = sum(ok)

    total_hours = total_ok + total_down + total_ok
    
    total_ok = (total_ok*100)/total_hours
    total_down = (total_down*100)/total_hours
    total_up = (total_up*100)/total_hours

    return len(days), total_down,total_ok,total_up


def comfort_workTime():

    try:
       conn01 = epmcomm.epmConnect(hostname='kotres', username='sa', password='admin')
       print "Conectado ao EPM Server!"
    except epmsdk.EpmException as ex:
        print 'Failed on connection to EPM with error\n{}\n'.format(ex)
        exit(1)


        #Leitura das annotations
    tagTeste = epmda.epmGetDataObjectAnnotation(conn01, 'wb_Tin')

    dataInicial = datetime.datetime(year=2016, month=3, day=1)
    dataFinal = datetime.datetime(year=2016, month=4, day=1)

    try:
        hG = epmhda.epmTagHistoryRead(tagTeste, dataInicial, dataFinal)
        print unicode(hG.size)
    except epmsdk.EpmException as ex:
        print 'Failed when getting Tag with error\n{}\n'.format(ex)
        raw_input("Error on historyread")
        exit(1)
    print 'Succeeded!' 
   
    ok = []
    down=[]
    up=[]


    acc_day_OK=0.0
    acc_day_UP=0.0
    acc_day_DOWN=0.0

    days = []

    for i in range(1,hG.size):
   
        date = hG[i][0]-datetime.timedelta(hours=3)
        previous_date = hG[i-1][0]-datetime.timedelta(hours=3)

        comfort, setpoint, statusAir, T_OUT, WorkTime, NUser = hG[i][1].split(',')
        previous_comfort,previous_setpoint, previous_statusAir, previous_T_OUT, previous_WorkTime, previous_NUser = hG[i-1][1].split(',')

        WorkTime = str(WorkTime.split(':')[1])
        comfort= str(comfort.split(':')[1])

        previous_WorkTime = str(previous_WorkTime.split(':')[1])
        previous_comfort= str(previous_comfort.split(':')[1])

        if WorkTime == 'y' and previous_WorkTime == 'y':
            #Dias diferentes -> Calula ate as 18:00 do mesmo dia e acaba a analise
            if previous_date.day!=date.day:
                
                if previous_date.hour<18:
                    diff_hours= float(((datetime.datetime(year=previous_date.year, month= previous_date.month, day= previous_date.day,hour=18,minute=0)- previous_date).seconds)/60)/60

                    if previous_comfort == 'UP':
                        acc_day_UP = acc_day_UP + diff_hours
                    elif previous_comfort == 'OK':
                        acc_day_OK = acc_day_OK + diff_hours
                    else:
                        acc_day_DOWN = acc_day_DOWN + diff_hours

                up.append(float('%.2f'% acc_day_UP))
                down.append(float('%.2f'% acc_day_DOWN))
                ok.append(float('%.2f'% acc_day_OK))
         
       
                acc_day_UP = 0.0
                acc_day_OK = 0.0
                acc_day_DOWN = 0.0

                days.append(previous_date.day)

                #Calula ate as 8:00 do mesmo dia
                diff_hours= float(((date - datetime.datetime(year=date.year, month= date.month, day= date.day,hour=8,minute=0)).seconds)/60)/60
                if previous_comfort == 'UP':
                    acc_day_UP = acc_day_UP + diff_hours
                elif previous_comfort == 'OK':
                    acc_day_OK = acc_day_OK + diff_hours
                else:
                    acc_day_DOWN = acc_day_DOWN + diff_hours

            #Mesmo dia
            else:
                diff_hours= float(((date - previous_date).seconds)/60)/60

                if previous_comfort == 'UP':
                    acc_day_UP = acc_day_UP + diff_hours
                elif previous_comfort == 'OK':
                    acc_day_OK = acc_day_OK + diff_hours
                else:
                    acc_day_DOWN = acc_day_DOWN + diff_hours

        elif WorkTime == 'y' and previous_WorkTime == 'n':
            #Dias diferentes -> Calula ate as 18:00 do mesmo dia e acaba a analise
            if previous_date.day!=date.day:
                #É expediente
                if previous_date.hour<18:
                    diff_hours= float(((datetime.datetime(year=previous_date.year, month= previous_date.month, day= previous_date.day,hour=18,minute=0)- previous_date).seconds)/60)/60           
                    if previous_comfort == 'UP':
                        acc_day_UP = acc_day_UP + diff_hours
                    elif previous_comfort == 'OK':
                        acc_day_OK = acc_day_OK + diff_hours
                    else:
                        acc_day_DOWN = acc_day_DOWN + diff_hours

                up.append(float('%.2f'% acc_day_UP))
                down.append(float('%.2f'% acc_day_DOWN))
                ok.append(float('%.2f'% acc_day_OK))
       
                acc_day_UP = 0.0
                acc_day_OK = 0.0
                acc_day_DOWN = 0.0

                days.append(previous_date.day)

                #Calula ate as 8:00 do mesmo dia
                diff_hours= float(((date - datetime.datetime(year=date.year, month= date.month, day= date.day,hour=8,minute=0)).seconds)/60)/60
                if previous_comfort == 'UP':
                    acc_day_UP = acc_day_UP + diff_hours
                elif previous_comfort == 'OK':
                    acc_day_OK = acc_day_OK + diff_hours
                else:
                    acc_day_DOWN = acc_day_DOWN + diff_hours

            #Mesmo dia
            else:
                if previous_date.hour<8:
                    diff_hours= float(((date - datetime.datetime(year=date.year, month= date.month, day= date.day,hour=8,minute=0)).seconds)/60)/60

                    if previous_comfort == 'UP':
                        acc_day_UP = acc_day_UP + diff_hours
                    elif previous_comfort == 'OK':
                        acc_day_OK = acc_day_OK + diff_hours
                    else:
                        acc_day_DOWN = acc_day_DOWN + diff_hours
            


 
        elif WorkTime == 'n' and previous_WorkTime == 'y':

            if previous_date.day!=date.day:

                #É expediente
                diff_hours= float(((datetime.datetime(year=previous_date.year, month= previous_date.month, day= previous_date.day,hour=18,minute=0)- previous_date).seconds)/60)/60           
                if previous_comfort == 'UP':
                    acc_day_UP = acc_day_UP + diff_hours
                elif previous_comfort == 'OK':
                    acc_day_OK = acc_day_OK + diff_hours
                else:
                    acc_day_DOWN = acc_day_DOWN + diff_hours

                up.append(float('%.2f'% acc_day_UP))
                down.append(float('%.2f'% acc_day_DOWN))
                ok.append(float('%.2f'% acc_day_OK))
       
                acc_day_UP = 0.0
                acc_day_OK = 0.0
                acc_day_DOWN = 0.0

                days.append(previous_date.day)
                             
            #mesmo dia
            else:
                if date.hour>=18:
                    diff_hours= float(((datetime.datetime(year=previous_date.year, month= previous_date.month, day= previous_date.day,hour=18,minute=0)-previous_date).seconds)/60)/60

                    if previous_comfort == 'UP':
                        acc_day_UP = acc_day_UP + diff_hours
                    elif previous_comfort == 'OK':
                        acc_day_OK = acc_day_OK + diff_hours
                    else:
                        acc_day_DOWN = acc_day_DOWN + diff_hours
                else:
                    diff_hours= float(((date - previous_date).seconds)/60)/60

                    if previous_comfort == 'UP':
                        acc_day_UP = acc_day_UP + diff_hours
                    elif previous_comfort == 'OK':
                        acc_day_OK = acc_day_OK + diff_hours
                    else:
                        acc_day_DOWN = acc_day_DOWN + diff_hours

        # worktime e previous_worktime ==n
        elif WorkTime == 'n' and previous_WorkTime == 'n':
            if previous_date.day!=date.day:
                up.append(float('%.2f'% acc_day_UP))
                down.append(float('%.2f'% acc_day_DOWN))
                ok.append(float('%.2f'% acc_day_OK))
       
                acc_day_UP = 0.0
                acc_day_OK = 0.0
                acc_day_DOWN = 0.0

                days.append(previous_date.day)
            


        #adicina o ultimo porque a ultima anotação não muda o dia
        if i==hG.size-1:
            if date.hour>=18:

                diff_hours= float(((datetime.datetime(year=previous_date.year, month= previous_date.month, day= previous_date.day,hour=18,minute=0)-previous_date).seconds)/60)/60

                if previous_comfort == 'UP':
                    acc_day_UP = acc_day_UP + diff_hours
                elif previous_comfort == 'OK':
                    acc_day_OK = acc_day_OK + diff_hours
                else:
                    acc_day_DOWN = acc_day_DOWN + diff_hours
            else:
                diff_hours= float(((date - previous_date).seconds)/60)/60

                if previous_comfort == 'UP':
                    acc_day_UP = acc_day_UP + diff_hours
                elif previous_comfort == 'OK':
                    acc_day_OK = acc_day_OK + diff_hours
                else:
                    acc_day_DOWN = acc_day_DOWN + diff_hours
            days.append(date.day)
            up.append(float('%.2f'% acc_day_UP))
            down.append(float('%.2f'% acc_day_DOWN))
            ok.append(float('%.2f'% acc_day_OK))

    return days, up, down, ok


def comfort_day():
    
    try:
       conn01 = epmcomm.epmConnect(hostname='kotres', username='sa', password='admin')
       print "Conectado ao EPM Server!"
    except epmsdk.EpmException as ex:
        print 'Failed on connection to EPM with error\n{}\n'.format(ex)
        exit(1)


        #Leitura das annotations
    tagTeste = epmda.epmGetDataObjectAnnotation(conn01, 'wb_Tin')

    dataInicial = datetime.datetime(year=2016, month=3, day=1)
    dataFinal = datetime.datetime(year=2016, month=4, day=1)

    try:
        hG = epmhda.epmTagHistoryRead(tagTeste, dataInicial, dataFinal)
        print unicode(hG.size)
    except epmsdk.EpmException as ex:
        print 'Failed when getting Tag with error\n{}\n'.format(ex)
        raw_input("Error on historyread")
        exit(1)
    print 'Succeeded!' 
   
    ok = []
    down=[]
    up=[]


    acc_day_OK=0.0
    acc_day_UP=0.0
    acc_day_DOWN=0.0

    days = []

    day=1
    for i in range(1,hG.size):
   
    
        date = hG[i][0]-datetime.timedelta(hours=3)
        previous_date = hG[i-1][0]-datetime.timedelta(hours=3)

        comfort, setpoint, statusAir, T_OUT, WorkTime, NUser = hG[i][1].split(',')
        previous_comfort,previous_setpoint, previous_statusAir, previous_T_OUT, previous_WorkTime, previous_NUser = hG[i-1][1].split(',')

        WorkTime = str(WorkTime.split(':')[1])
        comfort= str(comfort.split(':')[1])

        previous_WorkTime = str(previous_WorkTime.split(':')[1])
        previous_comfort= str(previous_comfort.split(':')[1])

        if previous_date.day == date.day:
            diff_hours= float(((date - previous_date).seconds)/60)/60

            if previous_comfort == 'UP':
                acc_day_UP = acc_day_UP + diff_hours
            elif previous_comfort == 'OK':
                acc_day_OK = acc_day_OK + diff_hours
            else:
               acc_day_DOWN = acc_day_DOWN + diff_hours

        #mudou de dia
        else:

            #Calula ate as 23:59 do mesmo dia
            diff_hours= float(((datetime.datetime(year=previous_date.year, month= previous_date.month, day= previous_date.day,hour=23,minute=59) - previous_date).seconds)/60)/60
            
            if previous_comfort == 'UP':
                acc_day_UP = acc_day_UP + diff_hours
            elif previous_comfort == 'OK':
                acc_day_OK = acc_day_OK + diff_hours
            else:
               acc_day_DOWN = acc_day_DOWN + diff_hours

            up.append(float('%.2f'% acc_day_UP))
            down.append(float('%.2f'% acc_day_DOWN))
            ok.append(float('%.2f'% acc_day_OK))

           
            days.append(day)
            day=day+1
                    
            #calcula da meia noite até a anotaçao
            diff_hours = float(((date - datetime.datetime(year= date.year, month= date.month, day= date.day,hour=00,minute=00)).seconds)/60)/60

            if previous_comfort == 'UP':
                acc_day_UP = diff_hours
                acc_day_OK = 0.0
                acc_day_DOWN = 0.0
            elif previous_comfort == 'OK':
                acc_day_OK =  diff_hours
                acc_day_DOWN = 0.0
                acc_day_UP = 0.0
            else:
               acc_day_DOWN = diff_hours
               acc_day_OK=0.0
               acc_day_UP=0.0

            weekend = date.day - previous_date.day
            if(weekend>1):
                for j in range(previous_date.day+1,date.day):               
                    days.append(j)
                    day=day+1
                    if previous_comfort == 'UP':
                        acc_day_UP =24
                        acc_day_OK = 0.0
                        acc_day_DOWN = 0.0
                    elif previous_comfort == 'OK':
                        acc_day_OK = 24
                        acc_day_DOWN = 0.0
                        acc_day_UP = 0.0
                    else:
                        acc_day_DOWN = 24
                        acc_day_OK=0
                        acc_day_UP=0

                    up.append(float('%.2f'% acc_day_UP))
                    down.append(float('%.2f'% acc_day_DOWN))
                    ok.append(float('%.2f'% acc_day_OK))

        #adicina o ultimo porque a ultima anotação não muda o dia
        if i==hG.size-1:
            days.append(day)
            diff_hours= float(((date - previous_date).seconds)/60)/60

            if previous_comfort == 'UP':
                acc_day_UP = acc_day_UP + diff_hours
            elif previous_comfort == 'OK':
                acc_day_OK = acc_day_OK + diff_hours
            else:
               acc_day_DOWN = acc_day_DOWN + diff_hours

            up.append(float('%.2f'% acc_day_UP))
            down.append(float('%.2f'% acc_day_DOWN))
            ok.append(float('%.2f'% acc_day_OK))

    return days,ok,up,down   

def get_annotations():
    try:
        conn01 = epmcomm.epmConnect(hostname='kotres', username='sa', password='admin')
        print "Conectado ao EPM Server!"
    except epmsdk.EpmException as ex:
        print 'Failed on connection to EPM with error\n{}\n'.format(ex)
        exit(1)


        #Leitura das annotations
    tagTeste = epmda.epmGetDataObjectAnnotation(conn01, 'wb_Tin')

    dataInicial = datetime.datetime(year=2016, month=3, day=1)
    dataFinal = datetime.datetime(year=2016, month=4, day=1)

    try:
        hG = epmhda.epmTagHistoryRead(tagTeste, dataInicial, dataFinal)
        print unicode(hG.size)
    except epmsdk.EpmException as ex:
        print 'Failed when getting Tag with error\n{}\n'.format(ex)
        raw_input("Error on historyread")
        exit(1)
    print 'Succeeded!'

    #leitura dos dados da tag wb_in

    tagTeste = epmda.epmGetDataObject(conn01, target="wb_Tin")

    dataInicial = datetime.datetime(2016, 3, 1)
    dataFinal = datetime.datetime(2016, 4, 1)

    try:
        wb_Tin = epmhda.epmTagHistoryRead(tagTeste, dataInicial, dataFinal)
        print unicode(wb_Tin.size)
    except epmsdk.EpmException as ex:
        print 'Failed when getting Tag with error\n{}\n'.format(ex)
        raw_input("Error on historyread")
        exit(1)
    print 'Succeeded!'

    values = wb_Tin["Value"].tolist()
    tag_values = map(lambda x: float('%.2f'%x),  values)

	#numpydate to datetime
    DatesList = (wb_Tin["Timestamp"] - datetime.timedelta(hours=3)).tolist()
	#transforma todos os valores da lista para o formato Jan 16
    tag_dates = map(lambda x: x.strftime("%Y,%m,%d,%H,%M,%S,%f"), DatesList)
    

   
    annotations_dates = []
    annotations_Comfort = []
    annotations_SetPoint=[]
    annotations_T_OUT=[]
    annotations_WortTime=[]
    annotations_NUser=[]
    annotations_StatusAir=[]

    for obj in hG:
        annotations_dates.append((obj[0]-datetime.timedelta(hours=3)).strftime("%Y,%m,%d,%H,%M,%S,%f"))

        comfort, setpoint, statusAir, T_OUT, WorkTime, NUser =obj[1].split(',')
        
        annotations_Comfort.append(str(comfort.split(':')[1]))
        annotations_SetPoint.append(str(setpoint.split(':')[1]))
        annotations_StatusAir.append(str(statusAir.split(':')[1]))
        annotations_T_OUT.append(str(T_OUT.split(':')[1]))
        if WorkTime.split(':')[1] =='y':
            annotations_WortTime.append(str('Sim'))
        else:
            annotations_WortTime.append(str('Nao'))

        annotations_NUser.append(str(NUser.split(':')[1]).replace("}", ""))

    return annotations_dates,annotations_Comfort,annotations_SetPoint,annotations_StatusAir, annotations_T_OUT,annotations_WortTime,annotations_NUser,tag_values,tag_dates