# -*- coding: utf-8 -*-
# EPM Plugin modules
import Plugins as ep

import numpy as np
import scipy.optimize as optimize
from scipy import interpolate
from scipy import integrate
import datetime as dt
import matplotlib.pyplot as plt
from Tkinter import *
import tkFileDialog
import ctypes
from ctypes.wintypes import MAX_PATH
import csv
import string

from mpl_toolkits.mplot3d import axes3d, Axes3D
from matplotlib.collections import PolyCollection
from matplotlib.colors import colorConverter



#\TODO: Implementar validacoes! Codigo nao esta a prova de usuario!

dll = ctypes.windll.shell32
myDocsDir = ctypes.create_unicode_buffer(MAX_PATH + 1)
dll.SHGetSpecialFolderPathW(None, myDocsDir, 0x0005, False)

# Variaveos globais
nominalPower = 3000.0 # Potencia nominal [KW]
minSpeed = 4.0 # velocidade minima para operar aerogerador [m/s]
supplierCurveFile = myDocsDir.value + '\\Refdata3000.csv'

# Grafico velocidade do vento vs potencia
@ep.DatasetFunctionPlugin('Wind Speed X Power Chart', 2)
def windSpeedPowerChart():
    """Grafico de potencia com a velocidade do vento
    Apresenta um grafico de dispersao da potencia com a velocidade do vento e calcula a curva que melhor o representa
    """
    if len(ep.EpmDatasetPens.SelectedPens) != 2:
        ep.showMsgBox('EPM Python Plugin - Demo Tools', 'Please select two interpolated pens before applying this function!', 'Warning')
        return 0
    global minSpeed
    global nominalPower    
    runDialogMinSpeedNomPower()
    minSpeed = float(minSpeed)
    nominalPower = float(nominalPower)
    rawSpeed, rawPower = getSpeedPowerValues(ep.EpmDatasetPens.SelectedPens[0], ep.EpmDatasetPens.SelectedPens[1])
    speed, power = cleanSpeedPowerData(rawSpeed, rawPower, minSpeed, nominalPower )
    xm, ym = windPowerAverage(speed, power)
    par0 = [1.0, 1.0, 1500.0, 1.0]
    binSpeed = 0.5
    parest,cov,infodict,mesg,ier = optimize.leastsq(residualsSPPn4, par0, args=(xm, ym), full_output=True)
    xEst = np.arange(xm.min(), xm.max(), binSpeed)
    yEst = powerFitPn4(parest, xEst)
    posAbove = np.argwhere(yEst > nominalPower)
    yEst[posAbove] = nominalPower
    fig1 = plt.figure()
    ax1 = fig1.add_subplot(1, 1, 1)
    ax1.set_ylim(0, 1.05*nominalPower)
    ax1.set_xlim(minSpeed-1, 1.1*speed.max())
    ax1.set_xlabel(r'$Speed (m/s)$')
    ax1.set_ylabel(r'$Power (KW)$')    
    ax1.scatter(speed, power)
    ax1.plot(xEst, yEst, color='r', linewidth=3)
    plt.show()

