import datetime
from zoneinfo import ZoneInfo
import dateutil.parser as dp
import time
import sys
taiwan_timezone = ZoneInfo("Asia/Taipei")

def unixtimestamp_to_iso8601(unixtimestamp):
    iso = datetime.datetime.fromtimestamp(unixtimestamp,taiwan_timezone).isoformat()
    return iso
    
def iso8601_to_unixtimestamp(iso8601):
    iso8601 = dp.parse(iso8601)
    print(iso8601)
    print(type(iso8601))
    
    return time.mktime(iso8601.timetuple())

def datetime_to_unixtimestamp(date_time):
    # import logging

    # logger = logging.getLogger('System')
    # logger.info('作業系統 %s',sys.platform)    
    if sys.platform.startswith('linux'): # 包含 linux 與 linux2 的情況
        return time.mktime(date_time.replace(tzinfo=taiwan_timezone).utctimetuple())#linux用的
    
    elif sys.platform.startswith('darwin'):
        print('macOS')
        return time.mktime(date_time.replace(tzinfo=taiwan_timezone).utctimetuple())#macOSv
    elif sys.platform.startswith('win32'):
            
        return datetime.datetime.timestamp(date_time) #windows用的  


def unixtimestamp_to_datetime(unixtimestamp):   
    return datetime.datetime.fromtimestamp(unixtimestamp,taiwan_timezone)    

def get_current_week(date=None):
    if date:
        duty_date = datetime.datetime.strptime(str(date), '%Y-%m-%d')
        monday, sunday = duty_date, duty_date
    else:
        monday, sunday = datetime.date.today(), datetime.date.today()
    one_day = datetime.timedelta(days=1)
    while monday.weekday() != 0:
        monday -= one_day
    while sunday.weekday() != 6:
        sunday += one_day
 
    # return monday, sunday
    # 返回时间字符串
    return datetime.datetime.strftime(monday, "%Y-%m-%d"), datetime.datetime.strftime(sunday, "%Y-%m-%d")

def get_last_week(date=None):
    if date:
        today = datetime.datetime.strptime(str(date), '%Y-%m-%d')
    else:
        today = datetime.datetime.today()
    end_time = today - datetime.timedelta(days=today.isoweekday())
    start_time = end_time - datetime.timedelta(days=6)
    return start_time.strftime("%Y-%m-%d"), end_time.strftime("%Y-%m-%d")

def get_dates(start_date, end_date):
    dates = list()
    start_date = datetime.datetime.strptime(start_date, '%Y-%m-%d')
    end_date = datetime.datetime.strptime(end_date, '%Y-%m-%d')
    dates.append(start_date.strftime('%Y-%m-%d'))
    while start_date < end_date:
        start_date += datetime.timedelta(days=1)
        dates.append(start_date.strftime('%Y-%m-%d'))
    return dates

def get_start_time_of_a_day(request_datetime):# request_datetime type=unix timestamp

    start_time = unixtimestamp_to_datetime(request_datetime/1000)
    print(start_time)
    start_time = start_time.replace(hour=0, minute=0, second=0)
    print(start_time)

    start_time = datetime_to_unixtimestamp(start_time)         
    print(start_time)   
    start_time = int(str(int(start_time)).ljust(13,'0'))  

    return start_time    