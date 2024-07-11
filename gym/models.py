from django.db import models
from django.utils import timezone

class Customer(models.Model):
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
    ]

    BLOOD_GROUP_CHOICES = [
        ('A+', 'A+'),
        ('A-', 'A-'),
        ('B+', 'B+'),
        ('B-', 'B-'),
        ('AB+', 'AB+'),
        ('AB-', 'AB-'),
        ('O+', 'O+'),
        ('O-', 'O-'),
    ]

    WEIGHT_TRAINING = 'WT'
    CARDIO = 'C'
    BOTH = 'B'

    MEMBERSHIP_CHOICES = [
        (WEIGHT_TRAINING, 'Weight Training'),
        (CARDIO, 'Cardio'),
        (BOTH, 'Both'),
    ]

    unique_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    phone_no = models.CharField(max_length=10, blank=True)
    email = models.EmailField(null=True, blank=True)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    height = models.FloatField(help_text='Height in centimeters', null=True, blank=True)
    weight = models.FloatField(help_text='Weight in kilograms', null=True, blank=True)
    blood_group = models.CharField(max_length=3, choices=BLOOD_GROUP_CHOICES)
    bmi = models.FloatField(editable=False, null=True, blank=True)
    admission_number = models.PositiveIntegerField(editable=False, default=0)
    date_of_admission = models.DateField(default=timezone.now)

    @property
    def is_active(self):
        current_year = timezone.now().year
        current_month = timezone.now().month
        fees_paid = self.feedetail_set.filter(date_of_payment__year=current_year).values_list('month', flat=True)
        return current_month in fees_paid

    @property
    def months_remaining(self):
        current_year = timezone.now().year
        current_month = timezone.now().month
        fees_paid = self.feedetail_set.filter(date_of_payment__year=current_year).values_list('month', flat=True)
        remaining_months = len([month for month in range(current_month, 13) if month not in fees_paid])
        return remaining_months

    def save(self, *args, **kwargs):
        if not self.admission_number:
            last_customer = Customer.objects.filter(gender=self.gender).order_by('admission_number').last()
            if last_customer:
                self.admission_number = last_customer.admission_number + 1
            else:
                self.admission_number = 10000
        if self.height and self.weight:
            self.bmi = self.weight / (self.height / 100) ** 2
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    def pay_fees(self, amount, months, start_month=None):
        """
        Function to pay fees for multiple months.
        :param amount: Total amount paid
        :param months: Number of months paid for
        :param start_month: Optional start month, defaults to the current month
        """
        if not start_month:
            start_month = timezone.now().month

        month = start_month
        year = timezone.now().year
        amount_per_month = round(amount / months, 2)

        for _ in range(months):
            if month > 12:
                month = 1
                year += 1
            FeeDetail.objects.create(
                customer=self,
                amount_paid=amount_per_month,
                date_of_payment=timezone.now(),
                month=month,
            )
            month += 1

class FeeDetail(models.Model):
    MONTH_CHOICES = [
        (1, 'January'),
        (2, 'February'),
        (3, 'March'),
        (4, 'April'),
        (5, 'May'),
        (6, 'June'),
        (7, 'July'),
        (8, 'August'),
        (9, 'September'),
        (10, 'October'),
        (11, 'November'),
        (12, 'December'),
    ]

    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2)
    date_of_payment = models.DateField(default=timezone.now)
    category = models.CharField(choices=Customer.MEMBERSHIP_CHOICES, max_length=2, default=Customer.WEIGHT_TRAINING)
    month = models.PositiveSmallIntegerField(choices=MONTH_CHOICES, default=timezone.now().month)
    year = models.IntegerField(default=timezone.now().year)

    def __str__(self):
        return f"{self.customer.name} - {self.get_month_display()} - {self.amount_paid}"

class CategoryTable(models.Model):
    name = models.CharField(choices=Customer.MEMBERSHIP_CHOICES, max_length=2, default=Customer.WEIGHT_TRAINING)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.get_name_display()