# Grafico velocidade do vento vs potencia comparada com a curva do fornecedor
@ep.DatasetFunctionPlugin('Supplier CMP Wind Speed X Power Chart', 4)
def suplierSpeedPowerChart():
    """Grafico de potencia com a velocidade do vento comparada com a cruva do fornecedor em um arquivo CSV
    Apresenta um grafico de dispersao da potencia com a velocidade do vento, calculan a curva que melhor o representa e compara com a curva
    de referencia fornecida pelo fornecedor
    """
    if len(ep.EpmDatasetPens.SelectedPens) != 2:
        ep.showMsgBox('EPM Python Plugin - Demo Tools', 'Please select two interpolated pens before applying this function!', 'Warning')
        return 0
    global minSpeed
    global nominalPower
    global supplierCurveFile
    runDialogMinSpeedNomPowerSupplier()
    minSpeed = float(minSpeed)
    nominalPower = float(nominalPower)
    rawSpeed, rawPower = getSpeedPowerValues(ep.EpmDatasetPens.SelectedPens[0], ep.EpmDatasetPens.SelectedPens[1])
    speed, power = cleanSpeedPowerData(rawSpeed, rawPower, minSpeed, nominalPower )
    xm, ym = windPowerAverage(speed, power)
    par0 = [1.0, 1.0, 1500.0, 1.0]
    binSpeed = 0.5
    parest,cov,infodict,mesg,ier = optimize.leastsq(residualsSPPn4, par0, args=(xm, ym), full_output=True)
    xEst = np.arange(xm.min(), xm.max(), binSpeed)
    yEst = powerFitPn4(parest, xEst)
    posAbove = np.argwhere(yEst > nominalPower)
    yEst[posAbove] = nominalPower
    speedRef, powerRef = readFromCsv(fileName=supplierCurveFile, delimiter=';')
    tckRef = interpolate.splrep(speedRef, powerRef, s=0)
    binSpeed = 0.5
    xRef = np.arange(speedRef.min(), speedRef.max(), binSpeed)
    yRef = interpolate.splev(xRef, tckRef, der=0)
    energyLost = integrate.simps(yRef, dx=binSpeed) - integrate.simps(yEst, dx=binSpeed)
    fig1 = plt.figure()
    ax1 = fig1.add_subplot(1, 1, 1)
    ax1.set_ylim(0, 1.05*nominalPower)
    ax1.set_xlim(minSpeed-1, 1.1*speed.max())
    ax1.set_xlabel(r'$Speed (m/s)$')
    ax1.set_ylabel(r'$Power (KW)$')    
    ax1.scatter(speed, power)
    ax1.plot(xEst, yEst, color='r', linewidth=3)
    ax1.plot(xRef, yRef, color='g', linewidth=3)
    ax1.text(15, 1100, 'Lost: ' + str(round(energyLost/1000,2)) + '(MW)', fontsize=14)
    plt.show()

# Pie chart com o percentual de tempo em cada direcao
@ep.DatasetFunctionPlugin('Percent time wind direction', 6)
def windDirectionPieChart():
    """Grafico de pizza da direcao do vento
    Apresenta um grafico de pizza baseado no percentual de tempo da direcao do vento
    """
    if len(ep.EpmDatasetPens.SelectedPens) != 1:
        ep.showMsgBox('EPM Python Plugin - Demo Tools', 'Please select one pen before applying this function!', 'Warning')
        return 0
    rawDirection = ep.EpmDatasetPens.SelectedPens[0]
    nodesPercents, nodesLabels = percentTimeIn(rawDirection.Values)
    colors = ['blue','yellowgreen', 'cyan', 'gold', 'lightskyblue', 'magenta', 'green', 'lightcoral']
    plt.pie(nodesPercents[:,1], labels=nodesLabels, colors=colors,autopct='%1.1f%%', shadow=False, startangle=90)
    plt.axis('equal')
    plt.show()
    
# Grafico polar de dispersao da direcao do vento
@ep.DatasetFunctionPlugin('Polar scatter wind direction', 8)
def PolarScatterWindDirection():
    """Grafico polar de dispersao da direcaodo vento
    Apresenta um grafico polar de dispersao com a direcao do vento
    """
    if len(ep.EpmDatasetPens.SelectedPens) != 2:
        ep.showMsgBox('EPM Python Plugin - Demo Tools', 'Please select 2 interpolated pens before applying this function!', 'Warning')
        return 0
    speed, direction = getSpeedDirectionValues(ep.EpmDatasetPens.SelectedPens[0], ep.EpmDatasetPens.SelectedPens[1])
    ax1 = plt.subplot(111, polar=True)
    ax1.set_theta_zero_location('N')
    ax1.set_theta_direction(-1)
    ax1.grid(True)
    ax1.xaxis.set_ticklabels(['N',r"$45^{o}$",'E',r"$135^{o}$",'S',r"$225^{o}$",'W', r"$315^{o}$"])
    ax1.set_title("Wind direction", va='bottom')
    ax1.plot(direction, speed, 'bo')
    plt.show()

