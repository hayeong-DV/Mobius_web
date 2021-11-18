from rest_framework import serializers
from .models import *
from django.conf import settings

from django.contrib.auth.models import User
from django.contrib.auth import authenticate

#이 두개는 뭐지 특히 api_settings??
from django.contrib.auth.models import update_last_login
from rest_framework_jwt.settings import api_settings
from rest_framework.fields import CurrentUserDefault

import jwt
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
        username = data.get('username', None)
        password = data.get('password', None)

        user = authenticate(username=username, password=password)

        if user is None:
            return {'username': 'None'}
        
        else:
            payload = JWT_PAYLOAD_HANDLER(user)
            jwt_token = JWT_ENCODE_HANDLER(payload)
            print('####jwt_token###',jwt_token)
            # receiver which updates the last_login date for
            update_last_login(None, user)
            
            return {
                'username' :  user.username,
                'token' :  jwt_token
            }


class StudentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        fields = ('id', 'name', 'email','phone')
        # fields = '__all__'
        # read_only_fields = ('id',)
    
    def create(self, validated_data):
        validated_data['teacher'] = self.context['teacher']
        return Student.objects.create(**validated_data)


class PointSerailizer(serializers.ModelSerializer):
    # number = serializers.IntegerField(source = 'get_number_display', required=True)

    class Meta:
        model = Point
        fields = '__all__'

    # def create(self, validated_data):
    #     validated_data['number'] = self.context['number']
    #     return Point.objects.create(**validated_data)

# student = models.ForeignKey(Student, on_delete=models.CASCADE, null=True, blank=True) #상품 소유자, 구매자
# name = models.CharField(max_length=20, null=False) #상품이름
# real_name =  models.CharField(max_length=100, null=False) 
# price = models.IntegerField( null=False ) #필요포인트

class ItemSerailizer(serializers.ModelSerializer):
    class Meta:
        model = Item
        write_only_fileds = ('student')

    def create(self, validated_data):
        pass


# class StudentPointSerailizer(serializers.ModelSerializer):
#     class Meta:
#         model = Student
#         fields = ('name','point')