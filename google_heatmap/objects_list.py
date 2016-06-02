
import epm_connection as epm
import datetime
import csv


init_time = datetime.datetime.now()
print 'Hora inicio:',init_time


conn = epm.NewConnection()
conn = conn.create_connection(server='localhost',user='sa',psw='Abcd1234')

objects = epm.GetDataObject()

tag_list = []
listtags = objects.get_taglist(connection=conn)

for item in listtags:
    tag_list.append(item.DisplayName)

with open('taglist.csv','wb')as myfile:
    wr = csv.writer(myfile,quoting=csv.QUOTE_ALL)
    wr.writerow(tag_list)

print tag_list



end_time = datetime.datetime.now()
print 'Hora fim:',end_time
print 'Tempo total:',end_time-init_time