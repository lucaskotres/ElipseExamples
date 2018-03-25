


# Copyright 2018 Lucas Kotres

#TODO: Validar gravação de dados
#TODO: incluir funçao para descobrir dialetica
#TODO: Possibilidade de usar a lib Rows para importar outros tipos de dados.

import epmwebapi as epm
from epmwebapi.dataobjectattributes import DataObjectAttributes
from epmwebapi.dataobjectsfilter import DataObjectsFilter
from epmwebapi.dataobjectsfilter import DataObjectsFilterType
from epmwebapi.domainfilter import DomainFilter

import datetime as dt
import numpy as np
import pandas as pd
import getpass
import logging
import argparse

#########################initialization code##############################


#log config
logFormatter = logging.Formatter("%(asctime)s  [%(levelname)-5.5s]  %(message)s")
logger = logging.getLogger()

fileHandler = logging.FileHandler("csv2epm.log")
fileHandler.setFormatter(logFormatter)
logger.addHandler(fileHandler)

consoleHandler = logging.StreamHandler()
consoleHandler.setFormatter(logFormatter)
logger.addHandler(consoleHandler)
logger.setLevel(logging.DEBUG)


# Instantiate the parser
parser = argparse.ArgumentParser(description='CSV to EPM - update EPM Basic Variables using epmwebapi default ports(44333 and 44332)',epilog="Problems? better call kotres",formatter_class=argparse.RawTextHelpFormatter)
# server name argument, if ignored use "localhost"
parser.add_argument('-server', default ='localhost',
                    help='server name - (default: localhost)')

# user name argument, if ignored use "sa"
parser.add_argument('-user', default ='sa',
                    help='user name - (default: sa)')

# bv name argument, required
parser.add_argument('-bv', 
                    help='(required if dont use configfile)epm basic variable name')

# file path argument, required
parser.add_argument('-csv', 
                    help='(required if dont use configfile)csv file path name')

# value column name argument, required
parser.add_argument('-v', 
                    help='(required if dont use configfile)value column name')

# timestamp column name argument, required
parser.add_argument('-t', 
                    help='(required if dont use configfile)timestamp column name')


# Argument to use config file
parser.add_argument('-f', 
                    help='(Optional) if using json configfile - format:{"server":"servername","user":"username","bvname":"bvname","csvfile":"csvfilepath","value":"valuecolumnname","timestamp":"timestampcolumnname"}')

args = parser.parse_args()



#parse prompt arguments
if args.f != None:
    try:
        import json
        with open(args.f) as json_data:
            d = json.load(json_data)
            server = d['server']
            user = d['user']
            bvname = d['bvname']
            csvfile = d['csvfile']
            v_column = d['value']
            t_column = d['timestamp']
            logger.info('configfile ok!.')
    except Exception:
        logger.error('failed to open file.')
        exit(1)

else:

    server = args.server
    user = args.user
    bvname = args.bv
    csvfile = args.csv
    v_column = args.v
    t_column = args.t

initime = dt.datetime.now()

#Arguments validation
logger.info('Verifing csv...')

#read file
try:
    df1 = pd.read_csv(csvfile, sep=';',lineterminator='\r',decimal='.')
except Exception:
    logger.error("can't read file: {}".format(csvfile))
    exit(1)

#read value column

if  not v_column in df1.columns:
    logger.error("can't found {} column in csvfile.".format(v_column))
    exit(1)

#read timestamp column
if not t_column in df1.columns:
    logger.error("can't found {} column in csvfile.".format(t_column))
    exit(1)


logger.info('Verifing epm...')
pswd = getpass.getpass("EPM {}'s password:".format(user))
try:
    connection = epm.EpmConnection('http://'+server+':44333', 'http://'+server+':44332', user, pswd) 
    #TODO: Conseguir capturar essa exceção, está passando direto. 
except Exception:
    logger.error("can't connect to epm server")
    exit(1)

try:
    bv = connection.getDataObjects([bvname])
    #TODO: Conseguir capturar essa exceção , está passando direto.
except Exception:
    logger.error("can't found {} in the epm Server".format(bvname))
    exit(1) 


logger.info('Parameters ok!')


# Print iterations progress
def printProgressBar (iteration, total, prefix = '', suffix = '', decimals = 1, length = 100, fill = '█'):
    """
    Call in a loop to create terminal progress bar
    @params:
        iteration   - Required  : current iteration (Int)
        total       - Required  : total iterations (Int)
        prefix      - Optional  : prefix string (Str)
        suffix      - Optional  : suffix string (Str)
        decimals    - Optional  : positive number of decimals in percent complete (Int)
        length      - Optional  : character length of bar (Int)
        fill        - Optional  : bar fill character (Str)
    """
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filledLength = int(length * iteration // total)
    bar = fill * filledLength + '-' * (length - filledLength)
    print('\r%s |%s| %s%% %s' % (prefix, bar, percent, suffix), end = '\r')
    # Print New Line on Complete
    if iteration == total: 
        print()





#####################data manipulation##########################
#TODO: converter corretamente a coluna de valores.

#sort and clean - df1 to newdf
logger.info('Csv original rows count: {}'.format(len(df1.index)))
logger.info('Sorting and cleaning data...')
df1[v_column].replace(np.nan, 0,inplace=True)
df1['Date_time'].replace(' ', np.nan, inplace=True)
df1.dropna(subset=[v_column], inplace=True)
df1.dropna(subset=['Date_time'], inplace=True)
logger.info('Csv cleaned rows count: {}'.format(len(df1.index)))


df1['Date_time'] = pd.to_datetime(df1['Date_time'], utc=True)
newdf = df1.sort_values(by='Date_time')


#epm data format
desc = np.dtype([('Value','>f8'),('Timestamp','object'),('Quality','>i4')])
datatemp = np.empty(len(df1.index), dtype=desc)

#iteration loop to create EPM format ndarray 
i = 0
printProgressBar(0, len(df1.index), prefix = 'Creating EPM array:', suffix = 'Complete', length = 50)
while i < len(df1.index):
    datatemp['Value'][i] = newdf[v_column][i]
    datatemp['Timestamp'][i] = newdf[t_column][i]
    datatemp['Quality'][i] = 0    
    #print('datatemp:{} index:{}'.format(datatemp[i], i))
    printProgressBar(i + 1, len(df1.index), prefix = 'Creating EPM array:', suffix = 'Complete', length = 50)   
    i = i + 1 


#EPM data write
logger.info('Writing data. Wait a minute...')
bv[bvname].historyUpdate(datatemp)
endtime = dt.datetime.now() 
logger.info('Write finished!')

#TODO: Verificação de inconsistências - comparação entre o datatemp e uma consulta raw do mesmo período.
logger.info('Verifing inconsistencies...')

queryPeriod = epm.QueryPeriod(newdf[t_column][0], newdf[t_column][-1])
bv = bv[bvname].historyReadRaw(queryPeriod)

import matplotlib.pyplot as plt

fig, (ax0, ax1) = plt.subplots(nrows=2)
ax0.set_title('Basic Variable: {}'.format(v_column))
ax1.set_title('Basic Variable: {}'.format(bvname))

ax0.plot(newdf[t_column],newdf[v_column])
#ax0.plot(bv['Timestamp'],bv['Value'])
ax0.plot(datatemp['Timestamp'],datatemp['Value'])
#ax1.plot(bv['Timestamp'],bv['Value'])

plt.tight_layout()
plt.show()

if np.array_equal(datatemp,bv):
    logger.info('Data Ok!')
else:
    logger.info('Data lost!')


logger.info('End Process')


logger.info('execution time:{}'.format(endtime-initime))


