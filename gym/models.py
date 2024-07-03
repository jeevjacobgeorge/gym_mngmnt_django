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

    name = models.CharField(max_length=255)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    blood_group = models.CharField(max_length=3, choices=BLOOD_GROUP_CHOICES)
    height = models.FloatField(help_text='Height in centimeters')
    weight = models.FloatField(help_text='Weight in kilograms')
    bmi = models.FloatField(editable=False)
    membership_type = models.CharField(max_length=2, choices=MEMBERSHIP_CHOICES)
    admission_number = models.PositiveIntegerField()
    unique_id = models.AutoField(primary_key=True)
    date_of_admission = models.DateField(default=timezone.now)
    
    def save(self, *args, **kwargs):
        self.bmi = self.weight / (self.height/100) ** 2
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name