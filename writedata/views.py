from rest_framework import generics,status
from rest_framework.response import Response
from .models import AMI, Device,DeviceTransfor
from .serializers import AMISerializer, DeviceSerializer,DeviceTransforSerializer
from .service import *

from django.db import connection
from django.db.models import Max

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
os.makedirs(f"Log/Server/", exist_ok = True) 
logging.basicConfig(
    filename=f"Log/Server/ServerLog.log",
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
        results = login_user(username=username, password=password)
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
    '''
    =======================================================================================================
                
                                    使用者 綁定 裝置
        功能: 使用者 綁定 多個裝置，傳入的必要參數是使用者名稱、QRID

        Step 1 : 檢查是否有輸入參數
        Step 2 : 檢查必要參數是否都有輸入
        Step 3 : 檢查使用者有沒有註冊
        Step 4 : 檢查資料庫有沒有這個裝置
        Step 5 : 檢查這個裝置ID有沒有被綁定
        Step 6 : 如果都有必要參數(deviceUuid、和 username)就執行綁定的動作
    =======================================================================================================

    '''    
    queryset = Device.objects.all()
    serializer_class = DeviceSerializer

    def get(self, request, *args, **krgs):
        
        logger.info('request.method= %s',request.method)
        #Step 1 : 檢查是否有輸入參數
        if len(request.GET)>0:

            request_username = request.GET.get('username','None')
            request_qrid = request.GET.get('qrid','None')

            #Step 2 檢查必要參數是否都有輸入
            Errormessage = "錯誤參數"
            request_username_of_Errormessage=''
            request_qrid_of_Errormessage=''

            if request_username=='None':
                request_username_of_Errormessage = " 參數裡沒有 username"
                

            if request_qrid=='None':
                request_qrid_of_Errormessage = " 參數裡沒有 qrid"

            if request_username=='None' or request_qrid=='None':

                logger.error('API Server參數錯誤 %s',f"{Errormessage}{request_username_of_Errormessage}{request_qrid_of_Errormessage}")

                return JsonResponse({'message':f"API Server參數錯誤 {Errormessage}{request_username_of_Errormessage}{request_qrid_of_Errormessage}"}, safe=False)
                        
            
                
            #Step 3 檢查使用者有沒有註冊
            if not User.objects.filter(username=request_username).exists():
                responseData = {'message':'error',
                                      'error_message':'使用者='+request_username+' 未註冊'  }
                return JsonResponse({'message':responseData}
                                      ,json_dumps_params={'ensure_ascii': False}
                                      , safe=False) 
            #Step 4 檢查資料庫有沒有這個裝置
              
            if request_qrid is not None:
                if not DeviceTransfor.objects.filter(QRid=request_qrid).exists(): 
                    responseData = {'message':'error',
                                    'error_message':'資料庫沒有'+request_qrid+'這個QrID'  }
                    return JsonResponse({'message':responseData}
                                        ,json_dumps_params={'ensure_ascii': False}
                                        , safe=False) 
                else:
                    
                    request_deviceUuid = DeviceTransfor.objects.filter(QRid=request_qrid)
                    request_deviceUuid = request_deviceUuid.values()
                    request_deviceUuid = request_deviceUuid[0].get('deviceUuid')
                    

            #Step 5 檢查這個裝置ID有沒有被綁定
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

            users = self.get_queryset()
            serializer = self.serializer_class(users, many=True)        
            data = serializer.data

            #Step 6 如果都有必要參數(deviceUuid、和 username)就執行綁定的動作
            if request_deviceUuid!="None" and request_username!="None":

                Device.objects.create(  user= User.objects.filter(username=request_username).first(),
                                        deviceUuid=request_deviceUuid, 
                                    ) 
                            
                responsedata = {'message':'ok',
                                'error_message': ''}
                return JsonResponse({'message':responsedata}, 
                                    json_dumps_params={'ensure_ascii': False},
                                    safe=False)
        else: 
            #如果沒給參數 return error
            userrequestkey=['']
            for k in request.GET:
                userrequestkey = userrequestkey.append(k)
            logger.warning('使用者參數 %s',userrequestkey)
            return JsonResponse({'message':'錯誤的參數, api/register_device/?username=&deviceUuid='}, 
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

class DeviceUnbind(APIView):

    '''
    =======================================================================================================
                
                                    裝置解綁
        功能: 解除裝置ID與使用者的綁定關係，傳入的必要參數是使用者名稱、QRID
        效果: 一個使用者可解除多個屬於他的裝置ID

        Step 1 : 取得參數(username，qrid)
        Step 2 : 使用qrid 取得裝置ID(deviceUuid )
        Step 3 : 確認使用者是否註冊 
                (1) 未註冊 ---> return  {'message':'error','error_message':'使用者xxx未註冊'  }
        Step 4 : 使用 使用者名稱 和 裝置ID 取得資料庫的 ID  
        Step 5 : 刪除在資料庫的id   
    =======================================================================================================

    '''
    def get(self, request, *args, **krgs):

        # Step 1 : 取得參數(username，qrid，deviceUuid )
        request_username = request.GET.get('username','None')
        request_qrid = request.GET.get('qrid','None')

        # Step 2 : 使用qrid 取得裝置ID
        request_deviceUuid = qrid_to_deviceuuid(request_qrid)

        # Step 3 : 確認使用者是否註冊
        if not User.objects.filter(username=request_username).exists():
            responseData = {'message':'error',
                            'error_message':f'使用者= {request_username} 未註冊'  }
            return JsonResponse({'message':responseData}
                                    ,json_dumps_params={'ensure_ascii': False}
                                    , safe=False) 
        # Step 4 : 使用 使用者名稱 和 裝置ID 取得資料庫的 ID
        delete_id = Device.objects.filter( user=User.objects.filter(username=request_username).first(),
                                        deviceUuid=request_deviceUuid)
        # Step 5 : 刪除這個ID
        if delete_id.exists():
            delete_id.delete()
 
            responseData = {'message':'ok',
                            'error_message': '' }
            return JsonResponse({'message':responseData}
                                    ,json_dumps_params={'ensure_ascii': False}
                                    , safe=False)         
            

        else:
            responseData = {'message':'error',
                    'error_message': '使用者未綁定任何裝置ID或這個裝置ID未被綁定' }

            return JsonResponse({'message':responseData}
                                    ,json_dumps_params={'ensure_ascii': False}
                                    , safe=False)         



class DeviceranforListCreate(generics.ListCreateAPIView):
    queryset = DeviceTransfor.objects.all()
    serializer_class = DeviceTransforSerializer
    def post(self, request,*args, **krgs):
        request_deviceUuid = request.GET.get('deviceUuid',"None")
        request_qrid= request.GET.get('qrid','None')

        
  
        if request_deviceUuid!="None" and request_qrid!="None":            
            DeviceTransfor.objects.create(deviceUuid=request_deviceUuid, 
                            QRid=request_qrid) 
                         
            responseData = "新增成功"    
        else:
            deviceUuid_of_responseData = ''
            qrid_of_responseData = ''
            value_of_responseData = ''
            if request_deviceUuid!="None":
              deviceUuid_of_responseData = "參數裡沒有 deviceUuid " 
            if request_qrid!="None":
              qrid_of_responseData = "參數裡沒有 qrid "
            responseData =  deviceUuid_of_responseData+\
                            qrid_of_responseData                 


        return JsonResponse({'message':responseData}, 
                                json_dumps_params={'ensure_ascii': False},
                                safe=False)  



class AMIListCreate(generics.ListCreateAPIView):
    queryset = AMI.objects.all()
    serializer_class = AMISerializer

    def get(self, request, *args, **krgs):
        print(request.method)
        logger.info('request.method= %s',request.method)
        if len(request.GET)>0:
                   
            request_username = request.GET.get('username','None')
            request_timestamp = request.GET.get('date','None')

            request_start_timestamp = request.GET.get('startdate','None')
            request_end_timestamp = request.GET.get('enddate','None')

            request_qrid = request.GET.get('qrid','None')

            logger.info('len(request.GET)>0')
            print(request_timestamp)
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
        if request_start_timestamp=='None' and request_end_timestamp=='None':

            Errormessage = "錯誤參數"
            request_username_of_Errormessage=''
            request_timestamp_of_Errormessage=''
            request_qrid_of_Errormessage=''

            if request_username=='None':
                request_username_of_Errormessage = " 參數裡沒有 username"
                

            if request_timestamp=='None':
                request_timestamp_of_Errormessage = " 參數裡沒有 date"

            if request_qrid=='None':
                request_qrid_of_Errormessage = " 參數裡沒有 qrid"


            if request_username=='None' or request_timestamp=='None'  or request_qrid=='None':

                logger.error('API Server參數錯誤 %s',Errormessage+request_username_of_Errormessage+request_timestamp_of_Errormessage)

                return JsonResponse({'message':'API Server參數錯誤'+Errormessage+request_username_of_Errormessage+request_timestamp_of_Errormessage+request_qrid_of_Errormessage}, safe=False)
            
            
            
            users = self.get_queryset()
            serializer = self.serializer_class(users, many=True)        
            data = serializer.data

            date_value = []

            for request_timestamp_string in request_timestamp.split(','):
                
                request_date = int(request_timestamp_string)
                print(request_timestamp_string)

                responseData = check_deviceuid(request_username,request_qrid)
                if responseData["errorcode"]:
                    return JsonResponse({'message':responseData}
                                        ,json_dumps_params={'ensure_ascii': False}
                                        , safe=False) 
                deviceUuid = qrid_to_deviceuuid(request_qrid)                        

                startdate = get_start_time_of_a_day(request_date)            
                print("開始時間>>",startdate)
                print("開始時間>>",type(startdate))

                startdate_value = get_Ami_Kwh_Data({'generatedTime':startdate,'deviceUuid':deviceUuid})
 

                if startdate==request_date:
                    enddate = request_date+86340000
                else:
                    enddate = request_date

                enddate_value = get_Ami_Kwh_Data({'generatedTime':enddate,'deviceUuid':deviceUuid})
                


                print(Check_date_in_databae(int(startdate)))
                if  enddate_value=='-1' and Check_date_in_databae(int(startdate)):
                    print('logic')
                    enddate_value, enddate= fill_data_logic(enddate,startdate,deviceUuid)

                print('startdate_value',startdate_value) 
                print('enddate_value',enddate_value)  
                if strfloatminus_and_convert_to_str(startdate_value, enddate_value)=="0":
                    date_value.append("0.0") 
                else:                                                                      
                    date_value.append(strfloatminus_and_convert_to_str(startdate_value, enddate_value))

                logger.info('API要求日期=%s, 裝置ID=%s,使用者=%s ,回傳 %s到%s 的用電量= %s'
                            ,unixtimestamp_to_datetime(request_date/1000)
                            ,deviceUuid
                            ,request_username
                            ,unixtimestamp_to_datetime(int(startdate)/1000)
                            ,unixtimestamp_to_datetime(int(enddate)/1000)
                            ,date_value)
            
            responseData = {"response Data":{"kwh":','.join(date_value)}}

            return JsonResponse({'message':responseData}, safe=False)  
        elif  request_start_timestamp!='None' and request_end_timestamp!='None':
            
            users = self.get_queryset()
            serializer = self.serializer_class(users, many=True)        
            data = serializer.data

            date_value = []
            
            request_start_timestamp = int(request_start_timestamp)
            

            responseData = check_deviceuid(request_username,request_qrid)
            if responseData["errorcode"]:
                return JsonResponse({'message':responseData}
                                    ,json_dumps_params={'ensure_ascii': False}
                                    , safe=False) 
            deviceUuid = qrid_to_deviceuuid(request_qrid)                        

            startdate = int(request_start_timestamp)
            print("開始時間>>",startdate)
            if Check_date_in_databae(startdate):
                startdate_value = get_Ami_Kwh_Data({'generatedTime':startdate,'deviceUuid':deviceUuid})
            else:
                startdate_value = "-1"
            print("開始時間的累積kwh>>",startdate_value)
            
            
            enddate = int(request_end_timestamp)       
            print("結束時間>>",enddate)
            if Check_date_in_databae(enddate):
                enddate_value = get_Ami_Kwh_Data({'generatedTime':enddate,'deviceUuid':deviceUuid})
            else: 
                enddate_value = "-1"

            print("結束時間的累積kwh>>",enddate_value)


 
            if strfloatminus_and_convert_to_str(startdate_value, enddate_value)=="0":
                date_value.append("0.0") 
            else:                                                                      
                date_value.append(strfloatminus_and_convert_to_str(startdate_value, enddate_value))

            responseData = {"response Data":{"kwh":f"{','.join(date_value)}","request_date":f"起始時間:{request_start_timestamp}, 結束時間:{request_end_timestamp}"}} 
            
            logger.info('裝置ID=%s,使用者=%s ,回傳 %s到%s 的用電量= %s'
                        ,deviceUuid
                        ,request_username
                        ,unixtimestamp_to_datetime(int(startdate)/1000)
                        ,unixtimestamp_to_datetime(int(enddate)/1000)
                        ,date_value)  

            return JsonResponse({'message':responseData},json_dumps_params={'ensure_ascii': False}, safe=False)
        else:

            responseData = {'message':'error',
            'error_message': '參數錯誤' }     
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

def Check_date_in_databae(checkedTime):
    
    return AMI.objects.aggregate(Max("generatedTime", default=0))['generatedTime__max']>checkedTime and  int(checkedTime/1000)< datetime_to_unixtimestamp(datetime.datetime.now(taiwan_timezone))
    
def get_Ami_Kwh_Data(dic):

    kwh = AMI.objects.filter(**dic)
    
    
    if kwh.exists():         
        kwh = kwh.values()
        kwh = kwh[0].get('value')
        
    else:    
        kwh = '-1'

    return kwh

def  WorkFlow_of_get_Ami_Kwh_Data(request_date):

    request_datetime = unixtimestamp_to_datetime(request_date/1000)
    now_datetime = datetime.datetime.today()
    # if request_datetime < now_datetime:


def fill_data_logic(enddate,startdate,deviceUuid):    
    while enddate > startdate:
        enddate = enddate-60000
        if get_Ami_Kwh_Data({'generatedTime':enddate,'deviceUuid':deviceUuid})!='-1':
            enddate_value = get_Ami_Kwh_Data({'generatedTime':enddate,'deviceUuid':deviceUuid})
            print(enddate)
            return enddate_value, enddate
    enddate_value = "-1"
    return enddate_value, enddate

def who_binding_the_device(deviceUuid):

    return  str( User.objects.get  (
                                    pk= Device.objects.filter
                                        (
                                            deviceUuid=deviceUuid
                                        ).values()[0].get('user_id')
                                )
            )

def qrid_to_deviceuuid(qrid):

    if qrid is not None:
        if not DeviceTransfor.objects.filter(QRid=qrid).exists(): 
            responseData = {'message':'error',
                            'error_message':'資料庫沒有'+qrid+'這個QrID'  }
            return JsonResponse({'message':responseData}
                                ,json_dumps_params={'ensure_ascii': False}
                                , safe=False) 
        else:
            deviceUuid = DeviceTransfor.objects.filter(QRid=qrid)
            deviceUuid = deviceUuid.values()
            deviceUuid = deviceUuid[0].get('deviceUuid')    
    return  deviceUuid   

def update_qrid_of_deviceUuid(request):
    old_qrid = request.GET.get('old_qrid','None')
    new_qrid = request.GET.get('new_qrid','None')
    updateid = request.GET.get('id','None')

    Erromessage='參數要有'

    if old_qrid=='None':
       Erromessage = Erromessage+'old_qrid'


    if new_qrid=='None':
       Erromessage = Erromessage+' new_qrid'


    if Erromessage!='參數要有':
        return JsonResponse({'message':Erromessage+'。'},
                            json_dumps_params={'ensure_ascii': False},
                            safe=False)


    if DeviceTransfor.objects.filter(QRid=old_qrid).exists():
        deviceUuid = DeviceTransfor.objects.get(QRid=old_qrid)
        deviceUuid.QRid = new_qrid

        deviceUuid.save()

        return JsonResponse({'message':'update' +old_qrid+' to '+new_qrid+' success'}
                                ,json_dumps_params={'ensure_ascii': False}
                                , safe=False)
    else:
        return JsonResponse({'message':'這個qrid不存在'}
                                ,json_dumps_params={'ensure_ascii': False}
                                , safe=False)


def delete_qrid(request):
    deleteid = request.GET.get('id','None')
    deviceUuid = DeviceTransfor.objects.get(pk=deleteid)
    deviceUuid.delete()
    return JsonResponse({'message':deleteid+'刪除成功'}
                            ,json_dumps_params={'ensure_ascii': False}
                            , safe=False)



def check_deviceuid(request_username,request_qrid):

    if not User.objects.filter(username=request_username).exists():
        responseData = {    'errorcode':1
                            ,'message':'error'
                            ,'error_message':f'使用者 {request_username} 未註冊'  }
        return responseData                    
 
    deviceUuid = qrid_to_deviceuuid(request_qrid)  

    if Device.objects.filter( user=User.objects.filter(username=request_username).first(),
                                deviceUuid=deviceUuid).exists():
        print(deviceUuid)
        responseData = {'errorcode':0}
        return responseData
                                

    else:
        responseData = {'errorcode':1
                        ,'message':'error'
                        ,'error_message': '使用者未綁定任何裝置ID或裝置ID未被綁定' }                
        return responseData
                                   