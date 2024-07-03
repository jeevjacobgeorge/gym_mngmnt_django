from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from .models import Customer, FeeDetail
from .forms import CustomerForm, FeePaymentForm
def customer_list(request):
    customers = Customer.objects.all()
    return render(request, 'gym/customers.html', {'customers': customers})


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