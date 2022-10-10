
from django.urls import path
from . import views

#now import the views.py file into this code

urlpatterns=[
  path('', views.home),
  path('seller', views.seller_page),
  path('weighmen', views.weighmen_page),
  path('add_seller/', views.add_seller),
  path('add_weighmen/', views.add_weighmen),
  path('add_sales/', views.add_sales),
  path('view_sales/', views.view_sales),

]