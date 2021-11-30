from django.urls.base import reverse
from django.views.generic import(
    ListView, DetailView, TemplateView,
    CreateView, UpdateView, DeleteView
)
from django.contrib.auth import authenticate, login
# from django.shortcuts import render, render_to_response
from django.shortcuts import render
from rest_framework.fields import JSONField

from .forms import *
from .serializers import *

from rest_framework.views import APIView
from rest_framework import status
from rest_framework import permissions
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.urls import reverse_lazy

from django.http import JsonResponse
from django.shortcuts import redirect
from django.contrib import messages
from administrator.models import *
from datetime import date
import requests
import json
import base64
import datetime

from PIL import Image
from io import BytesIO
import matplotlib.pyplot as plt
from django.core.files.base import ContentFile
from django.db.models import Q
from django.http import HttpResponseRedirect


get_headers = {
    'Accept': 'application/json',
    'X-M2M-RI': '12345',
    'X-M2M-Origin': 'SOrigin'
}

post_headers = {
    'Accept': 'application/json',
    'X-M2M-RI': '12345',
    'X-M2M-Origin': '{{aei}}',
    'Content-Type': 'application/vnd.onem2m-res+json; ty=4'
}

# def get_con():
# def post_con():
# 끝나면 시리얼라이저 추가

# Create your views here.
class HomeView(TemplateView):
    #메인화면- (일지목록, 포인트 항목, 장터) [O]
    template_name = 'administrator/main/main.html'

#회원가입
class RegisterView(CreateView):
    permission_classes = (permissions.AllowAny,)

    template_name = 'administrator/account/register.html'
    form_class = ResgisterForm
    success_url = reverse_lazy('administrator:home')


class RegisterAPIView(APIView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request, *args, **kwargs):
        register_serializer = RegisterSerializer(data = self.request.data)

        if register_serializer.is_valid():
            register_serializer.save()
            return JsonResponse(register_serializer.data, status = status.HTTP_201_CREATED )
        else:
            return JsonResponse({'message': register_serializer.errors}, status = status.HTTP_400_BAD_REQUEST )


#로그인
class LoginAPIView(APIView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request, *args, **kwargs):
        serializers = LoginSerializer(data=request.data)
        print('####Post')

        if serializers.is_valid():
            return JsonResponse( serializers.data, status = status.HTTP_200_OK )
        else:
            JsonResponse({'message': serializers.errors}, status = status.HTTP_400_BAD_REQUEST )


class StudentListView(LoginRequiredMixin, ListView):
    login_url = 'login/'
    template_name = 'administrator/account/student_list.html'
    # model = Student

    def get_queryset(self):
        return Student.objects.filter(teacher = self.request.user)


class StudentAddView(LoginRequiredMixin, CreateView):
    login_url = 'login/'
    template_name = 'administrator/account/student_create.html'
    model = User
    form_class= StudentForm
    success_url =  reverse_lazy('administrator:student_list') 
    #방법 1
    # def get_form_kwargs(self):
    #     kwargs = super().get_form_kwargs()
    #     kwargs.update({
    #         "initial":{
    #             'teacher': self.request.user}
    #     })
    #     return kwargs
    # def post(self, request, *args, **kwargs):

    #방법2
    def form_valid(self, form):
        if Student.objects.filter(name = form.cleaned_data['name']):
            messages.error(self.request, '이미 입력된 학생입니다.', extra_tags='danger')
            return self.render_to_response(self.get_context_data(form=form))
        else:
            self.object = form.save(commit=False)
            self.object.teacher = self.request.user
            self.object.save()
            return super().form_valid(form)
           
            # 해결 전 create
            #     #얘하나 추가할려고....이래야하나..
            #     teacher = self.request.user, 
            #     name = form.cleaned_data['name'],
            #     email = form.cleaned_data['email'],
            #     phone = form.cleaned_data['phone']
            # )
            # return redirect('administrator:student_list')


class StudentDetailView(LoginRequiredMixin, DetailView):
    login_url = 'login/'
    template_name = 'administrator/account/student_detail.html'
    model = Student

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        if request.POST.get('method') == 'delete':
            self.object.delete()
            return redirect('administrator:student_list')
        else:
            form = StudentForm(request.POST, instance = self.object)
            if form.is_valid():
                form.save()
                return redirect('administrator:student_list')
            

