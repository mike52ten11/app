from rest_framework import serializers
from .models import AMI, Device,DeviceTransfor

class AMISerializer(serializers.ModelSerializer):

    class Meta:
        model = AMI
        fields = '__all__'

class DeviceSerializer(serializers.ModelSerializer):

    class Meta:
        model = Device
        fields = '__all__'   

class DeviceTransforSerializer(serializers.ModelSerializer):

    class Meta:
        model = DeviceTransfor
        fields = '__all__'          