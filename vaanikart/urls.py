# bot/urls.py
from django.urls import path
from .views import whatsapp_webhook, ProductListView

urlpatterns = [
    path("webhook/", whatsapp_webhook, name="whatsapp_webhook"),
    # path('products/create/', ProductCreateView.as_view(), name='product-create'),
    path('api/products/', ProductListView.as_view(), name='product-list')
]
