
import numpy as np #biblioteca numpy - http://www.numpy.org/

a = np.array([25, 26, 225, 24, 23, 24, 25, 325, 28, 27]) #array com os elementos do conjunto


def removeoutlier(values):                     #define a função com uma variavel de entrada
    fator = 1.5                                #1.5 é o fator de multiplicacao
    q75, q25 = np.percentile(values, [75, 25]) #retorna o terceiro e primeiro quartil
    iqr = q75 - q25                            #calcula o iqr(interquartile range)

    lowpass = q25 - (iqr * fator)              #calcula o valor minimo para aplicar no filtro
    highpass = q75 + (iqr * fator)             #calcula o valor maximo para aplicar no filtro

    outliers = np.argwhere(values < lowpass)   #descobre onde estao os valores menores que o valor minimo
    values = np.delete(values, outliers)       #deleta esses valores

    outliers = np.argwhere(values > highpass)  #descobre onde estao os valores maiores que o valor maximo
    values = np.delete(values, outliers)       #deleta esses valores

    return values                              #retorna a variavel sem outliers


#teste
print a                #imprime a variavel com outliers
print removeoutlier(a) #imprime a variavel sem outliers
