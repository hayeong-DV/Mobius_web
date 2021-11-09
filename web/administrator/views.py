from django.shortcuts import render
from django.views.generic import(
    ListView, DetailView, TemplateView,
    CreateView, UpdateView, DeleteView
)
# from django.urls import reverse_lazy
# from django.conf import settings
from django.shortcuts import redirect
from administrator.models import *
import requests
import json
import base64
import datetime

from PIL import Image
from io import BytesIO
import matplotlib.pyplot as plt
from django.core.files.base import ContentFile
from django.db.models import Q



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


class ObserveLogView(ListView):
    #일지목록 [O]
    template_name = 'administrator/observation/student.html'
    model = Student

    def get(self, request, *args, **kwargs):
        self.object = self.get_queryset()
        self.object_list = self.object
        
        new_record = []
        #일단 학생수 만큼 cin가져오고 
        url = "http://203.253.128.161:7579/Mobius/AduFarm/record/la"

        #cin갯수에 따라 response데이터 받는거나중에 추가
        
        response = requests.request("GET", url, headers=get_headers)
        get_data = json.loads(response.text)
        record = get_data['m2m:cin']['con']
        # recor = get_data['m2m:cin']

        read_name = record['id']   
        #####물어볼거
        image = base64.b64decode(record['image'])
        #####
        title = record['title']
        text = record['intext']
        water = record['water']
        date = record['date']

        context = self.get_context_data()
       
       #나중에 받은 리스트만큼만 돌게 하기()
        for student in self.object:
            #각 학생마다 가진 관찰일지 우선 할당
            # context[student.name]= student.observe_set.all()
            
            #새로운 관찰일지 생성
            #같은 날짜가 있다면 생성 x
            #여기선 아니지만, create할 거 많다면 bulk create
            if student.name == read_name:
                if not student.observe_set.filter(receive_date = date).exists():
                    Observe.objects.create(
                        student = student,
                        image = ContentFile(
                            image,
                            student.name + str(datetime.datetime.now()).split(".")[0] + ".jpg"
                        ),
                        title = title,
                        content = text,
                        water = water,
                        receive_date = date
                    )
        return self.render_to_response(context)
        
    

class LogDetailView(DetailView):
    #일지세부(학생별) 
    template_name = 'administrator/observation/record.html'
    model = Student
 
    # def get_success_url(self):
    #     return reverse_lazy('administrator:log_detail', kwargs={"pk":self.kwargs['pk']})

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
        
        # print('############')
        # print(response.text)
        # print('############')
        return redirect('administrator:observation')


class PointView(ListView):
    #포인트 항목 [O]
    template_name = 'administrator/point/point_list.html'
    model = Point

    #항목 전송하는 버튼 필요
    def post(self, request, *args, **kwargs):
        point_list={}
        # 또 for.........
        for point_obj in self.get_queryset():
            point_list[point_obj.name] = {
                "action" : point_obj.action,
                "payment" : point_obj.payment,
                "num" : point_obj.number
            }
        send_content = str(point_list)

        url = "http://203.253.128.161:7579/Mobius/AduFarm/point_list"
        payload='{\n    \"m2m:cin\": {\n        \"con\": \"' + send_content  + '\"\n    }\n}'

        response = requests.request("POST", url, headers=post_headers, data=payload.encode('UTF-8'))

        return redirect('administrator:point_list')


def get_data(context):  
    for item in ['item1','item2','item3']:
        if Item.objects.filter(name=item, student__name ='teacher'):
            context[item] = Item.objects.filter(name= item, student__name ='teacher')
            context['{}_price'.format(item)] = context[item][0].price
        else:
            context['{}_save'.format(item)] = Item.objects.get(name='{}_save'.format(item))
            context['{}_price'.format(item)] = context['{}_save'.format(item)].price
        
    return context



class MarketView(ListView):
    #장터
    template_name = 'administrator/market/item_list.html'
    model = Item

    #학생들이 보낸 이름,포인트, 상품 받아와서 제일 높은 포인트 낸 학생 저장
    def get(self, request, *args, **kwargs):
        self.object_list = self.get_queryset()
        context = self.get_context_data()
        context = get_data(context)
        return self.render_to_response(context) 
    
    #장터 목록 개시
    def post(self, request, *args, **kwargs):
        url = "http://203.253.128.161:7579/Mobius/AduFarm/market_teacher"

        receive = self.request.POST['submit_btn']
        item_name_list = ['item1','item2','item3']

        if receive == '장터 개시':
        #일단 급하니 그냥 ㄱㄱㄱㄱ 나중에 정리 > 시리얼라이저로
            market_list= {}
            for item in item_name_list:
                market_list =  {
                    "id" : item,
                    "name" : Item.objects.filter(name=item).first().real_name,
                    "qty" : Item.objects.filter(name=item).count()
                }
                market_list = json.dumps(market_list)
                # payload='{\n    \"m2m:cin\": {\n        \"con\": ' + str(market_list)  + '\n    }\n}'
                # response = requests.request("POST", url, headers=post_headers, data= payload.encode('UTF-8'))

            #item가진사람 teacher아닌것들 삭제
            print('####')
            # Item.objects.filter(student__name = 'teacher').delete()
            

            return redirect('administrator:market')
        else:
            #장터 마감
            
            return redirect('administrator:purchase')
        

