from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from .models import Customer, FeeDetail
from .forms import CustomerForm, FeePaymentForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
def customer_list(request):
    customers = Customer.objects.all()
    return render(request, 'gym/customers.html', {'customers': customers})

@login_required
def add_customer(request):
    if request.method == 'POST':
        form = CustomerForm(request.POST)
        if form.is_valid():
            customer = form.save(commit=False)
            customer.save()
            return redirect('customer_list')
    else:
        form = CustomerForm()
    return render(request, 'gym/add_customer.html', {'form': form})


@login_required
def pay_fees(request):
    if request.method == 'POST':
        form = FeePaymentForm(request.POST)
        if form.is_valid():
            admission_number = form.cleaned_data['admission_number']
            customer = get_object_or_404(Customer, admission_number=admission_number)
            amount = form.cleaned_data['amount']
            months = form.cleaned_data['months']
            start_month = int(form.cleaned_data['start_month']) if form.cleaned_data['start_month'] else timezone.now().month
            customer.pay_fees(amount=amount, months=months, start_month=start_month)
            return redirect('customer_list')
    else:
        form = FeePaymentForm()
    return render(request, 'gym/pay_fees.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('dashboard')
    else:
        form = AuthenticationForm()
    return render(request, 'gym/login.html', {'form': form})


@login_required
def dashboard(request):
    return render(request, 'gym/dashboard.html')

def logout_view(request):
    logout(request)
    return redirect('login')