#coding=utf-8
import numpy
import datetime
import epmsdk
import epmsdk.communication as epmcomm
import epmsdk.dataaccess as epmda
import epmsdk.historicaldata as epmhda

################################################################################
# FUNÇÕES AUXILIARES
def isWorkTime(datahora):
    datahora = datahora - datetime.timedelta(hours=3) # passa de UTC para Localtime
    if datahora.weekday() == 5 or datahora.weekday() == 6:
        # É final de semana
        return "n"
    else:
        # É dia de semana
        entManha = datetime.time(hour=8, minute=30, second=0)
        saidaManha = datetime.time(hour=11, minute=45, second=0)
        entTarde = datetime.time(hour=13, minute=15, second=0)
        saidaTarde = datetime.time(hour=18, minute=0, second=0)
        if (datahora.time() > entManha and datahora.time() < saidaManha) or (datahora.time() > entTarde and datahora.time() < saidaTarde):
            return "y" # É horario comercial
        else:
            return "n" # Não é horario comercial

def levelTin(valorTin):
    if valorTin < 23:
        return "DOWN"
    elif valorTin > 25:
        return "UP"
    else:
        return "OK"

def statusAC(tagAC, tagPessoas, i):
    if isWorkTime(tagAC["Timestamp"][i]) == "y": # É expediente?
        return "OK" # Se sim, está OK independente do resto (pessoas e estado On/Off).
    else:
        if tagPessoas["Value"][i] >= 1: # Senão, tem pessoas?
            return "OK" # Se sim, está OK independente do AC On/Off
        else:
            if tagAC["Value"][i] != 0: # Senão, está ligado?
                return "WARNING" # Se sim, então WARNING
            else:
                return "OK" # Senão, OK.

def filtroMM( tag, windowSize ):
    filtrado = tag.copy()
    filtrado["Value"][:windowSize] = tag["Value"][:windowSize].mean()
    for i in range(windowSize, len(tag)):
        filtrado["Value"][i] = tag["Value"][i-windowSize:i].mean()
    return filtrado

def insertAnnotation(tagName, annotationList):
    try:
        annTin = epmda.epmGetDataObjectAnnotation(epmConn, tagName)
        epmhda.epmAnnotationHistoryUpdate(annTin, annotationList)
    except epmsdk.EpmException as ex:
        print 'Failed when inserting annotation with error\n{}\n'.format(ex)
        exit(1)

################################################################################

# Faz a conexão com o EPM Server
server = "renan"
user = "sdk"
pw = "1234"
try:
    epmConn = epmcomm.epmConnect(hostname=server, username=user, password=pw)
except epmsdk.EpmException as ex:
    print 'Failed on connection to EPM with error\n{}\n'.format(ex)
    exit(1)

# Pega os tags do EPM
try:
    bvTin = epmda.epmGetDataObject(epmConn, target="wb_Tin")
    bvTset = epmda.epmGetDataObject(epmConn, target="wb_Tset")
    bvTout = epmda.epmGetDataObject(epmConn, target="wb_Tout")
    bvAC_OnOff = epmda.epmGetDataObject(epmConn, target="wb_air")
    bvPCounter = epmda.epmGetDataObject(epmConn, target="wb_pCounter")
except epmsdk.EpmException as ex:
    print 'Failed when getting Tag with error\n{}\n'.format(ex)
    exit(2)

# Consulta o periodo historico de cada tag
dataInicial = datetime.datetime(year=2016, month=3, day=1)
dataFinal = datetime.datetime(year=2016, month=4, day=1)
try:
    Tin = epmhda.epmTagHistoryRead(bvTin, dataInicial, dataFinal)
    Tout = epmhda.epmTagHistoryRead(bvTout, dataInicial, dataFinal)
    Tset = epmhda.epmTagHistoryRead(bvTset, dataInicial, dataFinal)
    AC_OnOff = epmhda.epmTagHistoryRead(bvAC_OnOff, dataInicial, dataFinal)
    pCounter = epmhda.epmTagHistoryRead(bvPCounter, dataInicial, dataFinal)
except epmsdk.EpmException as ex:
    print 'Failed when reading Tag history with error\n{}\n'.format(ex)
    exit(3)

################################################################################

count = 1
arrAnnotations = numpy.empty(count, dtype=numpy.dtype([('AnnotationTime', 'object'), ('Message', 'object'), ('UserName', 'object')]))
currLevelTin = levelTin(Tin["Value"][0])        # Define status atual da Tin
currStatusAC = statusAC(AC_OnOff, pCounter, 0)  # Define status atual do AC_OnOff

# APLICA UM FILTRO DE MEDIA MOVEL NA TEMPERATURA INTERNA
Tin = filtroMM(Tin, 7)

# Habilita ou desabilita as analises.
rodarAnaliseCT = True # Analise de Conforto Térmico
rodarAnaliseAC = False  # Analise de funcionamento do AC

# ANÁLISES E ANOTAÇÕES
for i in range(len(Tin)):
    # Identificando conforto térmico
    if rodarAnaliseCT and ( currLevelTin != levelTin(Tin["Value"][i]) ):
        # Ocorreu mudança de estado/nivel
        currLevelTin = levelTin(Tin["Value"][i]) # Atualiza estado
        if currLevelTin == "DOWN":
            strAnnotation = "Comfort:DOWN,Setpoint:{},StatusAir:{},T_OUT:{},WorkTime:{},NUser:{}".format(Tset["Value"][i], "OFF" if AC_OnOff["Value"][i] == 0 else "ON", Tout["Value"][i], isWorkTime(Tin["Timestamp"][i]), pCounter["Value"][i])
        elif currLevelTin == "UP":
            strAnnotation = "Comfort:UP,Setpoint:{},StatusAir:{},T_OUT:{},WorkTime:{},NUser:{}".format(Tset["Value"][i], "OFF" if AC_OnOff["Value"][i] == 0 else "ON", Tout["Value"][i], isWorkTime(Tin["Timestamp"][i]), pCounter["Value"][i])
        else:
            strAnnotation = "Comfort:OK,Setpoint:{},StatusAir:{},T_OUT:{},WorkTime:{},NUser:{}".format(Tset["Value"][i], "OFF" if AC_OnOff["Value"][i] == 0 else "ON", Tout["Value"][i], isWorkTime(Tin["Timestamp"][i]), pCounter["Value"][i])

        strAnnotation = "{" + strAnnotation + "}"
        arrAnnotations[0]['AnnotationTime'] = Tin["Timestamp"][i]
        arrAnnotations[0]['Message'] = unicode(strAnnotation)
        arrAnnotations[0]['UserName'] = unicode(user)
        insertAnnotation("wb_Tin", arrAnnotations)

    # Identificando AC ligado fora do expediente (e sem pessoas na sala)
    if rodarAnaliseAC and ( currStatusAC != statusAC(AC_OnOff, pCounter, i) ):
        # Houve variação no estado (WARNING <-> OK)
        if currStatusAC == "OK":
            strAnnotation = "WARNING" # Foi para WARNING
        else:
            strAnnotation = "OK" # Foi para OK

        currStatusAC = statusAC(AC_OnOff, pCounter, i)
        arrAnnotations[0]['AnnotationTime'] = AC_OnOff["Timestamp"][i]
        arrAnnotations[0]['Message'] = unicode(strAnnotation)
        arrAnnotations[0]['UserName'] = unicode(user)
        insertAnnotation("wb_air", arrAnnotations)


print "Pre-analise concluida!"
