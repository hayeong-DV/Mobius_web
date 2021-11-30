from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm

from .models import *


class ResgisterForm(UserCreationForm):
    email = forms.EmailField(label = "email")
    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user


class StudentForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = '__all__'
        exclude = ('teacher',)


class ItemForm(forms.ModelForm):  
    class Meta:
        model = Item
        fields = (  'teacher',
                    'student',
                    'name',
                    'price',
                )
    
class PointForm(forms.ModelForm):
    class Meta:
        model = Point
        fields = '__all__'

# teacher = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True) #관리자
# student = models.ForeignKey(Student, on_delete=models.CASCADE, null=True, blank=True) #소유자, 구매자
# name = models.CharField(max_length=20, null=False) #상품이름
# real_name =  models.CharField(max_length=70, null=False) 
# price = models.IntegerField( null=False ) #필요포인트





