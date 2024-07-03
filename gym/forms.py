from django import forms
from .models import Customer
import calendar
class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = ['name', 'gender', 'blood_group', 'height', 'weight', 'membership_type', 'date_of_admission']


class FeePaymentForm(forms.Form):
    admission_number = forms.IntegerField()
    amount = forms.DecimalField(max_digits=10, decimal_places=2, label="Total Amount Paid")
    months = forms.IntegerField(label="Number of Months Paid For")
    start_month = forms.ChoiceField(choices=[(i, calendar.month_name[i]) for i in range(1, 13)], required=False, label="Start Month (Optional)")