class PurchaseView(ListView):
    #상품구매현황_계산용 [O]
    template_name = 'administrator/purchase/check.html'
    model = Item
 
    def get(self, request, *args, **kwargs):
        #학생들 구매상품 우선순위 정렬, 보유 포인트 수정
        #아님 여기서 해아하나
        url = "http://203.253.128.161:7579/Mobius/AduFarm/auction?fu=2&lim=5&rcn=4"
      
        #정보 받아옴
        response = requests.request("GET", url, headers=get_headers)
        text = response.text
        json_data = json.loads(text)
        rsp = json_data["m2m:rsp"]
        cin = rsp["m2m:cin"]

        buy_dict={
            "item1":[],
            "item2":[],
            "item3":[]
        }

        for i in range(len(cin)): #cin 갯수 만큼 받아와서 딕셔너리에 추가
            # print(cin[i])
            con = cin[i]["con"]
            # user = Student.objects.get(name = con["user"])
            user = con["user"]
            point = con["point"]
            item = con["item"]
            buy_dict[item].append(
                (item, user, point)
            )

        # 일단 ㄱ
        sort_list = {}
        result = []
        for item in buy_dict:
            print('currnet_item1: ', item)
            sort_list[item] = sorted(buy_dict[item], key=lambda x:x[2], reverse=True)

            coupon = Item.objects.filter(name = item, student__name = 'teacher')
                
            if sort_list[item] != [] and len(sort_list[item]) > 1:
                print('currnet_item2: ', item)

                for i in range(len(sort_list[item])):
                    if (coupon.count() > 0) :
                        buy_item =  sort_list[item][i][0]
                        buy_user = sort_list[item][i][1]
                        use_point = sort_list[item][i][2]

                        update =coupon.first()
                        if update != None:
                            update.student = Student.objects.get(name = buy_user) 
                            update.save()
                            result.append({
                                "user" : update.student,
                                "item": update.name,
                                "name" : update.real_name,
                                "point" : use_point,
                            })
                            student = Student.objects.get(name = buy_user)
                            student.point -= int(use_point)
                            student.point_used += int(use_point)
                            student.save()

            elif sort_list[item] != []:
                buy_item =  sort_list[item][0][0]
                buy_user = sort_list[item][0][1]
                use_point = sort_list[item][0][2]

                update =coupon.first()
                if update != None:
                    print('obj:', update)
                    update.student = Student.objects.get(name = buy_user) 
                    update.save()
                    result.append({
                                "user" : update.student,
                                "item": update.name,
                                "name" : update.real_name,
                                "point" : use_point,
                            })
                    student = Student.objects.get(name = buy_user)
                    student.point -= int(use_point)
                    student.point_used += int(use_point)
                    student.save()

        #=--------------------------------post해야함
        #test
        # result =[
        #     {'user': Student.objects.get(name = 'studentA'), 'item': 'item1', 'name': '자동 물 주기', 'point': '1200'}, 
        #     {'user': Student.objects.get(name = 'studentB'), 'item': 'item3', 'name': '자동 무드등 작동', 'point': '2200'}, 
        #     {'user': Student.objects.get(name = 'studentA'), 'item': 'item3', 'name': '자동 무드등 작동', 'point': '2000'}, 
        # ]


        #아이템 구매내역 전체 결과 전송 - result
        #아이템 구매내역 유저별 상세 결과 전송
        url_access = "http://203.253.128.161:7579/Mobius/AduFarm/market_access"
        
        user_list =[]
        for i, result_list in enumerate(result):
            user = result_list['user']
            result[i]['user'] = user.name  

            if user.name not in user_list:
                user_list.append(user.name) 
                
                all_item = Item.objects.filter(student=user)
                user_item = {
                    "item1": str(False if all_item.filter(name='item1').first() == None else True),
                    "item2": str(False if all_item.filter(name='item2').first() == None else True),
                    "item3": str(False if all_item.filter(name='item3').first() == None else True)
                }
                user_item = json.dumps(user_item)
                print('------사용자별 아이템-------')
                print(user.name,'  ', user_item)
                url_user = "http://203.253.128.161:7579/Mobius/AduFarm/market_access/{}".format(user.name)
                payload_user='{\n    \"m2m:cin\": {\n        \"con\": ' + str(user_item)  + '\n    }\n}'
                response_user = requests.request("POST", url_user, headers=post_headers, data=payload_user.encode('UTF-8'))
                print(response_user.text)
                print('-------------------------------')
            

            result_list = json.dumps(result_list)
            print('------전체 아이템 구매내역------')
            print(result_list)
            payload_access='{\n    \"m2m:cin\": {\n        \"con\": ' + str(result_list)  + '\n    }\n}'
            response_access = requests.request("POST", url_access, headers=post_headers, data=payload_access.encode('UTF-8'))
            print(response_access.text)
            print('-------------------------------')
         
            #참고 형식
            # con : {
            #     “user”: “studentA”,
            #     “item”: “item3”,
            #     “name”: “자동환풍기 제어”
            #     “point”: 2000
            #     }
            
                # +유저별로 중첩cnt해서 거기에 
                # con : {
                #     “item1”:false,
                #     “item2:false,
                #     “item3”:false
                # }

        self.object_list = self.get_queryset()
        context = self.get_context_data()
        for item in ['item1','item2','item3']:
            if Item.objects.filter(name=item):
                context[item] = Item.objects.filter(name= item)
                context['{}_price'.format(item)] = context[item][0].price
                context['{}_count'.format(item)] = context[item].filter(student__name ='teacher').count()
                print( context['{}_count'.format(item)])
            else:
                context[item] = Item.objects.filter(name='{}_save'.format(item))
                context['{}_price'.format(item)] = context[item][0].price
                context['{}_count'.format(item)] = context[item].filter(student__name ='teacher').count()
        
        return self.render_to_response(context) 



