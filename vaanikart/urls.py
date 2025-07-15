# bot/urls.py
from django.urls import path
from .views import whatsapp_webhook , ProductListView

urlpatterns = [
    path("webhook/", whatsapp_webhook, name="whatsapp_webhook"),
    path('api/products/', ProductListView.as_view(), name='product-list'),
    

]
