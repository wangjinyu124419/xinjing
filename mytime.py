import datetime
import time
#
# t=time.localtime()
# print(t)
t=time.localtime()
today_begin = '%d-%02d-%02d' % (t.tm_year, t.tm_mon, t.tm_mday)
today_begin_date = datetime.datetime.strptime(today_begin, '%Y-%m-%d')
for i in range(15):
    begin_date = today_begin_date - datetime.timedelta(days=(i))

    end_date = today_begin_date - datetime.timedelta(days=(i - 1))
    User
