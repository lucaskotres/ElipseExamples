import epmprocessor as epr
import epmprocessor.epm as epm
import numpy as np
import base64
import smtplib

@epr.applicationMethod('SimpleAverage')
def simpleaverage(session, bv1):

    processInterval = session.range
    endTime = session.timeEvent
    iniTime = endTime - processInterval
    queryPeriod = epm.QueryPeriod(iniTime, endTime)
    data = bv1.historyReadRaw(queryPeriod)

    avg = data['Value'].mean()

    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login("lucaskotres@gmail.com", "psw????")

    msg = f'Hello! The EPM Processor send a message to you:  the average is {avg}. Hugs!'

    msg = "YOUR MESSAGE!"
    server.sendmail("lucaskotres@gmail.com", "kotres@elipse.com.br", msg)
    server.quit()

    return epr.ScopeResult(True)