# Grafico polar de dispersao-area da direcao do vento, velocidade e potencia
@ep.DatasetFunctionPlugin('Polar area wind', 10)
def PolarScatterAreaWind():
    """Grafico polar de dispersao-area da direcao, velocidade e potencia do vento
    Apresenta um grafico polar de dispersao com a direcao, a velocidade e potencia do vento
    """
    if len(ep.EpmDatasetPens.SelectedPens) != 3:
        ep.showMsgBox('EPM Python Plugin - Demo Tools', 'Please select 3 interpolated pens before applying this function!', 'Warning')
        return 0
    speed, direction, power = getSpeedPowerDirectionValues(ep.EpmDatasetPens.SelectedPens[0], ep.EpmDatasetPens.SelectedPens[1],
                                                           ep.EpmDatasetPens.SelectedPens[2])
    colors = power/1000.
    area = np.pi * speed**2
    ax1 = plt.subplot(111, polar=True)
    ax1.set_theta_zero_location('N')
    ax1.set_theta_direction(-1)
    ax1.xaxis.set_ticklabels(['N',r"$45^{o}$",'E',r"$135^{o}$",'S',r"$225^{o}$",'W', r"$315^{o}$"])
    c = plt.scatter(direction, speed, c=colors, s=area, cmap=plt.cm.hsv)
    c.set_alpha(0.75)
    plt.show()

# Grafico polar de barra da direcao do vento, velocidade e potencia
@ep.DatasetFunctionPlugin('Polar bar wind', 12)
def PolarBarWind():
    """Grafico de polar de barras da direcao, velocidade e potencia do vento
    Apresenta um grafico polar de dispersao com a direcao, a velocidade e potencia do vento
    """
    if len(ep.EpmDatasetPens.SelectedPens) != 3:
        ep.showMsgBox('EPM Python Plugin - Demo Tools', 'Please select 3 interpolated pens before applying this function!', 'Warning')
        return 0
    speed, direction, power = getSpeedPowerDirectionValues(ep.EpmDatasetPens.SelectedPens[0], ep.EpmDatasetPens.SelectedPens[1],
                                                           ep.EpmDatasetPens.SelectedPens[2])
    spd4, dir4, pow4 = groupByDirection(speed, direction, power)
    width = pow4/1000.
    ax1 = plt.subplot(111, polar=True)
    ax1.set_theta_zero_location('N')
    ax1.set_theta_direction(-1)
    ax1.xaxis.set_ticklabels(['N',r"$45^{o}$",'E',r"$135^{o}$",'S',r"$225^{o}$",'W', r"$315^{o}$"])
    bars = ax1.bar(dir4, spd4, width=width, bottom=0.0)
    for r, bar in zip(spd4, bars):
        bar.set_facecolor(plt.cm.jet(r / 10.))
        bar.set_alpha(0.5)
    plt.show()

@ep.DatasetFunctionPlugin('Scatter 3D Power Curve', 13)
def PowerCurve3d():
    """Grafico de dispersão em 3D"""    
    if len(ep.EpmDatasetPens.SelectedPens) != 3:
        ep.showMsgBox('EPM Python Plugin - Demo Tools', 'Please select 3 interpolated pens before applying this function!', 'Warning')
        return 0
    speed, direction, power = getSpeedPowerDirectionValues(ep.EpmDatasetPens.SelectedPens[0], ep.EpmDatasetPens.SelectedPens[1],
                                                           ep.EpmDatasetPens.SelectedPens[2])
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')

    c = np.abs(speed)
    cmwinter = plt.get_cmap("winter")

    ax.scatter(speed, direction, power, c=c, cmap=cmwinter)
    ax.set_xlabel('Power (KW)')
    ax.set_ylabel('Direction')
    ax.set_zlabel('Speed (m/s)')

    plt.show()

@ep.DatasetFunctionPlugin('Expected Production', 14)
def ExpectedProduction():
    if len(ep.EpmDatasetPens.SelectedPens) != 2:
       ep.showMsgBox('EPM Python Plugin - Demo Tools', 'Please select Power and Speed pens before applying this function!', 'Warning')
       return 0

    global minSpeed
    global nominalPower
    global supplierCurveFile
    runDialogMinSpeedNomPowerSupplier()
    minSpeed = float(minSpeed)
    nominalPower = float(nominalPower)
    
    rawSpeed, rawPower = getSpeedPowerValues(ep.EpmDatasetPens.SelectedPens[0], ep.EpmDatasetPens.SelectedPens[1])
    speed, power = cleanSpeedPowerData(rawSpeed, rawPower, minSpeed, nominalPower )

    speedRef, powerRef = readFromCsv(fileName=supplierCurveFile, delimiter=';')

    #idx = []
    #for item in speed:
    #	idx.append(find_nearest(speedRef, item)

    idx = [find_nearest(speedRef, item) for item in speed]

    expected = [powerRef[index] for index in idx]

    #TODO: Calculo de perdas
    #lost = sum(expected - power)
    #print lost
    
    fig, ax = plt.subplots()

    line1 = ax.plot(power, label='Realized')
    line2 = ax.plot(expected, label='Expected')

    plt.ylabel('Power (Kw)')
    plt.xlabel('Time Unit')
    
    ax.legend(loc='lower right')
    plt.show()




