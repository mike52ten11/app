from rest_framework import generics,status
from rest_framework.response import Response
from .models import AMI, Device
from .serializers import AMISerializer, DeviceSerializer
from .service import *

from django.db import connection

from django.http import JsonResponse

import datetime
from zoneinfo import ZoneInfo
import dateutil.parser as dp
import time

from django.views.generic import TemplateView, CreateView
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.password_validation import validate_password
from django.contrib import auth

from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_protect
from rest_framework.views import APIView


from .writeTxT import *
import logging
import os
# import decimal
from writedata.datefunction import *
from writedata.strfloatminus_and_convert_to_str import *

taiwan_timezone = ZoneInfo("Asia/Taipei")
os.makedirs('/home/app/postdata/latest/Log/Server/', exist_ok = True) 
logging.basicConfig(
    filename='/home/app/postdata/latest/Log/Server//ServerLog.log',
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger('System')

class RegisterView(APIView):

    def get(self, request, *args, **krgs):
        results = register_user(request.GET)
        print(results)
        if results["success"]:            
            responsedata = {'message':'ok',
                            'error_message': ''}                   
            return JsonResponse({'message':responsedata}, 
                                json_dumps_params={'ensure_ascii': False},
                                safe=False)
        else:
            responsedata = {'message':'error',
                            'error_message': results['errors']}            
            return JsonResponse({'message':responsedata}, 
                                json_dumps_params={'ensure_ascii': False},
                                safe=False)


class LoginView(APIView):

    def get(self, request, *args, **krgs):

        username = request.GET.get('username')
        password = request.GET.get('password')
        print(username)
        print(password)
        results = login_user(username=username, password=password)
        print(results)
        if results["success"]:            
            responsedata = {'message':results['message'],
                                'error_message': results['error_message']}
            return JsonResponse({'message':responsedata}, 
                                json_dumps_params={'ensure_ascii': False},
                                safe=False)
        else:
            responsedata = {'message':results['message'],
                                  'error_message': results['error_message'] }    

            return JsonResponse({'message':responsedata}, 
                                json_dumps_params={'ensure_ascii': False},
                                safe=False)


class DeviceListCreate(generics.ListCreateAPIView):
    queryset = Device.objects.all()
    serializer_class = DeviceSerializer

    def get(self, request, *args, **krgs):
        print(request.method)
        logger.info('request.method= %s',request.method)
        if len(request.GET)>0:
            
            request_username = request.GET.get('username','None')
            
            
            # print(USR.values())
            if not User.objects.filter(username=request_username).exists():
                responseData = {'message':'error',
                                      'error_message':'使用者='+request_username+' 未註冊'  }
                return JsonResponse({'message':responseData}
                                      ,json_dumps_params={'ensure_ascii': False}
                                      , safe=False) 

               
            request_deviceUuid = request.GET.get('deviceUuid','None')
            if not AMI.objects.filter(deviceUuid=request_deviceUuid).exists():
                responseData = {'message':'error',
                                'error_message':'沒有'+request_deviceUuid+'這個裝置ID'  }
                return JsonResponse({'message':responseData}
                                      ,json_dumps_params={'ensure_ascii': False}
                                      , safe=False) 

            if  Device.objects.filter(deviceUuid=request_deviceUuid).exists():

                logger.info(request_username+'要求綁定'+\
                            '裝置ID'+request_deviceUuid+\
                            '結果: '+'已被'+who_binding_the_device(deviceUuid=request_deviceUuid)+'綁定') 

                responseData = {'message':'error',
                                      'error_message':'這個裝置ID已被綁定'}
                return JsonResponse({'message':responseData}
                                      ,json_dumps_params={'ensure_ascii': False}
                                      , safe=False) 
            logger.info('len(request.GET)>0')
        else: 
            userrequestkey=['']
            for k in request.GET:
                userrequestkey = userrequestkey.append(k)
            logger.warning('使用者參數 %s',userrequestkey)
            return JsonResponse({'message':'錯誤的參數, api/register_device/?username=&deviceUuid='}, 
                                json_dumps_params={'ensure_ascii': False},
                                safe=False) 
        Errormessage = "錯誤參數"
        request_username_of_Errormessage=''
        request_deviceUuid_of_Errormessage=''

        if request_username=='None':
            request_username_of_Errormessage = " 參數裡沒有 username"
            

        if request_deviceUuid=='None':
            request_deviceUuid_of_Errormessage = " 參數裡沒有 deviceUuid"

        if request_username=='None' or request_deviceUuid=='None':

            logger.error('API Server參數錯誤 %s',Errormessage+request_username_of_Errormessage+request_deviceUuid_of_Errormessage)

            return JsonResponse({'message':'API Server參數錯誤'+Errormessage+request_username_of_Errormessage+request_deviceUuid_of_Errormessage}, safe=False)
        
        
        users = self.get_queryset()
        serializer = self.serializer_class(users, many=True)        
        data = serializer.data

        if request_deviceUuid!="None" and request_username!="None":

            Device.objects.create(  user= User.objects.filter(username=request_username).first(),
                                    deviceUuid=request_deviceUuid, 
                                ) 
                         
            responsedata = {'message':'ok',
                            'error_message': ''}
            return JsonResponse({'message':responsedata}, 
                                json_dumps_params={'ensure_ascii': False},
                                safe=False)

def update_device(request, *args, **krgs):

    request_username = request.GET.get('username','None')

    if not User.objects.filter(username=request_username).exists():
        responseData = {'message':'error',
                                'error_message':'使用者='+request_username+' 未註冊'  }
        return JsonResponse({'message':responseData}
                                ,json_dumps_params={'ensure_ascii': False}
                                , safe=False)      

    request_deviceUuid = request.GET.get('deviceUuid','None')

    if not AMI.objects.filter(deviceUuid=request_deviceUuid).exists():
        responseData = {'message':'error',
                                'error_message':'沒有'+request_deviceUuid+'這個裝置ID'  }
        return JsonResponse({'message':responseData}
                                ,json_dumps_params={'ensure_ascii': False}
                                , safe=False)     

    Device.objects.update(  user= User.objects.filter(username=request_username).first(),
                            deviceUuid=request_deviceUuid, 
                        ) 
    responsedata = {
                        'message':'ok',
                        'error_message':''
                    }                    
    return JsonResponse({'message':responsedata}, 
                        json_dumps_params={'ensure_ascii': False},
                        safe=False)

def Unbind_device(request, *args, **krgs):

    request_username = request.GET.get('username','None')

    if not User.objects.filter(username=request_username).exists():
        responseData = {'message':'error',
                        'error_message':'使用者='+request_username+' 未註冊'  }
        return JsonResponse({'message':responseData}
                                ,json_dumps_params={'ensure_ascii': False}
                                , safe=False)    
    delete_id = Device.objects.filter( user=User.objects.filter(username=request_username).first())
    
    if delete_id.exists():
        delete_id.delete()
        print(delete_id)
        # Device.objects.delete(pk=delete_id)
        responseData = {'message':'ok',
                        'error_message': '' }
        return JsonResponse({'message':responseData}
                                ,json_dumps_params={'ensure_ascii': False}
                                , safe=False)         
        # delete_id = delete_id.values()[0].get('id')

    else:
        responseData = {'message':'error',
                'error_message': '使用者未綁定任何裝置ID' }
        return JsonResponse({'message':responseData}
                                ,json_dumps_params={'ensure_ascii': False}
                                , safe=False)         







class AMIListCreate(generics.ListCreateAPIView):
    queryset = AMI.objects.all()
    serializer_class = AMISerializer

    def get(self, request, *args, **krgs):
        print(request.method)
        logger.info('request.method= %s',request.method)
        if len(request.GET)>0:
                   
            request_username = request.GET.get('username','None')
            request_timestamp = request.GET.get('date','None')
            request_interval = request.GET.get('interval','None')
            print(type(request_interval))
            logger.info('len(request.GET)>0')
            # return JsonResponse({'message':'request_timestamp='+request_timestamp
            #                                 +', '+str(iso8601_to_unixtimestamp(request_timestamp))})
        else: 
            userrequestkey=['']
            for k in request.GET:
                userrequestkey = userrequestkey.append(k)
            logger.warning('使用者參數 %s',userrequestkey)
            return JsonResponse({'message':'錯誤的參數, api/energy/?username=&date='}, 
                                json_dumps_params={'ensure_ascii': False},
                                safe=False) 

        Errormessage = "錯誤參數"
        request_username_of_Errormessage=''
        request_timestamp_of_Errormessage=''

        if request_username=='None':
            request_username_of_Errormessage = " 參數裡沒有 username"
            

        if request_timestamp=='None':
            request_timestamp_of_Errormessage = " 參數裡沒有 date"

        if request_username=='None' or request_timestamp=='None':

            logger.error('API Server參數錯誤 %s',Errormessage+request_username_of_Errormessage+request_timestamp_of_Errormessage)

            return JsonResponse({'message':'API Server參數錯誤'+Errormessage+request_username_of_Errormessage+request_timestamp_of_Errormessage}, safe=False)
        
        
        
        users = self.get_queryset()
        serializer = self.serializer_class(users, many=True)        
        data = serializer.data

        
                  
        
        if request_interval=='None':

            request_date = int(request_timestamp)

            if not User.objects.filter(username=request_username).exists():
                responseData = {'message':'error',
                                      'error_message':'使用者 '+request_username+' 未註冊'  }
                return JsonResponse({'message':responseData}
                                      ,json_dumps_params={'ensure_ascii': False}
                                      , safe=False)   
                                      
            if Device.objects.filter( user=User.objects.filter(username=request_username).first()).exists():

               deviceUuid = Device.objects.get(user=User.objects.filter(username=request_username).first()).deviceUuid 
            else:
                responseData = {'message':'error',
                        'error_message': '使用者未綁定任何裝置ID' }                
                return JsonResponse({'message':responseData}
                                        ,json_dumps_params={'ensure_ascii': False}
                                        , safe=False)                

            
         
            startdate = get_start_time_of_a_day(request_date)            
            print(startdate)

            startdate_value = get_Ami_Kwh_Data({'generatedTime':startdate,'deviceUuid':deviceUuid})
            
            if startdate==request_date:
                enddate = request_date+86340000
            else:
                enddate = request_date

            enddate_value = get_Ami_Kwh_Data({'generatedTime':enddate,'deviceUuid':deviceUuid})

            #enddate_value-startdate_value
            if startdate_value=='0':
                responseData = {'message':'error',
                        'error_message': str(unixtimestamp_to_datetime(startdate/1000))+'沒有資料' }                
                return JsonResponse({'message':responseData}
                                        ,json_dumps_params={'ensure_ascii': False}
                                        , safe=False)      
            elif   enddate_value=='0':
                responseData = {'message':'error',
                        'error_message': str(unixtimestamp_to_datetime(enddate/1000))+'沒有資料' }                
                return JsonResponse({'message':responseData}
                                        ,json_dumps_params={'ensure_ascii': False}
                                        , safe=False)   
                                                                                      
            date_value = strfloatminus_and_convert_to_str(startdate_value, enddate_value)

            logger.info('API要求日期=%s, 裝置ID=%s,使用者=%s ,回傳 %s到%s 的用電量= %s'
                        ,unixtimestamp_to_datetime(request_date/1000)
                        ,deviceUuid
                        ,request_username
                        ,unixtimestamp_to_datetime(int(startdate)/1000)
                        ,unixtimestamp_to_datetime(int(enddate)/1000)
                        ,date_value)

            responseData = {"response Data":{"kwh":date_value}}

            return JsonResponse({'message':responseData}, safe=False)  


        else: 

            request_date = int(request_timestamp)
            username = request_username
            internval = int(request_interval)
            request_datetime = unixtimestamp_to_datetime(request_date)
            
            mondy_of_current_week, sundy_of_current_week = get_current_week(request_datetime)
            print(get_dates(mondy_of_current_week, sundy_of_current_week))
            # mondy_of_last_week, sundy_of_last_week = get_last_week('2023-12-06')
            # print(get_dates(mondy_of_current_week, sundy_of_current_week))
            # print(get_dates(mondy_of_last_week, sundy_of_last_week))
            
            # print(date)            


            

            startdate=request_date
            enddate = startdate+86340000 #+24小時
            kwh = []
            for loop in range(internval):

                
                start_kwh = get_Ami_Kwh_Data({'generatedTime':startdate,'deviceUuid':username})
                end_kwh = get_Ami_Kwh_Data({'generatedTime':enddate,'deviceUuid':username})        
                start_kwh = decimal.Decimal(start_kwh) 
                end_kwh = decimal.Decimal(end_kwh)      

                kwh.append(str(end_kwh-start_kwh))
                infopara = unixtimestamp_to_iso8601(startdate/1000)+\
                            '~'+unixtimestamp_to_iso8601(enddate/1000)+\
                            ' 用電量='+str(end_kwh-start_kwh)+'度'
                logger.info(infopara)
   
                startdate = enddate+60000#+1分鐘
                enddate = startdate+86340000
                    
            
            logger.info('API要求時間%s, 使用者%s,區間%s天, 回傳 %s',date,username,internval,kwh)
            responseData = {"response Data":{"kwh":kwh}}

            return JsonResponse({'message':responseData}, safe=False)  

    def post(self, request,*args, **krgs):
        print(request.method)
        # data = request.data

        request_deviceUuid = request.GET.get('deviceUuid',"None")
        request_generatedTime = request.GET.get('generatedTime','None')
        request_value = request.GET.get('value','None')

        
  
        if request_deviceUuid!="None" and request_generatedTime!="None" and request_value!="None":
            request_generatedTime = int(request_generatedTime)
            AMI.objects.create(deviceUuid=request_deviceUuid, 
                            generatedTime=request_generatedTime,  
                            value=request_value) 
                         
            responseData = "新增成功"    
        else:
            deviceUuid_of_responseData = ''
            generatedTime_of_responseData = ''
            value_of_responseData = ''
            if request_deviceUuid!="None":
              deviceUuid_of_responseData = "參數裡沒有 deviceUuid " 
            if request_generatedTime!="None":
              generatedTime_of_responseData = "參數裡沒有 generatedTime "
            if request_value!="None":
              value_of_responseData = "參數裡沒有 value " 
            responseData =  deviceUuid_of_responseData+\
                            generatedTime_of_responseData +\
                            value_of_responseData                  
        # except Exception as e:
        #     responseData = {'error': str(e)}

        return JsonResponse({'message':responseData}, 
                                json_dumps_params={'ensure_ascii': False},
                                safe=False)  



def deleteall(request):
    try:
        AMI.objects.all().delete()
        with connection.cursor() as cursor:
            # cursor.execute("SELECT generatedTime FROM writedata_ami WHERE deviceUuid = %s;",[username])
            cursor.execute("UPDATE sqlite_sequence SET seq = 0 WHERE sqlite_sequence.name = %s;",['writedata_ami'])
            # a = cursor.fetchall()        
        
        deletemessage = '資料全部刪除成功'
    except Exception as error:
        writeTxT('errorlog.log',str(error))
        deletemessage = '資料刪除失敗'+str(error)
    return JsonResponse({'message':deletemessage},
                    json_dumps_params={'ensure_ascii': False}, 
                    safe=False) 


def updatedata(request):
    
    request_username = request.GET.get('username','None')
    request_timestamp = request.GET.get('date','None')
    update_kwh = request.GET.get('kwh','None')
    Erromessage='參數要有'

    if request_username=='None':
       Erromessage = Erromessage+'username' 
       
    
    if request_timestamp=='None':
       Erromessage = Erromessage+' date(unix timestamp格式)'        
    
    if update_kwh=='None':
       Erromessage = Erromessage+' kwh' 

    if Erromessage!='參數要有':  
        return JsonResponse({'message':Erromessage+'。'},
                            json_dumps_params={'ensure_ascii': False}, 
                            safe=False)

    date = int(request_timestamp)
    username = str(request_username)    
    databasecolumn = AMI.objects.get(date=date, username=username)
     
    print(update_kwh)
    
    
    # databasecolumn.date = date

    # databasecolumn.username = username
    databasecolumn.kwh = update_kwh
    databasecolumn.save()
    return JsonResponse({'message':'update success'}, safe=False) 


    
def get_Ami_Kwh_Data(dic):

    kwh = AMI.objects.filter(**dic)
    
    
    if kwh.exists():         
        kwh = kwh.values()
        kwh = kwh[0].get('value')
        
    else:    
        kwh = '0'

    return kwh

def  WorkFlow_of_get_Ami_Kwh_Data(request_date):

    request_datetime = unixtimestamp_to_datetime(request_date/1000)
    now_datetime = datetime.datetime.today()
    # if request_datetime < now_datetime:

def who_binding_the_device(deviceUuid):

    return  str( User.objects.get  (
                                    pk= Device.objects.filter
                                        (
                                            deviceUuid=deviceUuid
                                        ).values()[0].get('user_id')
                                )
            )




