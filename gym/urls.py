from django.urls import path
from .views import *

urlpatterns = [
    path('',dashboard, name='dashboard'),
    path('add/', add_customer, name='add_customer'),
    # path('pay_fees/', pay_fees, name='pay_fees'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('fees/', fee_details, name='feeDetails'),
    path('pay_fees/<int:cust_id>/',pay_fees, name = "pay_fees"),
    path('profile/<int:customer_id>/', profile_view, name='profile'),
    path('edit/<int:customer_id>/', edit_customer, name='edit_customer'),

]
