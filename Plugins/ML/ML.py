# coding=utf-8

#Machine Learning Toolbox
import Plugins as ep
import tools
import pandas as pd

MSG_MSGBOXTITLE = 'EPM - Message'
ERR_NOPENSELECTED = 'Please, execute dataset then select one pen'


@ep.DatasetFunctionPlugin('Linear Regression', 1)
def linear_regression():
    if len(ep.EpmDatasetPens.SelectedPens) != 1:
        ep.showMsgBox(MSG_MSGBOXTITLE, ERR_NOPENSELECTED, 'Warning')
        return 0

    epm_tag = ep.EpmDatasetPens.SelectedPens[0].Values

    

    print(epm_tag)


@ep.DatasetFunctionPlugin('function 1', 2)
def function1():

    pass


@ep.DatasetFunctionPlugin('function 2', 3)
def function2():

    pass


@ep.DatasetFunctionPlugin('function 3', 4)
def function3():

    pass


@ep.DatasetFunctionPlugin('function 4', 5)
def function4():

    pass


@ep.DatasetFunctionPlugin('Run Test', 6)
def run_test():

    if len(ep.EpmDatasetPens.SelectedPens) != 1:
        ep.showMsgBox(MSG_MSGBOXTITLE, ERR_NOPENSELECTED, 'Warning')
        return 0

    epm_tag = ep.EpmDatasetPens.SelectedPens[0].Values

    #convert numpy to pandas dataframe
    print(tools.np2pd(epm_tag))


    #plot line
    tools.plot(epm_tag['Value'])


    #print OLS Summary
    #tools.print_OLS(tools.np2pd(epm_tag))

    tools.test_stationarity(tools.np2pd(epm_tag))



