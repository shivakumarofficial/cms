from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_view, name='home'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register_view, name='register'),
    path('new-request/', views.new_request_view, name='new_request'),
    path('manage/', views.manage_requests_view, name='manage_requests'),
    path('history/', views.history_view, name='history'),
    path('holidays/', views.holidays_view, name='holidays'),
    path('add-holiday/', views.add_holiday_view, name='add_holiday'),
    path('review/', views.review_view, name='review'),
    path('data/', views.data_view, name='data'),
    path('download-pdf-report/', views.download_pdf_report, name='download_pdf_report'),
    path('approve/<int:request_id>/', views.approve_request, name='approve_request'),
    path('reject/<int:request_id>/', views.reject_request, name='reject_request'),
]