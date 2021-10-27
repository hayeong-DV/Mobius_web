from django.urls import path
from administrator import views

app_name='administrator'

urlpatterns=[
    #메인화면 - (일지목록, 포인트 항목, 장터)
    path('', views.HomeView.as_view(), name='home'),
    
    #일지목록
    #일지세부(학생별)

    #포인트 항목

    #장터

    #상품구매현황
    
    #요구사항 페이지
   
    #학생별 포인트 현황 목록
  
    # path('', views.PostLV.as_view(), name='index'),

]