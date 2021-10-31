from django.urls import path
from administrator import views

app_name='administrator'

urlpatterns=[
    #메인화면 - (일지목록, 포인트 항목, 장터)
    path('', views.HomeView.as_view(), name='home'),
    
    #일지목록
    path('observation', views.ObserveLogView.as_view(), name='observation'),

    #일지세부(학생별)
    path('observation/<int:pk>', views.LogDetailView.as_view(), name='log_detail'),

    #포인트 항목
    path('point', views.PointView.as_view(), name='point_list'),

    #장터

    #상품구매현황
    path('purchase', views.PurchaseView.as_view(), name='purchase'),
    
    #요구사항 페이지
    path('requirement', views.RequirementView.as_view(), name='requirement'),
   
    #학생별 포인트 현황 목록
    path('student-log', views.StudentLogView.as_view(), name='student-log'),
  
    #상품 관리
    path('item-update/<int:pk>', views.ItemUpdateView.as_view(), name='item-update'),

]