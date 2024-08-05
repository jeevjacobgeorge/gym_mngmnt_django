from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from .models import Customer, FeeDetail
# from .forms import CustomerForm, FeePaymentForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
import datetime

@login_required
def dashboard(request):
    data ={}
    data['no_of_customers'] = Customer.objects.count()
    data['no_of_male'] = Customer.objects.filter(gender='male').count()
    data['no_of_female'] = Customer.objects.filter(gender='female').count()
    all_customers = Customer.objects.all()
    active_customers = [customer for customer in all_customers if customer.is_active]
    data['no_of_active'] = len(active_customers)
    return render(request, 'gym/dashboard.html',data)

def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
def add_customer(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        phone = request.POST.get('phone', None)  # Default to None if not provided
        email = request.POST.get('email', None)  # Default to None if not provided
        gender = request.POST.get('gender')
        height = request.POST.get('height', None)  # Default to None if not provided
        weight = request.POST.get('weight', None)  # Default to None if not provided
        blood_group = request.POST.get('bloodGroup')
        doj = request.POST.get('doj')
        # Validate and save form data
        try:
            new_customer = Customer(
                name=name,
                phone_no=phone,
                email=email,
                gender=gender,
                height=float(height) if height else None,
                weight=float(weight) if weight else None,
                blood_group=blood_group,
                date_of_admission=doj
            )
            new_customer.save()
            return render(request,'gym/success.html')  # Replace 'success' with the URL name for success page
        except ValueError:
           return render(request,'gym/add_customer.html', {'error': 'Invalid input. Please enter valid data.'})

   

    return render(request, 'gym/add_customer.html')



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
def fee_details(request):
    customers = Customer.objects.all()
    months = list(range(1, 13))  # Representing months from January to December
    current_year = datetime.datetime.now().year
    
    # Create a list to hold the customer fee details
    customer_fee_details = []
    for customer in customers:
        fees_paid = FeeDetail.objects.filter(customer=customer, year=current_year).values_list('month', flat=True)
        fees_status = {month: month in fees_paid for month in months}
        customer_fee_details.append({
            'customer': {
                'id': customer.pk,
                'admission_number': customer.admission_number,
                'name': customer.name,
            },
            'fees_status': fees_status
        })

    context = {
        'customers': customer_fee_details,
        'months': months
    }

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse(context)
    else:
        return render(request, 'gym/feeDetails.html', context)
    
@login_required
def pay_fees(request, cust_id):
    customer = get_object_or_404(Customer, pk=cust_id)
    
    # Get the last month the customer paid fees
    last_payment = FeeDetail.objects.filter(customer=customer).order_by('-year', '-month').first()
    if last_payment:
        last_month_paid = last_payment.month
        last_year_paid = last_payment.year
    else:
        last_month_paid = datetime.datetime.now().month
        last_year_paid = datetime.datetime.now().year

    if request.method == 'POST':
        amount = request.POST.get('amount')
        no_of_months = int(request.POST.get('duration'))
        startMonth = int(request.POST.get('startMonth'))
        category = request.POST.get('category')
        if not startMonth:
            startMonth = last_month_paid + 1
        month = startMonth 
        year = last_year_paid
        amount_per_month = round(float(amount) / float(no_of_months), 2)
        for i in range(no_of_months):
            FeeDetail.objects.create(
                customer=customer,
                amount_paid=amount_per_month,
                month=month,
                year=year,
                category=category
            )
            month += 1
            if month > 12:
                month = 1
                year += 1
        
        return redirect('feeDetails')

    return render(request, 'gym/pay_fees.html', {'customer': customer, 'last_month_paid': last_month_paid})
