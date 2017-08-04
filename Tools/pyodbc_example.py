import pyodbc


#odbc connection
cnxn = pyodbc.connect('DRIVER={SQL Server};SERVER=.\SQLExpress;DATABASE=DTS_Test;UID=????;PWD=?????')
cursor = cnxn.cursor()


querystring = 'SELECT * FROM Hist_SupportTest1'
cursor.execute(querystring)

rows = cursor.fetchall()


for item in rows:
    print item