##################################################################################################
##################################################################################################
#                                 *** Funcoes uteis ***
##################################################################################################
##################################################################################################

#Recebe um valor e um array e retorna a posição onde se encontra o valor mais próximo no array 
def find_nearest(array, value):
	idx = (np.abs(array-value)).argmin()
	return idx



# Recebe duas penas (velocidade [m/s] e potencia[KW]) e retorna dois vetores com os valores corretos
def getSpeedPowerValues(pen1, pen2):
    epmData1 = pen1.Values
    epmData2 = pen2.Values
    if epmData1['Value'].max() > epmData2['Value'].max():
        power = epmData1['Value'].copy()
        speed = epmData2['Value'].copy()
    else:
        power = epmData2['Value'].copy()
        speed = epmData1['Value'].copy()
    return speed, power

# Recebe duas penas (velocidade [m/s] e direcao [graus]) e retorna dois vetores com os valores corretos
def getSpeedDirectionValues(pen1, pen2):
    epmData1 = pen1.Values
    epmData2 = pen2.Values
    if epmData1['Value'].max() > epmData2['Value'].max():
        direction = epmData1['Value'].copy()
        speed = epmData2['Value'].copy()
    else:
        direction = epmData2['Value'].copy()
        speed = epmData1['Value'].copy()
    return speed, direction

# Recebe 3 penas (velocidade [m/s], direcao [graus] e potencia[KW]) e retorna 3 vetores com os valores corretos
def getSpeedPowerDirectionValues(pen1, pen2, pen3):
    epmData1 = pen1.Values
    epmData2 = pen2.Values
    epmData3 = pen3.Values
    if (epmData1['Value'].max() > epmData2['Value'].max()) and (epmData1['Value'].max() > epmData3['Value'].max()):
        power = epmData1['Value'].copy()
        speed, direction = getSpeedDirectionValues(pen2, pen3)
    elif (epmData2['Value'].max() > epmData1['Value'].max()) and (epmData2['Value'].max() > epmData3['Value'].max()):
        power = epmData2['Value'].copy()
        speed, direction = getSpeedDirectionValues(pen1, pen3)
    else:
        power = epmData3['Value'].copy()
        speed, direction = getSpeedDirectionValues(pen1, pen2)        
    return speed, direction, power

# Funcao que remove os dados que nao fazem sentido e/ou expurios
def cleanSpeedPowerData(speedData, powerData, minSpeed, nominalPower):
    pPos = np.argwhere(powerData < 0.)
    speed = np.delete(speedData, pPos)
    power = np.delete(powerData, pPos)
    pPos = np.argwhere(powerData > nominalPower)
    speed = np.delete(speed, pPos)
    power = np.delete(power, pPos)
    pPos = np.argwhere(speed < minSpeed)
    speed = np.delete(speed, pPos)
    power = np.delete(power, pPos)
    return speed, power

# Determinacao dos valores medios de potencia para cada valor de velocidade
def windPowerAverage(speed, power):
    pos = np.argsort(speed)
    x = speed[pos].copy()
    y = power[pos].copy()
    xm = []
    ym = []
    i = 0
    while i < (len(x)):
        p = np.where(x == x[i])
        xm.append(x[p].mean())
        ym.append(y[p].mean())
        i = p[0][-1] + 1
    return np.array(xm), np.array(ym)

# Curva de potencia com o vento - estimando a P nominal
def powerFitPn4(par, x):
    return par[2] / (par[3] + np.exp(-(par[0] * x + par[1])))

# Residuos para estimar parametros da curva de Pot com o Vento estimando tbm Pnominal
def residualsSPPn4(par, x, y):
    return powerFitPn4(par, x) - y

# Importar de um arquivo CSV (duas colunas de dados) \TODO: generalizar para N colunas
def readFromCsv( fileName, delimiter=';' ):
    f = csv.reader(open(fileName), delimiter=delimiter)
    cd1,cd2 = [], []
    for (c1, c2) in f:
        c1 = c1.replace(',', '.')
        c2 = c2.replace(',', '.')
        cd1.append(float(c1))
        cd2.append(float(c2))
    return np.array(cd1), np.array(cd2)