class ObserveLogView(LoginRequiredMixin, ListView):
    #일지목록 [O]
    login_url = 'login/'
    template_name = 'administrator/observation/student.html'
    model = Student

    def get(self, request, *args, **kwargs):
        #학생 없을 경우도 추가
        self.object = self.get_queryset()
        self.object_list = self.object
  
        #일단 학생수 만큼 cin가져오고 
        # url = "http://203.253.128.161:7579/Mobius/AduFarm/record/la"
        url = "http://203.253.128.161:7579/Mobius/AduFarm/record?fu=2&lim={}&rcn=4".format(self.object.count())

        #cin갯수(학생 수)에 따라 response데이터 받기-일단 la로 하나만 - 대회후 인원수 만큼 가져오게...
        response = requests.request("GET", url, headers=get_headers)
        get_data = json.loads(response.text)
        # cin = get_data['m2m:cin']
        # record = cin['con']

        #여러개 가져올때
        record_list = {}
        cin = get_data["m2m:rsp"]['m2m:cin']
        for i in range(len(cin)): 
            record = cin[i]["con"]

            # print(read_date)> 2021년 11월 10일 수요일
            read_date = record['date']
            student = record["id"]
            print('name: ', student)
            student_obj = Student.objects.get(name = student)
            student_observe = Observe.objects.filter(student = student_obj, student__teacher = request.user)
            print(student_observe)
            #새로운 관찰일지 생성
            #같은 날짜가 이미 있다면 생성 x
            #여기선 아니지만, create할 거 많다면 bulk create
            if not student_observe.filter(receive_date = read_date).exists():
                record_list[student] = {
                    "student": student_obj,
                    "image" : ContentFile(
                                base64.b64decode(record['image']),
                                student + str(datetime.datetime.now()).split(".")[0] + ".jpg"
                            ),
                    "title" : record["title"],
                    "content" : record['intext'],
                    # "water" : record['water'], 안받아짐 갑자기 ㅜㅜ
                    "receive_date" : read_date,
                    "feedback": ''
                }   
                print('#####observe create')
                Observe.objects.create(**record_list[student])
        
        #받은 학생 리스트만큼만 돌아가며 일지 만들기
        # for name in record_list:
        #     print('list')
        #     print('/',name)
            # if not record_list[name]['student'].observe_set.filter(receive_date = read_date).exists():
        
        print('###')
        context = self.get_context_data()
        return self.render_to_response(context)





        
        # record_list = {}
        # record = cin["con"]
        # read_date = record['date']
        # user = record["id"]
    
        # record_list[user] = {
        #     "student": self.object.get(name = user),
        #     "image" : ContentFile(
        #                 base64.b64decode(record['image']),
        #                 user + str(datetime.datetime.now()).split(".")[0] + ".jpg"
        #             ),
        #     "title" : record["title"],
        #     "content" : record['intext'],
        #     "water" : record['water'],
        #     "receive_date" : read_date,
        #     "feedback": ''
        # }
        # #받은 학생 리스트만큼만 돌아가며 일지 만들기
        # # for student in self.object:
        # for name in record_list:
        #     #새로운 관찰일지 생성
        #     #같은 날짜가 이미 있다면 생성 x
        #     #여기선 아니지만, create할 거 많다면 bulk create
        #     if not record_list[name]['student'].observe_set.filter(receive_date = read_date).exists():
        #         Observe.objects.create(**record_list[name])

        # context = self.get_context_data()
        # return self.render_to_response(context)
        
    

class LogDetailView(LoginRequiredMixin, DetailView):
    #일지세부(학생별) 
    login_url = 'login/'
    template_name = 'administrator/observation/record.html'
    model = Student
 
    def get(self, request, *args, **kwargs):
        #pk로 특정 학생 로드
        self.object = self.get_object()
        context = self.get_context_data() 
        
        context['observe'] = Observe.objects.filter(
            student =  self.object
            )
        return self.render_to_response(context)


    def post(self, request, *args, **kwargs):
        #피드백 (저장,전송) 확인상태 변경
        self.object = self.get_object()
        
        feedback = request.POST['feedback']
        log_id = request.POST['observe__id']

        obj = self.object.observe_set.get(id = log_id)
        obj.feedback = feedback
        obj.save()
        

        #관찰일지 피드백 후 포인트 부여
        #물 줬으면 포인트 부여
        if obj.water == 1:
            self.object.point +=100
        
        #관찰일지 있다는 가정이니 포인트 부여
        self.object.point += 500
        self.object.save()

        #피드백 보내기
        url = "http://203.253.128.161:7579/Mobius/AduFarm/feedback"

        payload='{\n    \"m2m:cin\": {\n        \"con\": \"' + obj.feedback  + '\"\n    }\n}'
        response = requests.request("POST", url, headers=post_headers, data=payload.encode('UTF-8'))
        
        print('############')
        print(response.text)
        print('############')
        return redirect('administrator:observation')


