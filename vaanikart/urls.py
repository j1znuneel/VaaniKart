# bot/urls.py
from django.urls import path
from .views import whatsapp_webhook,ProductCreateView

urlpatterns = [
    path("webhook/", whatsapp_webhook, name="whatsapp_webhook"),
    path('products/create/', ProductCreateView.as_view(), name='product-create'),
]
