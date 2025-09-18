from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class PhoneNumber(models.Model):
    """Model to store WhatsApp phone numbers"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='phone_numbers')
    phone_number = models.CharField(max_length=20)
    country_code = models.CharField(max_length=5, default='+1')
    full_phone_number = models.CharField(max_length=25)  # Stores full number with country code
    name = models.CharField(max_length=100, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['user', 'full_phone_number']
        ordering = ['-created_at']
    
    def save(self, *args, **kwargs):
        # Ensure full phone number is properly formatted
        if not self.full_phone_number:
            self.full_phone_number = f"{self.country_code}{self.phone_number}"
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.name or 'Unknown'} - {self.full_phone_number}"


class PhoneNumberGroup(models.Model):
    """Model to group phone numbers for easier management"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='phone_groups')
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    phone_numbers = models.ManyToManyField(PhoneNumber, related_name='groups')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['user', 'name']
        ordering = ['-created_at']
    
    def __str__(self):
        return self.name
    
    def get_phone_count(self):
        return self.phone_numbers.count()