class PointView(LoginRequiredMixin, ListView):
    #포인트 항목 [O]
    login_url = 'login/'
    template_name = 'administrator/point/point_list.html'
    model = Point

    #항목 전송하는 버튼
    def post(self, request, *args, **kwargs):
        if request.POST['submit'] == 'Submit point list':
            point_list={}
        
            for point_obj in self.get_queryset():
                point_list[point_obj.action] = {
                    "payment" : point_obj.payment,
                    "num" : point_obj.number
                }
            send_content = str(point_list)

            url = "http://203.253.128.161:7579/Mobius/AduFarm/point_list"
            payload='{\n    \"m2m:cin\": {\n        \"con\": \"' + send_content  + '\"\n    }\n}'

            response = requests.request("POST", url, headers=post_headers, data=payload.encode('UTF-8'))
            print(response.text)
            return redirect('administrator:point_list')
    

class CreatePointView(LoginRequiredMixin, CreateView):
    login_url = 'login/'
    template_name = 'administrator/point/create_point_list.html'
    model = Point
    form_class = PointForm
    success_url =  reverse_lazy('administrator:point_list') 

    # def get_form_kwargs(self):
    #     kwargs = super().get_form_kwargs()
    #     kwargs.update({
    #         "initial":{'teacher': self.request.user}
    #     })
    #     return kwargs

    def form_valid(self, form):
        if Point.objects.filter(action = form.cleaned_data['action']):
            messages.error(self.request, '이미 입력된 포인트 항목입니다.', extra_tags='danger')
            return self.render_to_response(self.get_context_data(form=form))
        else:
            self.object = form.save(commit=False)
            self.object.teacher = self.request.user
            self.object.save()
            return super().form_valid(form)

        

# teacher,action, payment, number

  
def check_item_type(self, check_student):
    if check_student == 'check':
        teacher_items = Item.objects.filter(teacher = self.request.user, student=None)
    else:
        teacher_items = Item.objects.filter(teacher = self.request.user)
    items = teacher_items.values_list('name', flat = True)

    #아이템 종류 리스트
    item_type_list = items.distinct()
    item_list = {}

    for item in item_type_list:
        filter_item = teacher_items.filter(name = item)
        item_list[item] = filter_item, filter_item.count()
    return item_list



class MarketView(LoginRequiredMixin, ListView):
    #장터
    login_url = 'login/'
    template_name = 'administrator/market/item_list.html'
    model = Item

    #학생들이 보낸 이름,포인트, 상품 받아와서 제일 높은 포인트 낸 학생 저장-여기서 말고
    def get(self, request, *args, **kwargs):
        self.object_list = self.get_queryset()
        context = self.get_context_data()

        item_list = check_item_type(self, 'check')  
        # context['item_list'] = item_list
        #      
        get_result={}
        for item in item_list:
            get_result[item] = {
                "price" : item_list[item][0][0].price, 
                "count" : item_list[item][1]
            }
        context['item_list'] = get_result
        return self.render_to_response(context) 
    
    #장터 목록 개시
    def post(self, request, *args, **kwargs):
        url = "http://203.253.128.161:7579/Mobius/AduFarm/market_teacher"

        receive = self.request.POST['submit_btn']
        item_list = check_item_type(self, 'check')

        if receive == 'market open':
            market_list= {}
            for item, item_value in item_list.items():
                market_list = {
                    "id" : item,
                    "name" : item,
                    "qty" : item_value[1]
                }
                market_list = json.dumps(market_list)
                payload='{\n    \"m2m:cin\": {\n        \"con\": ' + str(market_list)  + '\n    }\n}'
                response = requests.request("POST", url, headers=post_headers, data= payload.encode('UTF-8'))

            Item.objects.filter(teacher = request.user).exclude(student = None).delete()
            return redirect('administrator:market')
        else:
            #장터 마감
            
            return redirect('administrator:purchase')
        

