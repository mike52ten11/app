from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User
from rest_framework import serializers

def login_user(username,password):
    user = authenticate(username=username,password=password)
    print(user)
    if user is not None:
        
        # token,created = Token.objects.get_or_create(user=user)
        if user.is_active:
            return {
                "success": True,
                "is_superuser": user.is_superuser,
                "message": "ok",
                "error_message":""
                # "token":token.key
                    }
        else:
            return {
                "success": False,
                "message": "error",
                "error_message": "此帳號已被禁用"
                    }
    else:
        return {
            "success": False,
            "message": "error",
            "error_message":"無此帳號或帳號密碼輸入錯誤"
                }
## 註冊

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'password')  # 選擇字段
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)  # 確保密碼是哈希過的
        return user

def register_user(data):
    print(data)
    serializer = UserSerializer(data=data)
    if serializer.is_valid():
        serializer.save()
        return {
            "success": True,
            "data": serializer.data,
            "message": "註冊成功"
        }
    else:
        return {
            "success": False,
            "errors": serializer.errors,
            "message": "註冊失敗"
        }                