# Retorna o percentual de tempo que a variavel ficou em cada periodo
def percentTimeIn(epmData):
    t,y = rmNanAndOutliers2(epmData)
    minVal = 0
    maxVal = 360
    step = int((maxVal-minVal)/8)
    nodes = range(minVal,maxVal,step)
    intervNum = np.size(nodes)+1
    totTime = np.empty(intervNum, dtype=object)
    totTime.fill(dt.timedelta(0,0))
    for i in range(1,np.size(y)):
        deltaT = t[i] - t[i-1]
        ix = np.digitize([y[i]], nodes)
        totTime[ix] += deltaT
    nodesPercents = np.zeros([np.size(totTime),2])
    totalPeriod = totTime.sum().total_seconds()
    for i in range(np.size(totTime)):
        if i:
           nodesPercents[i,0] = nodes[i-1]
        else:
           nodesPercents[i,0] = -np.inf
        nodesPercents[i,1] = totTime[i].total_seconds()/totalPeriod
    nodesLabels = []
    for item in nodesPercents[:,0]:
        nodesLabels.append(angle2cardinal(item))
    return nodesPercents, nodesLabels

def angle2cardinal(degAngle):
    cardList = ['N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW']
    degBaseList = range(0, 360, 360/8)
    degBand = 360/16.
    dir = 0
    if degAngle> degBaseList[1]-degBand and degAngle<= degBaseList[2]-degBand:
        dir = 1
    elif degAngle> degBaseList[2]-degBand and degAngle<= degBaseList[3]-degBand:
        dir = 2
    elif degAngle> degBaseList[3]-degBand and degAngle<= degBaseList[4]-degBand:
        dir = 3
    elif degAngle> degBaseList[4]-degBand and degAngle<= degBaseList[5]-degBand:
        dir = 4
    elif degAngle> degBaseList[5]-degBand and degAngle<= degBaseList[6]-degBand:
        dir = 5
    elif degAngle> degBaseList[6]-degBand and degAngle<= degBaseList[7]-degBand:
        dir = 6
    elif degAngle> degBaseList[7]-degBand and degAngle<= 360-degBand:
        dir = 7
    return cardList[dir]


# Converte todos os valores de graus nas 4 direcoes principais (em graus)
def allDeg24Directions(degVector):
    fourDirVector = degVector.copy()
    # Norte:  315 <= DEG < 45
    pos = np.argwhere(degVector >= 315)
    fourDirVector[pos] = 0.0 # Norte
    pos = np.argwhere(degVector<45)
    fourDirVector[pos] = 0.0 # Norte
    # Leste:  45 <= DEG < 135
    pos = np.argwhere(np.logical_and(degVector>=45, degVector<135))
    fourDirVector[pos] = 90.0 # Leste
    # Sul:  135 <= DEG < 225
    pos = np.argwhere(np.logical_and(degVector>=135, degVector<225))
    fourDirVector[pos] = 180.0 # Sul
    # Oeste:  225 <= DEG < 315
    pos = np.argwhere(np.logical_and(degVector>=225, degVector<315))
    fourDirVector[pos] = 270.0 # Oeste
    return fourDirVector

