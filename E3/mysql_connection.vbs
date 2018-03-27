dim cn, rs

set cn = CreateObject("ADODB.Connection")
set rs = CreateObject("ADODB.Recordset")
cn.connectionString = "Driver={MySQL ODBC 5.1 Driver};Server=yourServerAddress;" & _
                   "Database=yourDataBase;User=yourUsername;" & _
                   "Password=yourPassword;"
cn.open
rs.open "select * from table", cn, 3
rs.MoveFirst
while not rs.eof
    MessageBox rs(0)
    rs.next
wend
cn.close

