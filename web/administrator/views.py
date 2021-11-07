from django.shortcuts import render
from django.views.generic import(
    ListView, DetailView, TemplateView,
    CreateView, UpdateView, DeleteView
)
from django.urls import reverse_lazy
from django.shortcuts import get_object_or_404, redirect
from administrator.models import *
import requests
import json
import base64
from django.core.files.base import ContentFile
from PIL import Image
from io import BytesIO
import matplotlib.pyplot as plt

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
        
        #ㅅ학생수 만큼 cin가져오기
        url = "http://203.253.128.161:7579/Mobius/AduFarm/record/la"

        headers = {
        'Accept': 'application/json',
        'X-M2M-RI': '12345',
        'X-M2M-Origin': 'SOrigin'
        }

        #일지 올릴때 (record)cnt에 모든 애들이 다올리는거지? - O
        # (record)cnt하나만 쓴다 하면 이름,날짜도 같이 받아오기

        #cin갯수에 따라 response데이터 받는거나중에 추가
        
        response = requests.request("GET", url, headers=headers)
        get_data = json.loads(response.text)
        record = get_data['m2m:cin']['con']

        read_name = record['id']
        image = record['image']
        # print('###')
        # print(read_image)
        # # [B@52dd2d9
        # print('###')
        
        # image = base64.b64decode(read_image)
        # print('###')
        # image = BytesIO(image)
        # print(image)
        # # <_io.BytesIO object at 0x7fa96b446950
        # # print((image))
        # # cannot identify image file <_io.BytesIO object at 0x7fb148dc7ae0>
        # print('##1')

    
        title = record['title']
        text = record['intext']
        date = record['date']

        context = self.get_context_data()
       
       #나중에 받은 리스트만큼만 돌게 하기
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
                        image = image,
                        title = title,
                        content = text,
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
        
        read_name = self.object.name
        context['observe'] = Observe.objects.filter(
            student = Student.objects.get(name = read_name)
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

        headers = {
        'Accept': 'application/json',
        'X-M2M-RI': '12345',
        'X-M2M-Origin': '{{aei}}',
        'Content-Type': 'application/vnd.onem2m-res+json; ty=4'
        }

        # response = requests.request("POST", url, headers=headers, data=payload.encode('UTF-8'))
        
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
        headers = {
            'Accept': 'application/json',
            'X-M2M-RI': '12345',
            'X-M2M-Origin': '{{aei}}',
            'Content-Type': 'application/vnd.onem2m-res+json; ty=4'
            }

        response = requests.request("POST", url, headers=headers, data=payload.encode('UTF-8'))

        return redirect('administrator:point_list')


def get_data(context):
    context['item1'] = Item.objects.filter(name='item1')
    context['item2'] = Item.objects.filter(name='item2')
    context['item3'] = Item.objects.filter(name='item3')
    
    context['item1_price'] = context['item1'][0].price
    context['item2_price'] = context['item2'][0].price
    context['item3_price'] = context['item3'][0].price
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
        headers = {
            'Accept': 'application/json',
            'X-M2M-RI': '12345',
            'X-M2M-Origin': '{{aei}}',
            'Content-Type': 'application/vnd.onem2m-res+json; ty=4'
            }
        receive = self.request.POST['submit']
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
                payload='{\n    \"m2m:cin\": {\n        \"con\": ' + str(market_list)  + '\n    }\n}'
                response = requests.request("POST", url, headers=headers, data= payload.encode('UTF-8'))
                print('########')
                print(response.text)
            return redirect('administrator:market')
        else:
            #장터 마감
            return redirect('administrator:purchase')
        

class PurchaseView(ListView):
    #상품구매현황 [O]
    template_name = 'administrator/purchase/check.html'
    model = Item
 
    def get(self, request, *args, **kwargs):
        #학생들 구매상품 우선순위 정렬, 보유 포인트 수정
        #아님 여기서 해아하나
        url = "http://203.253.128.161:7579/Mobius/AduFarm/auction?fu=2&lim=5&rcn=4"
        headers = {
            'Accept': 'application/json',
            'X-M2M-RI': '12345',
            'X-M2M-Origin': 'SOrigin'
        }
        #정보 받아옴
        response = requests.request("GET", url, headers=headers)
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

        print(buy_dict)
        result = {}
        #일단 ㄱ
        for item in buy_dict:
            # 상품구매자가 1명 이상일때,
            if len(buy_dict[item]) > 1:
                test = sorted(buy_dict[item], )
                print(test)
                # for i, item in enumerate(buy_dict[item]):
                #     print(i, item)
                # result[item] = sorted(buy_dict[item], key=lambda x: x[1])
                
       

         
         
        
        # aution_list = sorted(dict.items(), key=lambda x:x[1], reverse=True)

        # print(aution_list) #이해를 돕기 위한 정렬된 딕셔너리 전체 출력
        # print(aution_list[:3]) #상위 3명 출력
        # print(aution_list[0][0]) #1등의 이름 출력! 포인트 출력하려면 [0][1]로 고쳐주면 돼


        self.object_list = self.get_queryset()

        context = self.get_context_data()
        context = get_data(context)
        return self.render_to_response(context) 
        

class RequirementView(ListView):
    #요구사항 페이지 [O]
    template_name = 'administrator/requirement/request.html'
    model = Requirements

class StudentLogView(ListView):
    #학생별 포인트 현황 목록 [O]
    template_name = 'administrator/student/point.html'
    model = Student


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
            
            if count != '':
                old = Item.objects.filter(name=item).count()
                new = int(count)
                
                if new > old:
                    for i in range(new - old):
                        Item.objects.create(
                            student = self.object,
                            name = item,
                            price = Item.objects.filter(name=item)[0].price
                        )
                elif new < old:
                    for i in range(old - new ):
                        last_obj = Item.objects.filter(name=item).last().delete()
                        
        return redirect('administrator:home')
                


        



