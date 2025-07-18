# bot/urls.py
from django.urls import path
from .views import whatsapp_webhook, ProductListView,delete_product_by_name

urlpatterns = [
    path("webhook/", whatsapp_webhook, name="whatsapp_webhook"),
    # path('products/create/', ProductCreateView.as_view(), name='product-create'),
    path('api/products/', ProductListView.as_view(), name='product-list'),
    path('api/products/delete-by-name/', delete_product_by_name, name='delete-product-by-name'),

]
