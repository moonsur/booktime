"""booktime URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path
from django.views.generic import TemplateView
from django.views.generic.detail import DetailView
from django.contrib.auth import views as auth_views
from main import forms, views
from main import models


urlpatterns = [   
    path('',TemplateView.as_view(template_name='home.html'), name='home'),
    path('about-us/',views.about_us_View, name='about-us'),
    path('contact-us/', views.ContactUsForm.as_view(), name='contact-us'),
    path('products/<slug:tag>/', views.ProductListView.as_view(), name='products'),
    path('product/<slug:slug>/', DetailView.as_view(template_name='main/product_details.html', model=models.Product), name='product'),
    path('signup/', views.SignupView.as_view(), name='signup'),
    path('address/', views.AddressListView.as_view(), name='address_list'),
    path('address/create/', views.AddressCreateView.as_view(), name='address_create'),
    path('address/<int:pk>/', views.AddressUpdateView.as_view(), name='address_update'),
    path('address/select/', views.AddressSelectionView.as_view(), name='address_selection'),
    path('address/<int:pk>/delete/', views.AddressDeleteView.as_view(), name='address_delete'),
    path('add-to-basket/', views.add_to_basket, name='add_to_basket'),
    path('basket/', views.manage_basket, name='basket'),
    path('order/done/', TemplateView.as_view(template_name='main/order_done.html'), name='checkout_done'),
    path('login/', auth_views.LoginView.as_view(template_name='login.html', form_class=forms.LoginForm), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
]