class PurchaseView(LoginRequiredMixin, ListView):
    #상품구매현황_계산용 [O]
    login_url = 'login/'
    template_name = 'administrator/purchase/check.html'
    model = Item
 
    def get(self, request, *args, **kwargs):
        #학생들 구매상품 우선순위 정렬, 보유 포인트 수정
        #아님 여기서 해아하나
        url = "http://203.253.128.161:7579/Mobius/AduFarm/auction?fu=2&lim=3&rcn=4"
      
        #정보 받아옴
        response = requests.request("GET", url, headers=get_headers)
        text = response.text
        json_data = json.loads(text)
        rsp = json_data["m2m:rsp"]
        cin = rsp["m2m:cin"]

        buy_dict={}
        for i in range(len(cin)): #cin 갯수 만큼 받아와서 딕셔너리에 추가
            con = cin[i]["con"]
            date = con["date"]

            if date == str(datetime.date.today()):
                user = con["user"]
                point = con["point"]
                item = con["item"]

                if item not in buy_dict:
                    buy_dict[item] = []
                
                buy_dict[item].append(
                    (user, point)
                )

        # 일단 ㄱ
        sort_list = {}
        coupon = {}
        result1 = []
        result2 = {}

        # for문 지옥.......
        for item in buy_dict:
            sort_list[item] = sorted(buy_dict[item], key=lambda x:x[1], reverse=True)
            coupon[item] = Item.objects.filter(name = item, teacher = self.request.user, student = None)
            
            if coupon[item].first():
                for num in range(len(sort_list[item])):
                    buy_user, use_point = sort_list[item][num]
                    update_item = coupon[item].first()

                    update_item.student = student = Student.objects.get(name = buy_user) 
                    update_item.save()
                    student.point -= int(use_point)
                    student.point_used += int(use_point)
                    student.save()

                    #전체 결과
                    result1.append({
                                "user" : update_item.student.name,
                                "item": update_item.name,
                                "point" : use_point,
                            })  

        #사용자별 결과
        item_list = check_item_type(self, None)
        # print(item_type.keys())

        for student in Student.objects.all():
            result2[student.name] = {}
            for item in item_list.keys():
                result2[student.name][item] = str(False if Item.objects.filter(
                                    name = item, 
                                    teacher = self.request.user, 
                                    student = student).first() == None else True)
            user_item = json.dumps(result2)
            print('#사용자별 아이템#')
            url_user = "http://203.253.128.161:7579/Mobius/AduFarm/user_control/{}".format(student.name)
            payload_user='{\n    \"m2m:cin\": {\n        \"con\": ' + str(user_item)  + '\n    }\n}'
            response_user = requests.request("POST", url_user, headers=post_headers, data=payload_user.encode('UTF-8'))
            print(response_user.text)

        result_list = json.dumps(result1)
        #아이템 구매내역 전체 결과 전송 - result
        #아이템 구매내역 유저별 상세 결과 전송
        url_access = "http://203.253.128.161:7579/Mobius/AduFarm/user_control"

        print('#전체 아이템 구매내역#')
        url_market_access = "http://203.253.128.161:7579/Mobius/AduFarm/market_access"
        payload_access='{\n    \"m2m:cin\": {\n        \"con\": ' + str(result_list)  + '\n    }\n}'
        response_access = requests.request("POST", url_market_access, headers=post_headers, data=payload_access.encode('UTF-8'))
        print(response_access.text)

      
        self.object_list = self.get_queryset()
        context = self.get_context_data()

        get_result={}
        for item in item_list:
            get_result[item] = {
                "item" : item_list[item][0],
                "price" : item_list[item][0][0].price, 
                "count" : item_list[item][1],
            #   "slug_name" : item_list[item][0][0].slug
            }
        # print(get_result)
        context['item_list'] = get_result
        return self.render_to_response(context) 



class CheckPurchaseView(ListView):
    #상품구매현황_확인용 [O]
    login_url = 'login/'
    template_name = 'administrator/purchase/check_view.html'
    model = Item

    def get(self, request, *args, **kwargs):
        self.object_list = self.get_queryset()

        context = self.get_context_data()
        item_list = check_item_type(self, None)
    
        get_result={}
        for item in item_list:
            get_result[item] = {
                "item" : item_list[item][0],
                "price" : item_list[item][0][0].price, 
                "count" : item_list[item][1],
            #   "slug_name" : item_list[item][0][0].slug
            }
        # print(get_result)
        context['item_list'] = get_result
        return self.render_to_response(context) 





class RequirementView(LoginRequiredMixin, ListView):
    #요구사항 페이지 [O]
    login_url = 'login/'
    template_name = 'administrator/requirement/request.html'
    model = Requirements


