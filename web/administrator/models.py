from django.db import models

# Create your models here.

class Student(models.Model):
    name = models.CharField(max_length=20, null=False)
    point =  models.IntegerField( null=True, blank=True)
    point_used = models.IntegerField( null=True, blank=True)

    def __str__(self): 
        return '[{}] {}'.format(self.id, self.name)
    

class Observe(models.Model):
    # STATUS = (
	# 	('X', '미확인'),
    #     ('O', '확인'),
    # )

    student = models.ForeignKey(Student, on_delete=models.CASCADE, null=False)
    # check = models.CharField(max_length=20, choices= STATUS)
    image = models.ImageField(upload_to = 'images/', blank=True, null=True )
    title = models.CharField(max_length=100, null=False)
    content = models.TextField(null=False)
    feedback = models.TextField(null=True, blank=True)
    receive_date = models.CharField(max_length=100, null=False)


    def __str__(self): 
        return '[{}] {}'.format(self.id, self.student)


class Item(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, null=True) #상품 소유자, 구매자
    name = models.CharField(max_length=20, null=False) #상품이름
    price = models.IntegerField( null=False ) #필요포인트

    def __str__(self): 
        return '[{}] {}'.format(self.id, self.name)


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


