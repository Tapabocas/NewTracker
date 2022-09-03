from datetime import datetime
from datetime import timedelta

print (type((datetime.now())))

date='2022-08-26 12:55:00'
deit=datetime.strptime(date,'%y/%m/%d %H:%M:%S')
print (type(deit))