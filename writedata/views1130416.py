from rest_framework import generics
from .models import Energy
from .serializers import EnergySerializer
from django.db import connection
from django.http import JsonResponse


from django.views.generic import TemplateView, CreateView
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.password_validation import validate_password




import requests
from datetime import datetime, timezone, timedelta
import dateutil.parser as dp
from zoneinfo import ZoneInfo
import time
import json
import logging
import os

os.makedirs('./Log/APIServer/', exist_ok = True)
logging.basicConfig(
    filename='./Log/APIServer/API_ServerLog.log',
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger('API_Server')

taiwan_timezone = ZoneInfo("Asia/Taipei")

server_IP = 'https://mike521011.pythonanywhere.com/'

def iso8601_to_unixtimestamp(iso8601):
    iso8601 = dp.parse(iso8601)
    print(iso8601)
    print(type(iso8601))

    return time.mktime(iso8601.timetuple())

def call_resource_database_api(username,qrid ,date):
    url = server_IP+'api/energy/'
    # url = 'http://10.52.15.201:800/api/energy/'
    params = {
      'username': username,
      'date':  date,
      'qrid': qrid
    }

    response = requests.get(url, params=params)
    data = response.json()
    try:
        return data['message']['response Data']['kwh']
    except:
        print('yes')
        return data['message']

def call_resource_database_api_with_time_interval(username, date, interval):
    url = server_IP+'api/energy/'
    # url = 'http://10.52.15.201:800/api/energy/'
    params = {
      'username': username,
      'date':  date,
      'interval': interval
    }

    response = requests.get(url, params=params)
    data = response.json()
    try:
        return data['message']['response Data']['kwh']
    except:
        print('yes')
        return data['message']

def login_user_api(username,password):
    url = server_IP+'api/login/'
    # url = 'http://10.52.15.201:800/api/login/'
    params = {
      'username': username,
      'password': password,
    }

    response = requests.get(url, params=params)
    data = response.json()
    return data['message']

def register_user_api(username,password):
    url = server_IP+'api/register/'
    # url = 'http://10.52.15.201:800/api/register/'
    params = {
      'username': username,
      'password': password,
    }

    response = requests.get(url, params=params)
    data = response.json()

    return data['message']

def register_device_api(username,qrid):
    url = server_IP+'api/register_device/'
    # url = 'http://10.52.15.201:800/api/register_device/'
    params = {
      'username': username,
      'qrid': qrid,
    }

    response = requests.get(url, params=params)
    data = response.json()

    return data['message']

def update_device_api(username,deviceUuid):
    url = server_IP+'api/update_device/'
    # url = 'http://10.52.15.201:800/api/update_device/'
    params = {
      'username': username,
      'deviceUuid': deviceUuid,
    }

    response = requests.get(url, params=params)
    data = response.json()

    return data['message']



def login(request, *args, **krgs):

    username = request.GET.get('username')

    password = request.GET.get('password')
    msg = login_user_api(username,password)
    logger.warning(msg)

    return JsonResponse(msg,
            json_dumps_params={'ensure_ascii': False},
            safe=False)

def register(request, *args, **krgs):

    username = request.GET.get('username')

    password = request.GET.get('password')
    msg = register_user_api(username,password)
    logger.warning(msg)

    return JsonResponse(msg,
            json_dumps_params={'ensure_ascii': False},
            safe=False)

def register_device(request, *args, **krgs):

    username = request.GET.get('username')

    qrid =  request.GET.get('qrid')

    msg = register_device_api(username,qrid)
    logger.warning(msg)

    return JsonResponse(msg,
            json_dumps_params={'ensure_ascii': False},
            safe=False)

def update_device(request, *args, **krgs):
    username = request.GET.get('username')

    deviceUuid =  request.GET.get('deviceUuid')

    msg = update_device_api(username,deviceUuid)
    logger.warning(msg)

    return JsonResponse(msg,
            json_dumps_params={'ensure_ascii': False},
            safe=False)

def unbind_device_api(username,qrid):
    url = server_IP+'api/Unbind_device/'
    # url = 'http://10.52.15.201:800/api/update_device/'
    params = {
      'username': username,
      'qrid': qrid,
    }

    response = requests.get(url, params=params)
    data = response.json()

    return data['message']

def Unbind_device(request, *args, **krgs):
    username = request.GET.get('username')

    qrid =  request.GET.get('qrid')

    msg = unbind_device_api(username,qrid)
    logger.warning(msg)

    return JsonResponse(msg,
            json_dumps_params={'ensure_ascii': False},
            safe=False)

def parse_date_of_userParasmeter_and_transfor_to_dateParasmeter_of_server(request_date):
    request_date_for_many = request_date.split(',')
    print('type(request_date_for_many) = ',type(request_date_for_many))
    request_date_for_iso8601_to_unixtimestamp = []

    for request_date in request_date_for_many:
        # print(request_date)
        request_date = str(int(iso8601_to_unixtimestamp(request_date)-8*60*60)).ljust(13,'0')
        # print('iso8601_to_unixtimestamp = ',request_date)
        request_date_for_iso8601_to_unixtimestamp.append(request_date)
    request_date = ','.join(request_date_for_iso8601_to_unixtimestamp)
    print('解析後 = ',request_date)
    return   request_date

class EnergyListCreate(generics.ListCreateAPIView):
    queryset = Energy.objects.all()
    serializer_class = EnergySerializer

    def get(self, request, *args, **krgs):
        print(request.method)
        logger.info('request.method= %s',request.method)
        if len(request.GET)>0:
            request_username = request.GET.get('username','None')
            request_date = request.GET.get('date','None')
            request_qrid = request.GET.get('qrid','None')
            request_interval = request.GET.get('interval','None')
            print('request_username = ', request_username)
            print('request_date = ', type(request_date))
            print('request_interval = ', request_interval)


            logger.info('request_username =%s request_date =%s ', type(request_username),type(request_username))
        else:

            logger.warning('使用者參數 %s','['']')
            return JsonResponse({'message':'錯誤的參數, 網址是http://API伺服器IP/api/energy/?username=&date='},
                                json_dumps_params={'ensure_ascii': False},
                                safe=False)
        Errormessage = "錯誤參數"
        request_username_of_Errormessage=''
        request_date_of_Errormessage=''
        request_qrid_of_Errormessage=''

        if request_username=='None':
            request_username_of_Errormessage = " 參數裡沒有 username"


        if request_date=='None':
            request_date_of_Errormessage = " 參數裡沒有 date"

        if request_qrid=='None':
            request_qrid_of_Errormessage = " 參數裡沒有 qrid"

        if request_username=='None' or request_date=='None' or request_qrid=='None':

            logger.error('使用者者參數錯誤 %s',Errormessage+request_username_of_Errormessage+request_date_of_Errormessage)

            return JsonResponse({'Errormessage':Errormessage+request_username_of_Errormessage+request_date_of_Errormessage+request_qrid_of_Errormessage},
                                json_dumps_params={'ensure_ascii': False},
                                safe=False)


        request_date = parse_date_of_userParasmeter_and_transfor_to_dateParasmeter_of_server(request_date)

        print('request_date with , = ',request_date)
        if request_interval=='None':
            responseData = call_resource_database_api(request_username,request_qrid,request_date)
        else:
            request_interval = int(request_interval)
            print(type(request_interval))
            print(request_interval)
            responseData = call_resource_database_api_with_time_interval(request_username,request_date,request_interval)
        return JsonResponse({'message':responseData}, json_dumps_params={'ensure_ascii': False},safe=False)