class StudentLogView(LoginRequiredMixin, ListView):
    #학생별 포인트 현황 목록 [O]
    login_url = 'login/'
    template_name = 'administrator/student/point.html'
    model = Student

    def post(self, request, *args, **kwargs):
        print('###########')
        receive = request.POST['submit_point']
        print(receive)

        url = "http://203.253.128.161:7579/Mobius/AduFarm/havepoint"
            
        if receive == "Submit student's point":
            students_set = self.get_queryset().exclude(name = 'teacher')
            # 형식
            # name: "studentB"    
            # hp: "3000"

            for student in students_set:
                send_hp = {
                    "name" : student.name,
                    "hp" : student.point
                }
                print(send_hp)
                send_hp = json.dumps(send_hp)

                payload='{\n    \"m2m:cin\": {\n        \"con\": ' + str(send_hp)  + '\n    }\n}'
                response_access = requests.request("POST", url, headers=post_headers, data=payload.encode('UTF-8'))
                print(response_access.text)

        return redirect('administrator:student-log')
  
  
class ItemManageView(LoginRequiredMixin, DetailView):
    #상품 관리 [O]
    login_url = 'login/'
    model = User
    fields=['name','price']

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        item_list = check_item_type(self, 'check')

        context = self.get_context_data() 
       
        get_result={}
        for item in item_list:
            get_result[item] = {
              "price" : item_list[item][0][0].price, 
              "count" : item_list[item][1],
              "slug_name" : item_list[item][0][0].slug
            }
        # print(get_result)
        context['item_list'] = get_result
        #?pk안보내도 되네?????/
        return render(request, 'administrator/item/item_manage.html', context)


class ItemCreateView(LoginRequiredMixin, CreateView):
    #아이템 생성 []
    login_url = 'login/'

    model = User
    form_class = ItemForm
    template_name =  'administrator/item/item_create.html'
    
    def get_success_url(self):
        return reverse_lazy('administrator:item_manage', kwargs={'pk': self.kwargs['pk']})


    def form_valid(self, form):
        if not Item.objects.filter(name= form.cleaned_data['name'], teacher = self.request.user, student=None).exists():
        # 'WSGIRequest' object has no attribute 'data' 이거 뭐여 request.data치면 이럼     
        #     print(self.request.POST['quantity'])

            self.object = form.save(commit=False)
            self.object.teacher = self.request.user
            self.object.save()
 
            return super().form_valid(form)
        else:
            messages.error(self.request, '이미 존재하는 아이템입니다', extra_tags='danger')
            return self.render_to_response(self.get_context_data(form=form))


def update_item_count(self, items, count, price):
    print('####update_item_count###')
    print(self.object)
    if count > items.count():
        num = count - items.count()
        data = {
            'teacher' : self.request.user,
            'name' : self.object.name,
            'price' : self.object.price
        }
        result = [Item.objects.create(**data) for i in range(num)]   
    else:
        num = items.count() - count
        result = [items.last().delete() for i in range(num)]
    return items


class ItemUpdateView(LoginRequiredMixin, UpdateView):
    #아이템 수량, 포인트 가격 업데이트 
    login_url = 'login/'
    model = User
    form_class = ItemForm
    template_name =  'administrator/item/item_update.html'
    success_url = None

    def get_queryset(self):
        return Item.objects.filter(slug=self.kwargs['slug'])

    def get(self, request, *args, **kwargs):
        self.object = self.get_queryset().first()
        context = self.get_context_data()
        context['count'] = Item.objects.filter(teacher=request.user, name=self.object.name ).count()
        return self.render_to_response(context)
        
    def post(self, request, *args, **kwargs):
        self.object = self.get_queryset().first()
        items = Item.objects.filter(teacher = request.user, name = self.object.name)   

        if request.POST['button'] == 'update':
            price = request.POST.get('price', None)
            count = request.POST.get('count', None)
            print(price, count)
            if price and count:
                item = update_item_count(self, items, int(count), price)
                item.update(price = price)

            elif not price:
                item = update_item_count(self, items, int(count), price)
            elif not count:
                items.update(price=price)

        else:
            items = Item.objects.filter(teacher = request.user, name = self.object.name).delete()
        #위엔 문제 없는 듯
        #리턴하면  '__proxy__' object has no attribute 'get'  뜸  -reverse_lazy는 url 을 만들기만 할 뿐...이어서 에러뜬거였음
        return HttpResponseRedirect(reverse_lazy('administrator:item_manage', kwargs={'pk': self.kwargs['pk']}) )  



