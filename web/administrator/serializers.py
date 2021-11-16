from rest_framework import serializers
from .models import *
from django.conf import settings

from django.contrib.auth.models import User
from django.contrib.auth import authenticate

#이 두개는 뭐지 특히 api_settings??
from django.contrib.auth.models import update_last_login
from rest_framework_jwt.settings import api_settings

# class CreateUserSerializer(serializers.ModelSerializer):
#     password1 = serializers.CharField(max_length=100, write_only=True)
#     password2 = serializers.CharField(max_length=100, write_only=True)
#     class Meta:
#         model = User
#         fields = ("username", "email", "password1", "password2")
#         # read_only_fields = ('password',)
            
#     def create(self, validated_data):
#         # instance.old_pw = validated_data.get('old_pw')
#         # instance.new_pw = validated_data.get('new_pw')
#         # instance.new_pw_re = validated_data.get('new_pw_re')
#         password1 = validated_data.pop('password1')
#         password2 = validated_data.pop('password2')

#         if password1 == password2:
#             user = User.objects.create(**validated_data)
#             user.set_password(password1)
#             user.save()
#             return user
#         else:
#             raise ValidationError("new password not match") #400

class RegisterSerializer(serializers.ModelSerializer):
    # password = serializers.CharField(max_length=100, write_only=True)
    class Meta:
        model = User
        write_only_fields = ('password',)
        fields = ('username', 'email',)

    def create(self, validated_data):
        new_user = User.objects.create(**validated_data)
        new_user.set_password(validated_data.get('password'))
        new_user.save()
        return new_user



# JWT 사용을 위한 설정
JWT_PAYLOAD_HANDLER = api_settings.JWT_PAYLOAD_HANDLER
JWT_ENCODE_HANDLER = api_settings.JWT_ENCODE_HANDLER

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=20)
    password = serializers.CharField(max_length=30, write_only=True)
    token = serializers.CharField(max_length=255, read_only=True)

    def validate(self, data):
        print("#########loginserializer####")
        username = data.get('username')
        password = data.get('password')

        user = authenticate(username=username, password=password)

        if user is None:
            return {'username': 'None'}
        
        else:
            # (user)(payload)왜 하는거지?
            payload = JWT_PAYLOAD_HANDLER(user)
            jwt_token = JWT_ENCODE_HANDLER(payload)
            # receiver which updates the last_login date for
            update_last_login(None, user)
            
        return {
            'username' :  user.username,
            'token' :  jwt_token
        }



class PostPointSerailizer(serializers.ModelSerializer):
    class Meta:
        model = Point
        fields = '__all__'


class StudentPointSerailizer(serializers.ModelSerializer):
    class Meta:
        model = Student
        fields = ('name','point')