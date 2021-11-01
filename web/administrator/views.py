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
# Create your views here.
class HomeView(TemplateView):
    #메인화면- (일지목록, 포인트 항목, 장터) [O]
    template_name = 'administrator/main/main.html'


class ObserveLogView(ListView):
    #일지목록 [O]
    template_name = 'administrator/observation/student.html'
    model = Student

    def get(self, request, *args, **kwargs):
        self.object_list = self.get_queryset()
        context = self.get_context_data()
        
        for student in self.object_list:
            context[student] = student.observe_set.all()
        
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
        print('####')
        print(self.object.name)
        
        url = "http://203.253.128.161:7579/Mobius/AduFarm/record/la"

        headers = {
        'Accept': 'application/json',
        'X-M2M-RI': '12345',
        'X-M2M-Origin': 'SOrigin'
        }

        response = requests.request("GET", url, headers=headers)
        get_data = json.loads(response.text)
        record = get_data['m2m:cin']['con']

        #임시 이름
        read_name = self.object.name
        image = record['image']
        title = record['title']
        text = record['intext']

        # Observe.objects.create(
        #     student = Student.objects.get(name = read_name),
        #     image = image,
        #     title = title,
        #     content = text
        # )
        context['object'] = Observe.objects.filter(
            student = Student.objects.get(name = read_name)
            )

        print('####')
        print(context)
        return self.render_to_response(context)


    def post(self, request, *args, **kwargs):
        #피드백 (저장,전송) 확인상태 변경
        self.object = self.get_object()
        feedback = self.request.POST['feedback']
        self.object.feedback = feedback
        self.object.check = 'O'
        self.object.save()

        send_feed = self.object.feedback
        
        #피드백 보내기
        url = "http://203.253.128.161:7579/Mobius/AduFarm/feedback"

        payload='{\n    \"m2m:cin\": {\n        \"con\": \"' + send_feed + '\"\n    }\n}'
        print('####')
        print(payload)

        headers = {
        'Accept': 'application/json',
        'X-M2M-RI': '12345',
        'X-M2M-Origin': '{{aei}}',
        'Content-Type': 'application/vnd.onem2m-res+json; ty=4'
        }

        response = requests.request("POST", url, headers=headers, data=payload.encode('UTF-8'))
        
        print('############')
        print(response.text)
        print('############')
        return redirect('administrator:observation')


class PointView(ListView):
    #포인트 항목 [O]
    template_name = 'administrator/point/point_list.html'
    model = Point

    def get(self, request, *args, **kwargs):
        self.object_list = self.get_queryset()
        #여기 
        #post request
        return HttpResponse

        


def get_context(context):
    context['item1'] = Item.objects.filter(name='item1')
    context['item2'] = Item.objects.filter(name='item2')
    context['item3'] = Item.objects.filter(name='item3')
    
    context['item1_price'] = context['item1'][0].price
    context['item2_price'] = context['item2'][0].price
    context['item3_price'] = context['item3'][0].price
    return context


class PurchaseView(ListView):
    #상품구매현황 [O]
    template_name = 'administrator/purchase/check.html'
    model = Item
 
    def get(self, request, *args, **kwargs):
        self.object_list = self.get_queryset()
        context = self.get_context_data()
        context = get_context(context)
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
    #상품 관리
    template_name = 'administrator/item/item.html'
    model = Student
    fields=['name','price']

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
       
        context = self.get_context_data() 
        context = get_context(context) 
        return self.render_to_response(context) 

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        update_list= {
            'item1' : {
                'price' : self.request.POST.get('item1_price', ''),
                'count' : self.request.POST.get('item1_count', ''),
                'item' : Item.objects.filter(name='item1')
            },
            'item2' : {
                'price' : self.request.POST.get('item2_price',''),
                'count' : self.request.POST.get('item2_count',''),
                'item' : Item.objects.filter(name='item2')
            },
            'item3' : {
                'price' : self.request.POST.get('item3_price', ''),
                'count' : self.request.POST.get('item3_count', ''),
                'item' : Item.objects.filter(name='item3')
            }   
        }
        #새 포인트 가격 저장, 수량 만큼 객체 생성,삭제
        for num in update_list:
            if update_list[num]['price'] != '':
                new_price = update_list[num]['price']
                
                for item in update_list[num]['item']:
                    item.price = new_price
                    item.save()
             
            if update_list[num]['count'] != '':
                new = int(update_list[num]['count'])
                old = update_list[num]['item'].count()

                if new > old:
                    for i in range(new - old):
                        Item.objects.create(
                            student = self.object,
                            name = num,
                            price = items[num][0].price
                        )
                elif new < old:
                    for i in range(old - new ):
                        last_obj = update_list[num]['item'].last()
                        last_obj.delete()
                        
        return redirect('administrator:home')
                


        



