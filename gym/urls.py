from django.urls import path
from .views import *

urlpatterns = [
    path('customers/', customer_list, name='customer_list'),
    path('customers/add/', add_customer, name='add_customer'),
    path('customers/pay_fees/', pay_fees, name='pay_fees'),
]
