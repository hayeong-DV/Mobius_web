from django.db import models
from django.contrib.auth.models import User
from django.db.models import Q
from django.urls import reverse
from django.utils.text import slugify

# Create your models here.


class Student(models.Model):
    teacher = models.ForeignKey(User, on_delete=models.CASCADE, null=False)
    name = models.CharField(max_length=10, null=True)
    email = models.EmailField(max_length=100, null = True)
    phone = models.CharField(max_length=20, null=True)
    point =  models.IntegerField( default=0, null=True, blank=True)
    point_used = models.IntegerField(default=0, blank=True, null=True)

    def __str__(self): 
        return '[{}] {}'.format(self.id, self.name)

    # def set_teacher(self):
    #     self.objects.update(teacher = self.request.user)
    #     self.objects.save()
    
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

    
#선생님이 item들 가지고 있다가 student에게 나중에 주는거 하고싶은데
#그럼 어떻게 해야하지 - null을 그냥 선생님으로 나타내게 하여라! -근데 여기서 request.user어케하지 - 못함
class Item(models.Model):
    # blank=''면 선생님인걸로 - 근데 그럼 선생님마다 의 아이템이 안생기는거 아닌가???
    teacher = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True) #관리자
    student = models.ForeignKey(Student, on_delete=models.CASCADE, null=True, blank=True) #소유자, 구매자
    name = models.CharField(max_length=70, null=False) #상품이름
    # real_name =  models.CharField(max_length=70, null=False) 
    price = models.IntegerField( null=False ) #필요포인트
    slug = models.SlugField(allow_unicode=True)

    def __str__(self): 
        return '[{}] {}'.format(self.id, self.name)

    def save(self, *args, **kwargs):
        # allow_unicode에 True 값을 줘야 한국어로 작성을 할수있다
        self.slug = slugify(self.name, allow_unicode=True)
        super().save(*args, **kwargs)

    # def get_absolute_url(self):
    #     return reverse("administrator:item_update", kwargs={"slug": self.slug})
    



CHOICE = (
    ( '1', '1일 1회'),
    ( '2', '1일 2회'),
    ( '3', '1일 3회'),
)

class Point(models.Model):
    teacher = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True) #관리자
    action = models.CharField(max_length=100, null=False) #포인트 행동조건
    payment = models.IntegerField( null=False ) # 지급 포인트
    number= models.CharField(max_length=10, choices=CHOICE, null=False, default = '1' ) #지급 횟수 조건???
    slug = models.SlugField(allow_unicode=True, unique=True)

    def __str__(self): 
        return '[{}] {}'.format(self.id, self.action)

    def save(self, *args, **kwargs):
        # allow_unicode에 True 값을 줘야 한국어로 작성을 할수있다
        self.slug = slugify(self.action, allow_unicode=True)
        super().save(*args, **kwargs)


class Requirements(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, null=False)
    content = models.TextField(null=False)
    created_date = models.DateTimeField(auto_now_add=True)

    def __str__(self): 
        return '[{}] {}'.format(self.id, self.student.name)