class CheckPurchaseView(ListView):
    #상품구매현황_확인용 [O]
    template_name = 'administrator/purchase/check_view.html'
    model = Item

    def get(self, request, *args, **kwargs):
        self.object_list = self.get_queryset()

        context = self.get_context_data()
        for item in ['item1','item2','item3']:
            if Item.objects.filter(name = item):
                context[item] = Item.objects.filter(name= item)
                context['{}_price'.format(item)] = context[item][0].price
                context['{}_count'.format(item)] = context[item].filter(student__name ='teacher').count()
                print( context['{}_count'.format(item)])
            else:
                context[item] = Item.objects.filter(name='{}_save'.format(item))
                context['{}_price'.format(item)] = context[item][0].price
                context['{}_count'.format(item)] = 0
                
        return self.render_to_response(context) 





class RequirementView(ListView):
    #요구사항 페이지 [O]
    template_name = 'administrator/requirement/request.html'
    model = Requirements

class StudentLogView(ListView):
    #학생별 포인트 현황 목록 [O]
    template_name = 'administrator/student/point.html'
    model = Student

    def post(self, request, *args, **kwargs):
        receive = request.POST['submit_point']
        url = "http://203.253.128.161:7579/Mobius/AduFarm/havepoint"
            
        if receive == '학생별 포인트 내역 전송':
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



class ItemUpdateView(DetailView):
    #상품 관리 [O]
    template_name = 'administrator/item/item.html'
    model = Student
    fields=['name','price']

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
       
        context = self.get_context_data() 
        context = get_data(context)
        return self.render_to_response(context) 

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        update_list={}
        
        #새 포인트 가격 저장, 수량 만큼 객체 생성,삭제
        
        #post된 것들 가져오기
        for item in ['item1', 'item2','item3']:
            data = {
                'price' : self.request.POST.get('{}_price'.format(item), ''),
            }
            count = self.request.POST.get('{}_count'.format(item), '')
            
            
            if data['price'] != '':
                # price = data['price']
                Item.objects.filter(name= item).update(**data)
                Item.objects.filter(name= '{}_save'.format(item)).update(**data)
            
            if count != '':
                old = Item.objects.filter(name=item, student__name = 'teacher').count()
                new = int(count)

                print('old: ',old, 'new: ', new)

                if new > old or old == 0 :
                    for i in range(new - old):
                        Item.objects.create(
                            student = self.object,
                            name = item,
                            price = Item.objects.get(name='{}_save'.format(item)).price,
                            real_name = Item.objects.get(name='{}_save'.format(item)).real_name
                        )
                elif new < old:
                    for i in range(old - new):
                        last_obj = Item.objects.filter(name=item).last().delete()

                        
        return redirect('administrator:home')
                


        



