from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone

class User(AbstractUser):
    ROLE_CHOICES = (
        ('employee', 'Employee'),
        ('manager', 'Manager'),
        ('admin', 'Admin'),
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='employee')
    location = models.CharField(max_length=100, blank=True)
    country = models.CharField(max_length=100, default='USA')
    
    def __str__(self):
        return f"{self.get_full_name()} ({self.role})"

class TimeOffRequest(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    )
    
    TYPE_CHOICES = (
        ('vacation', 'Vacation'),
        ('sick', 'Sick Leave'),
        ('personal', 'Personal Leave'),
        ('other', 'Other'),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='time_off_requests')
    type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='vacation')
    start_date = models.DateField()
    end_date = models.DateField()
    reason = models.TextField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    reviewed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='reviewed_requests')
    review_comment = models.TextField(blank=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.start_date} to {self.end_date}"
    
    class Meta:
        ordering = ['-created_at']

class Holiday(models.Model):
    country = models.CharField(max_length=100, default='USA')
    location = models.CharField(max_length=100, default='ALL')
    name = models.TextField()
    date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.name} - {self.date}"
    
    class Meta:
        ordering = ['date']