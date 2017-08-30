# -*- coding: utf-8 -*-

import numpy as np
from scipy.signal import lfilter
from scipy.signal import butter


# Filtro de media movel de ordem "o"
def filtMean( xo, o ):
    x = xo.copy()
    X = x.copy()
    for i in range( 1, o ):
        tmp = np.hstack( (x[i:], np.zeros(i)) )
        X += tmp
    X /= o
    # Repete a ultima media para os valores finais
    lastM = X[-o]
    for i in range( 1, o ):
        X[-i] = lastM
    return X

# Filtro de media movel de ordem "o" - informa objeto de dados do EPM
def filtMeanEpm( xepmo, o ):
	xepm = xepmo.copy() # copia os dados para nao alterar a vairavel do console
	xf = filtMean( xepm['Value'], o )
	xepm['Value'] = xf.copy()
	return xepm

# Filtro de ruido de um sinal utiliza Butterworth ordem 2 - informa objeto de dados do EPM
def filtSignal( xepmo, w = 0.3, o = 2 ):
    b, a = butter( o, w )
    yfVec = FiltFilt( b, a, xepmo['Value'] )
    yf = xepmo.copy()
    yf['Value'] = yfVec
    return yf

# Filtro de primeira ordem
def filter1st( xepm, st, fp ):
	xepmF = xepm.copy()
	x = xepmF['Value'].copy()
	xf = x.copy()
	tmp = np.exp(-st/fp)
	for i in range(len(x)-1):
		xf[i+1] = ( 1 - tmp ) * x[i+1] + tmp * x[i]
	xepmF['Value'] = xf.copy()
	return xepmF


##########################################################################################################
# *** Extras ***
def LFilter_zi( b, a ):
    n = max(len(a),len(b))
    zin = (  np.eye(n-1) - np.hstack( (-a[1:n, np.newaxis], np.vstack((np.eye(n-2), np.zeros(n-2))))))
    zid=  b[1:n] - a[1:n]*b[0]
    zi_matrix=np.linalg.inv(zin)*(np.matrix(zid).transpose())
    zi_return=[]
    for i in range(len(zi_matrix)):
      zi_return.append(float(zi_matrix[i][0]))
    return np.array( zi_return )

def FiltFilt( b, a, x ):
    # Filtro nos dois sentidos - apenas para vetores
    ntaps = max(len(a),len(b))
    edge = ntaps * 3
    if x.ndim != 1:
        raise ValueError, "Apenas arrays de dimensao 1."
    # x deve ser maior que o extremo
    if x.size < edge:
        raise ValueError, "Vetor de entrada maior que 3 * max(len(a),len(b)."
    if len(a) < ntaps:
        a = np.r_[a,np.zeros(len(b)-len(a))]
    if len(b) < ntaps:
        b = np.r_[b,np.zeros(len(a)-len(b))]
    zi = LFilter_zi( b, a )
    # Amplia o sinal para ter os extremos ao aplicar o sinal no sentido inverso
    s = np.r_[2*x[0]-x[edge:1:-1],x,2*x[-1]-x[-1:-edge:-1]]
    # Filtrando no sentido direto
    ( y, zf ) = lfilter( b, a, s, -1, zi*s[0] )
    # Filtrando no sentido inverso - removendo a fase
    ( y, zf ) = lfilter( b, a, np.flipud(y), -1, zi*y[-1] )
    # Removendo os extremos adicionados
    return np.flipud( y[edge-1:-edge+1] )

