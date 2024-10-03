from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from .models import Customer, FeeDetail
# from .forms import CustomerForm, FeePaymentForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
import datetime
from datetime import datetime
from django.db import models
@login_required
def dashboard(request):
    data ={}
    data['no_of_customers'] = Customer.objects.count()
    data['no_of_male'] = Customer.objects.filter(gender='M').count()
    data['no_of_female'] = Customer.objects.filter(gender='F').count()
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
        admission_number = request.POST.get('admission_number')
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
                admission_number=admission_number,
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
def fee_details(request):
    gender = request.GET.get('gender', 'select')
    year = request.GET.get('year', timezone.now().year)
    search_query = request.GET.get('search', '').strip()

    # Filter customers by gender
    customers = Customer.objects.all()
    if gender != 'select':
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

    # Get the current month and handle months across the year boundary
    current_month = datetime.now().month + 3
    months_to_show = [(current_month - i) % 12 or 12 for i in range(2, -1, -1)]

    # Get the corresponding years for those months
    months_and_years = []
    for i, month in enumerate(months_to_show):
        # If the month is ahead of the current month, it means it belongs to the previous year
        year_for_month = year - 1 if month > current_month else year
        months_and_years.append((month, year_for_month))

    # Map month numbers to their abbreviations
    month_abbreviations = {
        1: 'Jan', 2: 'Feb', 3: 'Mar', 4: 'Apr',
        5: 'May', 6: 'Jun', 7: 'Jul', 8: 'Aug',
        9: 'Sep', 10: 'Oct', 11: 'Nov', 12: 'Dec'
    }

    months = [month_abbreviations[month] for month, _ in months_and_years]

    # Create a list to hold the customer fee details, only for those who paid in the last 4 months
    active_customers = []
    for customer in customers:
        # Initialize a dictionary to store fee status for each displayed month
        fees_status = {}
        paid_count = 0

        for month, month_year in months_and_years:
            # Fetch the FeeDetail object for the specific month and year
            fee_detail = FeeDetail.objects.filter(customer=customer, year=month_year, month=month).first()
            if fee_detail:
                # If fee is paid, store the category and increment paid_count
                fees_status[month_abbreviations[month]] = fee_detail.get_category_display()
                paid_count += 1
            else:
                # If no fee is paid, store 'Not Paid'
                fees_status[month_abbreviations[month]] = 'Not Paid'

        # Only include customers who have paid for at least one month in the last 4 months
        if paid_count > 0:
            active_customers.append({
                'customer': {
                    'id': customer.pk,
                    'admission_number': customer.admission_number,
                    'name': customer.name,
                },
                'fees_status': fees_status,
                'paid_count': paid_count  # Track how many months they paid
            })

    # Sort customers by activity (paid_count in descending order)
    active_customers.sort(key=lambda x: x['paid_count'], reverse=True)

    context = {
        'customers': active_customers,
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
@login_required
def pay_fees(request, customer_id):
    customer = get_object_or_404(Customer, pk=customer_id)
    
    # Prepare the list of years (current year and previous few years)
    current_year = timezone.now().year
    years = list(range(current_year, current_year - 5, -1))  # e.g., last 5 years

    if request.method == 'POST':
        category = request.POST.get('category')
        amount = request.POST.get('amount')
        month = request.POST.get('month')
        year = request.POST.get('year')  # Get the year from the form
        dop = request.POST.get('dop')
        
        # Parse the form inputs to the appropriate types
        amount = float(amount)
        
        # Map month names to numbers
        month_mapping = {
            "January": 1, "February": 2, "March": 3, "April": 4, 
            "May": 5, "June": 6, "July": 7, "August": 8, 
            "September": 9, "October": 10, "November": 11, "December": 12
        }

        # Convert month name to an integer
        month = month_mapping.get(month)
        if month is None:
            raise ValueError("Invalid month selected")

        # Convert the year to an integer
        year = int(year)

        # Create FeeDetail entry
        fee_detail = FeeDetail(
            customer=customer,
            amount_paid=amount,
            date_of_payment=dop if dop else timezone.now(),
            category=category,
            month=month,
            year=year  # Save the selected year
        )
        fee_detail.save()

        # Redirect back to the fee details page after saving
        return redirect('feeDetails')

    # If the request is GET, show the form
    context = {
        'customer': customer,
        'years': years  # Pass the list of years to the template
    }
    return render(request, 'gym/pay_fees.html', context)


def customer_fee_details(request, customer_id):
    customer = get_object_or_404(Customer, pk=customer_id)
    fee_details = FeeDetail.objects.filter(customer=customer).order_by('year', 'month')
    
    context = {
        'customer': customer,
        'fee_details': fee_details,
    }
    return render(request, 'gym/customer_fee_details.html', context)