class ChartView(LoginRequiredMixin, ListView):     
    #차트연습
    login_url = 'login/'
    model = Item
    template_name =  'administrator/chart/chart_practice.html'

    # def get_queryset(self):
    #     return Item.objects.filter(teacher = self.request.user)

    def get(self, request, *args, **kwargs):
        self.object_list = self.get_queryset()
        context = self.get_context_data()

        items = Item.objects.filter(teacher = request.user).exclude(student=None)
        buy_list = {}
        for item in items:
            buy_list[item.name] = items.filter(name=item.name).count()
        
        context['item_list'] = buy_list
        return self.render_to_response(context)

        



#api_________________________________________________________________________________________________

class StudentListAPIView(APIView):
    #관리자별 학생리스트
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        print('##get')
        queryset = request.user.student_set.all()
        student_list = StudentSerializer(queryset, many = True)
        return JsonResponse(student_list.data, status = status.HTTP_200_OK, safe=False)
       
    def post(self, request, format=None):
        # print('##post')
        add_serializer = StudentSerializer(data = request.data, context={'teacher':request.user})
        if add_serializer.is_valid():
            add_serializer.save()
            return JsonResponse(add_serializer.data, status = status.HTTP_201_CREATED, safe=False)
        return JsonResponse({'message': 'create error'}, status = status.HTTP_400_BAD_REQUEST)


class StudentDetailAPIView(APIView):
    #관리자별 학생 수정
    permission_classes = [IsAuthenticated]

    def get_object(self, pk):
        try:
            return Student.objects.get(pk=pk)
        except:
            return {'message': 'no pk'}

    def get(self, request, pk, format = None):
        # print('####get')
        obj= self.get_object(pk)
        get_students = StudentSerializer(obj)
        return JsonResponse(get_students.data, status = status.HTTP_200_OK)

    def put(self, request, pk, format = None):
        # print('####put')
        obj= self.get_object(pk)
        put_serial = StudentSerializer(obj, request.data)
        if put_serial.is_valid():
            put_serial.save()
            return JsonResponse(put_serial.data, status = status.HTTP_200_OK)
        return JsonResponse(put_serial.errors, status = status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, format = None):
        obj= self.get_object(pk)
        obj.delete()
        return JsonResponse({'message':'success delete'}, status = status.HTTP_204_NO_CONTENT)


class PointAPIView(APIView):
    #포인트 항목 API
    permission_classes = [IsAuthenticated]
    queryset = Point.objects.all()

    def post(self, request, format = None):
        point_serial = PointSerailizer(request.data)
        if point_serial.is_valid():
            point_serial.save()
            return JsonResponse(point_serial.data, status = status.HTTP_201_CREATED)
        else:
            return JsonResponse(point_serial.errors, status = status.HTTP_400_BAD_REQUEST)
    
    def get(self, format = None):
        queryset = Point.objects.all()
        print(queryset)
        #queryset은 dict가 아니라서 safe=False필요 
        #safe> 변환할 데이터가 dict인지 확인하는거
        
        send_content = PointSerailizer(queryset, many=True)
        return JsonResponse(send_content.data, status = status.HTTP_200_OK, safe=False)



class ItemManageAPIView(APIView):
    #관리 api
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        items = Item.objects.filter(teacher__pk = self.kwargs['pk'], student=None)
        item_serializer = ItemSerailizer(items, many=True)
        item_list = check_item_type(self, 'check')
        # print(item_list.items())

        get_result={}
        for item in item_list:
            get_result[item] = {
              "price" : item_list[item][0][0].price, 
              "count" : item_list[item][1]
            }
            
        get_result['detail'] = list(item_serializer.data)
        return JsonResponse(get_result, status = status.HTTP_200_OK, safe=False)

    def post(self, request, *args, **kwargs):
        teacher = User.objects.get(id = self.kwargs['pk'])
        create_items = ItemSerailizer(data = request.data, context={'teacher': teacher})

        if create_items.is_valid():
            create_items.save()
            return JsonResponse(create_items.data, status = status.HTTP_201_CREATED, safe=False)
        return JsonResponse({'message': 'create error'}, status = status.HTTP_400_BAD_REQUEST)


