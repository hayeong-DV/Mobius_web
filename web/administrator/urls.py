from django.urls import path, include
from administrator import views
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views

# from rest_framework_jwt.views import obtain_jwt_token
# from rest_framework.authtoken.views import obtain_auth_token
# from rest_framework_simplejwt.views import (
#     TokenObtainPairView,
#     TokenRefreshView,
# )


app_name='administrator'

urlpatterns=[
    #메인화면 - (일지목록, 포인트 항목, 장터)
    path('', views.HomeView.as_view(), name='home'),

    #회원가입
    path('register', views.RegisterView.as_view(), name='register'),
    path('api/register', views.RegisterAPIView.as_view(), name='api_register'),

    #로그인
    path('login/', auth_views.LoginView.as_view(template_name='administrator/account/login.html'), name='login'),
    #로그인 API
    # path("api/token", TokenObtainPairView.as_view()),  # 토큰 발급
    # path("api/refresh", TokenRefreshView.as_view()),  # 토큰 재발급
    path('api/login', views.LoginAPIView.as_view(), name='api_login' ),
   

    #로그아웃
    path('logout/', auth_views.LogoutView.as_view(next_page = 'administrator:home'), name='logout'),
    
    #관리자별-학생목록
    path('student-list', views.StudentListView.as_view(), name='student_list' ),
    path('api/student-list', views.StudentListAPIView.as_view(), name='api_student_list' ),

    #관리자별-학생 추가
    path('student-list/add', views.StudentAddView.as_view(), name='student_add' ),
    # path('api/student-list', views.StudentListAPIView.as_view(), name='api_student_list' ),

    #관리자별-학생-업데이트, 삭제
    path('student-list/<int:pk>/detail', views.StudentDetailView.as_view(), name='student_detail' ),
    path('api/student-list/<int:pk>/detail', views.StudentDetailAPIView.as_view(), name='api_student_detail' ),

    
    #일지목록
    path('observation', views.ObserveLogView.as_view(), name='observation'),
    # path('api-observation', vie∂s.ObserveLogAPIView.as_view(), name='api_observation'),

    #일지세부(학생별)
    path('observation/<int:pk>', views.LogDetailView.as_view(), name='log_detail'),

    #포인트 항목 일단pass(create,put,delete)
    path('point', views.PointView.as_view(), name='point_list'),
    path('api/point', views.PointAPIView.as_view(), name='api_point_list'),

    #장터
    path('market', views.MarketView.as_view(), name='market'),
    # path('api/market', views.MarketAPIView.as_view(), name='market'),

    #상품구매현황(상품, 포인트 정렬, 계산)
    path('purchase', views.PurchaseView.as_view(), name='purchase'),

    #상품구매현황_확인용)
    path('check-purchase', views.CheckPurchaseView.as_view(), name='check_purchase'),
    
    #요구사항 페이지
    path('requirement', views.RequirementView.as_view(), name='requirement'),
   
    #학생별 포인트 현황 목록
    path('student-log', views.StudentLogView.as_view(), name='student_log'),
    # path('api-student-log', views.StudentLogAPIView.as_view(), name='student-log'),
    
  
    #상품 관리
    path('item-update/<int:pk>', views.ItemManageView.as_view(), name='item_manage'),
    # path('api/item-update/', views.ItemManageView.as_view(), name='item-update'),

] + static(settings.MEDIA_URL, document_root = settings.MEDIA_ROOT)