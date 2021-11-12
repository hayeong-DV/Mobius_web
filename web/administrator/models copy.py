from django.db import models
from django.contrib.auth.models import User
from django.db.models import Q
# Create your models here.

class Student(models.Model):
    name = models.CharField(max_length=20, null=False)
    point =  models.IntegerField( null=True, blank=True)
    point_used = models.IntegerField(default=0, blank=True, null=True)

    def __str__(self): 
        return '[{}] {}'.format(self.id, self.name)
    
    def check_feedback(self):
        return self.observe_set.filter(feedback="").exists()
        # return len(list(filter(lambda x: x == "" ,list(self.observe_set.all().values_list("feedback", flat=True))))) > 0
     


class Observe(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, null=False)
    # check = models.CharField(max_length=20, choices= STATUS)
    image = models.ImageField(upload_to = 'images/', blank=True, null=True )
    title = models.CharField(max_length=100, null=False)
    content = models.TextField(null=False)
    feedback = models.TextField(null=True, blank=True)
    water = models.IntegerField( null=True, blank=True)
    receive_date = models.CharField(max_length=100, null=False)


    def __str__(self): 
        return '[{}] {}'.format(self.id, self.student)

    


class Item(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, null=True) #상품 소유자, 구매자
    name = models.CharField(max_length=20, null=False) #상품이름
    real_name =  models.CharField(max_length=100, null=False) 
    price = models.IntegerField( null=False ) #필요포인트

    def __str__(self): 
        return '[{}] {}'.format(self.id, self.name)

    # def check_item_type(self):
    #     print('###')
    #     print(Item.objects.exclude(name__contains = 'save').values('name').distnct())

 

class Point(models.Model):
    name = models.CharField(max_length=20, null=False) # 포인트 지급 이름?
    action = models.CharField(max_length=100) #포인트 행동조건
    payment = models.IntegerField( null=False ) # 지급 포인트
    number= models.CharField(max_length=100) #포인트 지급 횟수

    def __str__(self): 
        return '[{}] {}'.format(self.id, self.name)


class Requirements(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, null=False)
    content = models.TextField(null=False)
    created_date = models.DateTimeField(auto_now_add=True)

    def __str__(self): 
        return '[{}] {}'.format(self.id, self.student.name)