# Plota o perfil diario da direcao do vento (4 direcoes principais) - dados devem estar interpolados a cada 10 minutos e fechando dias completos de 24h
def plot4MainDir(degVector):
    fourDirVector = allDeg24Directions(degVector['Value'])
    pHours = 24 # periodo considerado
    sampling = 60 # 10min de amostragem
    base = pHours*60/sampling
    totDays = len(fourDirVector)/base  # Dias multiplo de 5, para graficos poly 3d
    days  = np.arange(totDays)+1
    hours = np.arange(0,pHours*60,sampling)
    meshTime, indices = np.meshgrid(hours, days)
    meshProfile = np.zeros(meshTime.shape)
    profileList = []
    ii = 1
    for i in range(totDays):
        dataPeriod = fourDirVector[i*base:ii*base]
        profileList.append( dataPeriod )
        ii +=1
    profileMatrix = np.array(profileList)
    for i in range( indices.shape[0] ):
        for j in range( indices.shape[1] ):
            meshProfile[(i,j)] = profileMatrix[(i,j)]
    
    fig = plt.figure()
    ax = fig.gca(projection='3d')
    X = meshTime
    Y = indices
    Z = meshProfile
    ax.plot_surface(X, Y, Z, rstride=1, cstride=1, cmap='coolwarm', alpha=0.8) # ou a linha abaixo
    ax.set_xlabel('minutos')
    ax.set_ylabel('dia')
    ax.set_zlabel(r'$^oC$')
    
    # Visao apenas dos perfis
    fig2 = plt.figure()
    ax2 = fig2.gca(projection='3d')
    cc = lambda arg: colorConverter.to_rgba(arg, alpha=0.6)
    verts = []
    cs = [cc('r'), cc('g'), cc('b'), cc('y'), cc('c')]*(totDays/5)
    k = 0
    for d in days:
        verts.append(list(zip(hours, meshProfile[k])))
        k += 1
    poly = PolyCollection(verts, facecolors = cs)
    poly.set_alpha(0.7)
    ax2.add_collection3d(poly, zs=days, zdir='y')

    """ OK! Mostra grafico de barras
    cs = ['r', 'g', 'b', 'y','c']*(totDays/5)
    k = 0
    for c, d in zip(cs, days):
        cc = [c]*len(hours)
        ax2.bar(hours, meshProfile[k], zs=d, zdir='y', color=cc, alpha=0.5)
        k += 1
    """
    ax2.set_xlabel('minutos')
    ax2.set_xlim3d(0, hours[-1])
    ax2.set_ylabel('dia')
    ax2.set_ylim3d(0, days[-1])
    ax2.set_zlabel('Dir')
    ax2.set_zlim3d(0, 360)

    plt.show()
    
    
    #ii = 1
    #for i in range(totDays):
    #    plt.plot(fourDirVector[i*base:ii*base-1])
    #    ii +=1
    #plt.show()

def groupByDirection(speed, power, direction):
    posN =[]
    posE =[]
    posS =[]
    posW =[]
    bins  = np.array([0, 45, 135, 225, 315, 360])
    pos = np.digitize(direction, bins)
    for n in range(direction.size):
        if pos[n] == 1:
            posN.append(n)
        elif pos[n] == 2:
            posE.append(n)
        elif pos[n] == 3:
            posS.append(n)
        elif pos[n] == 4:
            posW.append(n)
        else:
            posN.append(n)
    speed4dir = np.array([speed[posN].mean(), speed[posE].mean(), speed[posS].mean(), speed[posW].mean()])
    power4dir = np.array([power[posN].mean(), power[posE].mean(), power[posS].mean(), power[posW].mean()])
    dir = np.array([0, 90, 180, 270])
    return speed4dir, dir, power4dir


# Remove dados Nan e Outliers baseado no desvio padrao e retorna vetores t e y
def rmNanAndOutliers2(epmData, sd = 6):
    y = epmData['Value']
    t = epmData['Timestamp']
    nanPos = np.argwhere(np.isnan(y))
    y = np.delete(y,nanPos)
    t = np.delete(t,nanPos)
    s3 = np.floor(sd * np.sqrt(y.std()))
    smin = y.mean() - s3
    smax = y.mean() + s3
    outPos = np.argwhere(y<smin)
    y = np.delete(y,outPos)
    t = np.delete(t,outPos)
    outPos = np.argwhere(y>smax)
    y = np.delete(y,outPos)
    t = np.delete(t,outPos)
    return t,y



##################################################################################################
##################################################################################################
#                                 *** Dialogs ***
##################################################################################################
##################################################################################################


# Diolog para solictar Velocidade minima do vento e Potencia nominal do Aerogerador
class DialogMinSpeedNomPower():

    def __init__(self,raiz):
        self.raiz = raiz
        self.makeScreen()
        self.raiz.title('Elipse Plant Manager - Wind Speed vs Power')

    def makeScreen(self):
        margin = LabelFrame(self.raiz, bd=0, padx=5,pady=5)
        margin.grid()
        fora = LabelFrame(margin, bd=2, padx=5,pady=5)
        fora.grid()
        self.minWinSpeed = StringVar()
        self.nominalPower = StringVar()
        cabecalho = LabelFrame(fora, text="User information", bd=2)
        cabecalho.grid(sticky=E+W)
        Label(cabecalho,text='Minimum Wind Speed [m/s]:').grid(sticky=E)
        Label(cabecalho,text='Nominal Power [KW]:').grid(sticky=E)
        
        self.minSpeedEdit = Entry(cabecalho, width=50, textvariable=self.minWinSpeed).grid(row=0, column=1, sticky=W)
        self.minWinSpeed.set(str(minSpeed))

        self.nomPowerEdit = Entry(cabecalho, width=50, textvariable=self.nominalPower).grid(row=1, column=1, sticky=W)
        self.nominalPower.set(nominalPower)
                
        frame_botoes = LabelFrame(fora, bd=0)
        frame_botoes.grid(sticky=E)
        Button(frame_botoes, text='OK',width=10,command=self.Action_OK).grid(row=21,column=0,sticky=W,padx=10, pady=8)
        Button(frame_botoes, text='Cancelar',width=10,command=self.Action_Cancel).grid(row=21,column=1,sticky=E,padx=10, pady=8)

    def Action_OK(self):
        global minSpeed
        global nominalPower
        minSpeed = self.minWinSpeed.get()
        nominalPower = self.nominalPower.get()
        print 'Variáveis atualizadas!'
        self.raiz.destroy()

    def Action_Cancel(self):
        self.raiz.destroy()

