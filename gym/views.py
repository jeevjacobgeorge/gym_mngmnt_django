from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from .models import Customer, FeeDetail
# from .forms import CustomerForm, FeePaymentForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
import datetime
from django.db import models
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
        dob = request.POST.get('dob')
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
                date_of_birth=dob,
                date_of_admission=timezone.now()
            )
            new_customer.save()
            return redirect('profile', customer_id=new_customer.pk)
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
def pay_fees(request, cust_id):
    customer = get_object_or_404(Customer, pk=cust_id)
    
    # Get the last month the customer paid fees
    last_payment = FeeDetail.objects.filter(customer=customer).order_by('-year', '-month').first()
    if last_payment:
        last_month_paid = last_payment.month
        last_year_paid = last_payment.year
    else:
        last_month_paid = datetime.datetime.now().month-1   
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
@login_required
def fee_details(request):
    gender = request.GET.get('gender', 'select')
    year = request.GET.get('year', timezone.now().year)
    search_query = request.GET.get('search', '').strip()

    # Filter customers by gender
    customers = Customer.objects.all()
    if (gender != 'select'):
        customers = customers.filter(gender=gender)

    # Filter customers by search query for name or membership ID
    if search_query:
        customers = customers.filter(
            models.Q(name__icontains=search_query) | 
            models.Q(admission_number__icontains=search_query)
        )

    # Validate year
    try:
        year = int(year)
    except ValueError:
        year = timezone.now().year

    # Map month numbers to their abbreviations
    month_abbreviations = {
        1: 'Jan', 2: 'Feb', 3: 'Mar', 4: 'Apr',
        5: 'May', 6: 'Jun', 7: 'Jul', 8: 'Aug',
        9: 'Sep', 10: 'Oct', 11: 'Nov', 12: 'Dec'
    }
    
    months = [month_abbreviations[i] for i in range(1, 13)]

    # Create a list to hold the customer fee details
    customer_fee_details = []
    for customer in customers:
        # Fetch the FeeDetail objects for the customer and year
        fee_details = FeeDetail.objects.filter(customer=customer, year=year)
        
        # Initialize a dictionary to hold the status for each month
        fees_status = {}
        
        for month in range(1, 13):
            # Get the fee detail for the specific month
            fee_detail = fee_details.filter(month=month).first()
            if fee_detail:
                # If fee is paid for the month, store the category
                fees_status[month_abbreviations[month]] = fee_detail.get_category_display()
            else:
                # If no fee is paid, store 'Not Paid'
                fees_status[month_abbreviations[month]] = False
        
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
        'months': months,
        'year': year,
    }

    # Return JSON response for AJAX requests
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse(context)
    
    # Render the HTML template for non-AJAX requests
    return render(request, 'gym/feeDetails.html', context)

@login_required
def profile_view(request, customer_id):
    customer = get_object_or_404(Customer, pk=customer_id)
    latest_fee_detail = customer.feedetail_set.order_by('-date_of_payment').first()
    if customer.date_of_birth:
        age = timezone.now().year - customer.date_of_birth.year
    else:
        age = None
    context = {
        'name': customer.name,
        'id': customer.pk,
        'gender': customer.get_gender_display(),
        'age': age,
        'email': customer.email,
        'phone': customer.phone_no,
        'height': customer.height,
        'weight': customer.weight,
        'bmi': customer.bmi,
        'bloodGroup': customer.get_blood_group_display(),
        'doj': customer.date_of_admission,
        'category': latest_fee_detail.get_category_display() if latest_fee_detail else 'N/A',
        'activeMonth': latest_fee_detail.get_month_display() if latest_fee_detail else 'N/A'
    }
    return render(request, 'gym/profile.html', context)
@login_required
def edit_customer(request, customer_id):
    customer = get_object_or_404(Customer, pk=customer_id)

    if request.method == 'POST':
        # Get the updated details from the form
        name = request.POST.get('name')
        phone = request.POST.get('phone', None)
        email = request.POST.get('email', None)
        gender = request.POST.get('gender')
        height = request.POST.get('height', None)
        weight = request.POST.get('weight', None)
        blood_group = request.POST.get('bloodGroup')
        dob = request.POST.get('dob')

        try:
            # Update the customer details
            customer.name = name
            customer.phone_no = phone
            customer.email = email
            customer.gender = gender
            customer.height = float(height) if height else None
            customer.weight = float(weight) if weight else None
            customer.blood_group = blood_group
            customer.date_of_birth = dob  # Ensure dob is in 'YYYY-MM-DD' format
            customer.save()

            return redirect('profile', customer_id=customer_id)
        except ValueError:
            return render(request, 'gym/edit_customer.html', {'error': 'Invalid input. Please enter valid data.', 'customer': customer})

    return render(request, 'gym/edit_customer.html', {'customer': customer})