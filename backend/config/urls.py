from django.contrib import admin
from django.urls import path
from circulation import views

urlpatterns = [path('admin/', admin.site.urls), path('api/session/', views.session_view), path('api/login/', views.login_view), path('api/logout/', views.logout_view), path('api/dashboard/', views.dashboard), path('api/books/', views.books), path('api/books/<int:pk>/', views.book_detail), path('api/loans/', views.loans), path('api/loans/<int:pk>/return/', views.return_loan), path('api/readers/', views.readers), path('api/reservations/', views.reservations)]