# Diolog para solictar a curva de referencia, a Velocidade minima do vento e Potencia nominal do Aerogerador
class DialogSupplierMinSpeedNomPower():

    def __init__(self,raiz):
        self.raiz = raiz
        self.makeScreen()
        self.raiz.title('Elipse Plant Manager - Supplier CPM Wind Speed vs Power')

    def makeScreen(self):
        margin = LabelFrame(self.raiz, bd=0, padx=5,pady=5)
        margin.grid()
        fora = LabelFrame(margin, bd=2, padx=5,pady=5)
        fora.grid()
        self.minWinSpeed = StringVar()
        self.nominalPower = StringVar()
        self.supplierCurve = StringVar()
        cabecalho = LabelFrame(fora, text="User information", bd=2)
        cabecalho.grid(sticky=E+W)
        Label(cabecalho,text='Minimum Wind Speed [m/s]:').grid(sticky=E)
        Label(cabecalho,text='Nominal Power [KW]:').grid(sticky=E)
        Label(cabecalho, text='Suplier SxP curve:').grid(sticky=E)
        
        self.minSpeedEdit = Entry(cabecalho, width=50, textvariable=self.minWinSpeed).grid(row=0, column=1, sticky=W)
        self.minWinSpeed.set(str(minSpeed))

        self.nomPowerEdit = Entry(cabecalho, width=50, textvariable=self.nominalPower).grid(row=1, column=1, sticky=W)
        self.nominalPower.set(nominalPower)

        self.supplierCurveEdit = Entry(cabecalho, width=50, textvariable=self.supplierCurve).grid(row=2, column=1, sticky=W)
        self.supplierCurve.set(supplierCurveFile)
        Button(cabecalho, text='...',command=self.setCurveFile,width=5).grid(row=2,column=2,sticky=W,padx=5)
                
        frame_botoes = LabelFrame(fora, bd=0)
        frame_botoes.grid(sticky=E)
        Button(frame_botoes, text='OK',width=10,command=self.Action_OK).grid(row=21,column=0,sticky=W,padx=10, pady=8)
        Button(frame_botoes, text='Cancelar',width=10,command=self.Action_Cancel).grid(row=21,column=1,sticky=E,padx=10, pady=8)

    def setCurveFile(self):
        global myDocsDir
        suppFile = tkFileDialog.askopenfilename(defaultextension='.csv',initialdir=myDocsDir.value,
                                               filetypes=[('CSV file','*.csv'), ('All files','*.*')], title='Select supplier curve csv file' )
        self.supplierCurve.set(suppFile)

    def Action_OK(self):
        global minSpeed
        global nominalPower
        global supplierCurveFile
        minSpeed = self.minWinSpeed.get()
        nominalPower = self.nominalPower.get()
        supplierCurveFile = self.supplierCurve.get()
        print 'Variaveis atualizadas!'
        self.raiz.destroy()

    def Action_Cancel(self):
        self.raiz.destroy()


# Funcao para rodar a Dialog que solicita a velocidade minima do vento e a potencia nominal do exemplo
def runDialogMinSpeedNomPower():
    raiz = Tk()
    interface = DialogMinSpeedNomPower(raiz)
    raiz.mainloop()

# Funcao para rodar a Dialog que solicita a cruve de referencia, a velocidade minima do vento e a potencia nominal do exemplo
def runDialogMinSpeedNomPowerSupplier():
    raiz = Tk()
    interface = DialogSupplierMinSpeedNomPower(raiz)
    raiz.mainloop()
