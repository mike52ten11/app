from django.db import models
from django.contrib.auth.models import User

class AMI(models.Model):
    id = models.AutoField(auto_created=True, primary_key=True)
    deviceUuid = models.CharField(max_length=100) 
    generatedTime = models.BigIntegerField() 
    value = models.CharField(max_length=100)
    class meta:
        get_latest_by = 'id'
        db_table_comment  = 'ami'


class Device(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    deviceUuid = models.CharField(max_length=100)

class DeviceTransfor(models.Model):
    QRid = models.CharField(max_length=100)
    deviceUuid = models.CharField(max_length=100)
    class meta:
        get_latest_by = 'id'
        db_table_comment  = 'devicetransfor'
# class UserProfile(AbstractUser):
#     account  = models.CharField(max_length=150)
#     password = models.CharField(max_length=150)
#     deviceUuid = models.CharField(max_length=100) 
#     createtime = models.DateTimeField(auto_now_add=True,auto_now=False)
#     updatetime = models.DateTimeField(auto_now_add=False,auto_now=True)
#     def __str__(self) :
#         return self.account    
#     class meta:
#         get_latest_by = 'id'
#         db_table_comment  = 'userAccount'