class ItemUpdateAPIView(APIView):
    permission_classes = [IsAuthenticated]

    # def get_object(self, item_pk):
    #     try:
    #         return Item.objects.get(pk = item_pk)
    #     except:
    #         return {'message': 'no pk'}

    def get_queryset(self):
        return Item.objects.filter(slug=self.kwargs['slug'])

    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        self.object = queryset.first()
        result = {
            "name": self.object.name,
            "price": self.object.price,
            "count":queryset.count()
        }
        return JsonResponse(result, status = status.HTTP_200_OK) 

    def put(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        self.object = queryset.first()

        price = request.POST.get('price', None)
        count = request.POST.get('count', None)
    
        if price and count:
            item = update_item_count(self, queryset, int(count), price)
            item.update(price = price)

        elif not price:
            item = update_item_count(self, queryset, int(count), price)

        elif not count:
            queryset.update(price=price)

        # print(items)
        update_result = {
            'name' : self.object.name,
            'count' : queryset.count(),
            'price' :  self.object.price
        }
        return JsonResponse(update_result, status = status.HTTP_200_OK)

    def delete(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        self.object = queryset.first()
        Item.objects.filter(name=self.object.name).delete()
        return JsonResponse({'message': '[{}] 삭제 완료'.format(self.object.name)}, status = status.HTTP_200_OK)


    
class StudentLogAPIView(APIView):
    #학생별 포인트 현황 목록 API
    permission_classes = [IsAuthenticated]
    def post(self, request, *args, **kwargs):
        students =Student.objects.filter(teacher =  request.user)
        send_content = StudentPointSerailizer(students, many=True)
        return JsonResponse(send_content.data, status = status.HTTP_200_OK, safe=False)


class ObserveLogAPIView(APIView):
    #관찰일지 목록 API
    permission_classes = [IsAuthenticated]
    def get(self, request, *args, **kwargs):
        students =Student.objects.filter(teacher = request.user)
    
        url = "http://203.253.128.161:7579/Mobius/AduFarm/record?fu=2&lim={}&rcn=4".format(students.count())
        response = requests.request("GET", url, headers=get_headers)
        get_data = json.loads(response.text)

        record_list = {}
        result_list = []
        cin = get_data["m2m:rsp"]['m2m:cin']
        for i in range(len(cin)): 
            record = cin[i]["con"]
            # print(read_date)> 2021년 11월 10일 수요일
            read_date = record['date']
            student = record["id"]
            print(read_date, student)

            student_obj = Student.objects.get(name = student)
            student_observe = Observe.objects.filter(student = student_obj, student__teacher = request.user)
            
            #새로운 관찰일지 생성
            #같은 날짜가 이미 있다면 생성 x
            if not student_observe.filter(receive_date = read_date).exists():
                print('###create')
                record_list[student] = {
                    "student": student_obj.pk,
                    "image" : ContentFile(
                                base64.b64decode(record['image']),
                                student + str(datetime.datetime.now()).split(".")[0] + ".jpg"
                            ),
                    "title" : record["title"],
                    "content" : record['intext'],
                    "water" : record['water'], 
                    "receive_date" : read_date,
                    "feedback": ''
                }   
            #여기선 아니지만, create할 거 많다면 bulk create
            # Observe.objects.create(**record_list[name])
                create_observe = ObserveSerializer(data=record_list[student])
                if create_observe.is_valid():
                    print('####valid')
                    create_observe.save()
                    result_list.append(create_observe.data)
                else:
                    print(create_observe.errors)

            else:
                print('no create')
                read_observe = Observe.objects.filter(student =student_obj)
                get_observe = ObserveSerializer(read_observe, many=True)
                result_list.append(get_observe.data)

        return JsonResponse(result_list, status = status.HTTP_200_OK, safe = False)

       
class LogDetailAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        student = Student.objects.get(id = self.kwargs['pk'])
        logs = Observe.objects.filter(student__pk = self.kwargs['pk'])
        print(logs)
        log_detail = ObserveSerializer(logs, many=True)
        return JsonResponse(log_detail.data, status = status.HTTP_200_OK, safe = False)

    def put(self, request, *args, **kwargs):
        read_feedback = request.POST.get('feedback', None)
        log_id = request.POST.get('log_id', None)

        student  = Student.objects.get(id = self.kwargs['pk'])
        log = Observe.objects.get(pk = log_id)
        print(log.__dict__)
        update_log = ObserveSerializer(log, data={'feedback': read_feedback}, partial=True)
        # update_log = ObserveSerializer.save(feedback = read_feedback)
        # log.update(feedback = read_feedback)
        if update_log.is_valid():
        # if read_feedback != None:
            print('###')
            update_log.save()

            if log.water == '1':
                #나중에 포인트 부분 수정
                student.point += 600
                student.save()
            else:
                student.point += 500
                student.save()

            return JsonResponse(update_log.data, status = status.HTTP_200_OK)
        else:
            print('###!!')
            print(update_log.errors)
            get_log = ObserveSerializer(log)
            return JsonResponse(get_log.data, status = status.HTTP_200_OK)


class MarketAPIView(APIView):
    permission_classes = [IsAuthenticated]
    #장터목록개시
    def post(self, format=None):
        item_list = check_item_type(self, 'check')
        get_result={}
        for item in item_list:
            get_result[item] = {
                "price" : item_list[item][0].first().price, 
                "count" : item_list[item][1]
            }
        return JsonResponse(get_result, status = status.HTTP_200_OK)

        
class PurchaseAPIView(APIView):
    permission_classes = [IsAuthenticated]
    #상품구매현황_계산용 []
    def get(self, format=None):
        url = "http://203.253.128.161:7579/Mobius/AduFarm/auction?fu=2&lim=3&rcn=4"
      
        #정보 받아옴
        response = requests.request("GET", url, headers=get_headers)
        text = response.text
        json_data = json.loads(text)
        rsp = json_data["m2m:rsp"]
        cin = rsp["m2m:cin"]

        buy_dict={}
        for i in range(len(cin)): #cin 갯수 만큼 받아와서 딕셔너리에 추가
            con = cin[i]["con"]
            date = con["date"]

            if date == str(datetime.date.today()):
                user = con["user"]
                point = con["point"]
                item = con["item"]

                if item not in buy_dict:
                    buy_dict[item] = []
                
                buy_dict[item].append(
                    (user, point)
                )

        # 일단 ㄱ
        sort_list = {}
        coupon = {}
        result1 = []
        result2 = {}

        # for문 지옥.......
        for item in buy_dict:
            sort_list[item] = sorted(buy_dict[item], key=lambda x:x[1], reverse=True)
            coupon[item] = Item.objects.filter(name = item, teacher = self.request.user, student = None)
            
            if coupon[item].first():
                for num in range(len(sort_list[item])):
                    buy_user, use_point = sort_list[item][num]
                    update_item = coupon[item].first()

                    print(buy_user)

                    update_item.student = student = Student.objects.get(name = buy_user) 
                    update_item.price = int(use_point)
                    update_item.save()
                    student.point -= int(use_point)
                    student.point_used += int(use_point)
                    student.save()

                    #전체 결과
                    result1.append({
                                "user" : update_item.student.name,
                                "item": update_item.name,
                                "point" : use_point,
                            })  
        #사용자별 결과
        item_list = check_item_type(self, None)
        # print(item_type.keys())

        for student in Student.objects.all():
            result2[student.name] = {}
            for item in item_list.keys():
                result2[student.name][item] = str(False if Item.objects.filter(
                                    name = item, 
                                    teacher = self.request.user, 
                                    student = student).first() == None else True)
        result = {
            "전체 결과" : result1,
            "개인 결괴" : result2
        }
        
        return JsonResponse(result, status = status.HTTP_200_OK)


class CheckPurchaseAPIView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, format=None):
        items = Item.objects.filter(teacher = self.request.user)
        item_list = check_item_type(self, None)
        get_result={}
        
        for item in item_list:
            print(item_list[item][0])
            get_result[item] = {
                "price" : list(map(lambda x: x.price if x.student else "", item_list[item][0])),
                "count" : item_list[item][1],
                "user" :  list(map(lambda x: x.student.name if x.student else "", item_list[item][0]))
            }
        print(get_result)
        return JsonResponse(get_result, status = status.HTTP_200_OK)

        






    #  def get(self, request, *args, **kwargs):
    #     self.object_list = self.get_queryset()

    #     context = self.get_context_data()
    #     item_list = check_item_type(self, None)
    
    #     get_result={}
    #     for item in item_list:
    #         get_result[item] = {
    #             "item" : item_list[item][0],
    #             "price" : item_list[item][0][0].price, 
    #             "count" : item_list[item][1],
    #         #   "slug_name" : item_list[item][0][0].slug
    #         }
    #     # print(get_result)
    #     context['item_list'] = get_result
    #     return self.render_to_response(context) 
            


        

      




