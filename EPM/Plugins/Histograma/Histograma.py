# coding=utf-8

# EPM Plugins
import Plugins as ep

import matplotlib.pyplot as plt
import matplotlib.mlab as mlab


@ep.DatasetFunctionPlugin('Visualizar Histograma', 1)#Decorator criado pela Elipse para que o Plugin seja executado pelo EPM Studio.
def histograma():
    # Verifica se existe apenas uma pena selecionada no Dataset Analysis.
    if len(ep.EpmDatasetPens.SelectedPens) != 1:
        ep.showMsgBox("EPM - Histograma",
                      "Execute a consulta do Dataset Analysis \n e selecione uma pena antes de aplicar a funcao.",
                      "Warning")
        return 0

    # Passa para a variavel 'epm_tag' a variavel selecionada.
    epm_tag = ep.EpmDatasetPens.SelectedPens[0].Values
    x = epm_tag["Value"]
    mu = epm_tag["Value"].mean()  # Mediana da amostra
    sigma = epm_tag["Value"].std()  # Desvio padrao da amostra

    # Quantidade de valores que desejamos agrupar. (barras verdes)
    num_bins = 20
    # Gera o histograma
    n, bins, ignore = plt.hist(x, num_bins, normed=1, facecolor='green', alpha=0.5)
    # Adiciona uma linha indicando a curva de normalidade (vermelha tracejada)
    y = mlab.normpdf(bins, mu, sigma)
    plt.plot(bins, y, 'r--')
    plt.title("Histograma  \n $\mu=" + "{:.3f}".format(mu) + "$, $\sigma=" + "{:.3f}".format(sigma) + "$")

    # Mostra na tela o gráfico
    plt.subplots_adjust(left=0.15)
    plt.show()

