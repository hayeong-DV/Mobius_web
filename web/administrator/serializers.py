from rest_framework import serializers
from .models import *
from django.contrib.auth.models import User

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

class CreateUserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(max_length=100, write_only=True)
    class Meta:
        model = User
        fields = ('username', 'email', 'password')

    def create(self, validated_data):
        print('#####')
        print(validated_data)
        new_user = User.objects.create(**validated_data)
        new_user.set_password(validated_data.get('password'))
        new_user.save()
        return new_user



class PostPointSerailizer(serializers.ModelSerializer):
    class Meta:
        model = Point
        fields = '__all__'


class StudentPointSerailizer(serializers.ModelSerializer):
    class Meta:
        model = Student
        fields = ('name','point')