
import epmwebapi as epm
#from epmwebapi.dataobjectattributes import DataObjectAttributes
#from epmwebapi.dataobjectsfilter import DataObjectsFilter
#from epmwebapi.dataobjectsfilter import DataObjectsFilterType
#from epmwebapi.domainfilter import DomainFilter

import datetime as dt
import numpy as np
import pandas as pd
import getpass
import logging
import argparse

'''
TODO: CSV dialect discover
'''



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
parser = argparse.ArgumentParser(description='CSV to EPM - update EPM Basic Variables using epmwebapi default ports(44333 and 44332)',epilog="kotres@elipse.com.br")
# server name argument, if ignored use "localhost"
parser.add_argument('-server', default ='localhost',
                    help='server name - (default: localhost)')

# user name argument, if ignored use "sa"
parser.add_argument('-user', default ='sa',
                    help='user name - (default: sa)')

# bv name argument, required
parser.add_argument('-bv',
                    help='epm basic variable name')

# file path argument, required
parser.add_argument('-csv',
                    help='csv path name')

# value column name argument, required
parser.add_argument('-v',
                    help='value column name')

# timestamp column name argument, required
parser.add_argument('-t',
                    help='timestamp column name')


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

#discover dialect reading first 10 lines and using python engine
try:
    reader = pd.read_csv(csvfile, sep = None, iterator = True,engine='python',nrows=10)
    inferred_sep = reader._engine.data.dialect.delimiter
    logger.info('Inferred separator: {}'.format(inferred_sep))
except Exception:
    logger.error("can't discover csv delimiter (: , |...)")
    exit(1)
#read file
try:
    #read all file using inferred separator and c engine(faster)
    df1 = pd.read_csv(csvfile,sep=inferred_sep, encoding='utf-8', decimal='.', engine='c')
    df_copy = df1.copy(deep=True)
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
pswd = getpass.getpass("EPM {} password:".format(user))
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
logger.info('Sort and clean...')
pd.to_numeric(df1[v_column], errors='coerce')
df1[v_column].replace(np.nan, 0,inplace=True)
df1[t_column].replace(' ', np.nan, inplace=True)
df1.dropna(subset=[v_column], inplace=True)
df1.dropna(subset=[t_column], inplace=True)
logger.info('Csv cleaned rows count: {}'.format(len(df1.index)))

#sort by datetime
df1[t_column] = pd.to_datetime(df1[t_column], utc=True)
newdf = df1.sort_values(by=t_column)
newdf = newdf.reset_index(drop=True)

newdf = newdf[[v_column,t_column]]


#epm data format
desc = np.dtype([('Value', '>f8'),('Timestamp','object'),('Quality','>i4')])
datatemp = np.empty(len(df1.index), dtype=desc)


#iteration loop to create EPM format ndarray
#TODO: insert 128 if bad quality
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

#TODO: arrumar esse teste
if np.array_equal(datatemp['Timestamp'],bv['Timestamp']):
    logger.info('Timestamp data Ok!')
else:
    logger.info('Timestamp data lost!')

if np.array_equal(datatemp['Value'],bv['Value']):
    logger.info('Value data Ok!')
else:
    logger.info('Value data lost!')


logger.info('End Process')


logger.info('execution time:{}'.format(endtime-initime))


