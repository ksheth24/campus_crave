from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator


class SellerVerificationApplication(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='verification_applications', null=True, blank=True)
    full_name = models.CharField(max_length=200)
    email = models.EmailField()
    student_id_number = models.CharField(max_length=100)
    student_id_file = models.FileField(upload_to='ids/', blank=True, null=True)
    agree_meal_safety = models.BooleanField(default=False)
    submitted_at = models.DateTimeField(auto_now_add=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)
    reviewed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='reviewed_applications')
    admin_notes = models.TextField(blank=True, help_text="Internal notes for admins reviewing this application")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

    class Meta:
        ordering = ['-submitted_at']

    def __str__(self):
        return f"{self.full_name} <{self.email}> ({self.status})"


class UserProfile(models.Model):
    """Extended user profile for sellers and buyers."""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    is_verified_seller = models.BooleanField(default=False)
    phone_number = models.CharField(max_length=20, blank=True)
    
    def __str__(self):
        return f"{self.user.username} - {'Verified Seller' if self.is_verified_seller else 'Buyer'}"


class Meal(models.Model):
    """Meal listing created by verified sellers."""
    seller = models.ForeignKey(User, on_delete=models.CASCADE, related_name='meals')
    title = models.CharField(max_length=200)
    description = models.TextField()
    ingredients = models.TextField(help_text="List main ingredients")
    photo = models.ImageField(upload_to='meals/', blank=True, null=True)
    price = models.DecimalField(max_digits=6, decimal_places=2)
    
    # Pickup location
    pickup_location = models.CharField(max_length=300)
    pickup_latitude = models.FloatField()
    pickup_longitude = models.FloatField()
    
    # Availability
    is_available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.title} by {self.seller.username} - ${self.price}"


class Reservation(models.Model):
    """Buyer's meal reservation/purchase order."""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed by Seller'),
        ('ready', 'Ready for Pickup'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    meal = models.ForeignKey(Meal, on_delete=models.CASCADE, related_name='reservations')
    buyer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reservations')
    quantity = models.PositiveIntegerField(default=1)
    total_price = models.DecimalField(max_digits=8, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Contact information
    buyer_phone = models.CharField(max_length=20, blank=True, help_text="Contact number for pickup coordination")
    buyer_notes = models.TextField(blank=True, help_text="Special requests or dietary restrictions")
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Order #{self.id} - {self.buyer.username} → {self.meal.title} ({self.status})"
    
    def save(self, *args, **kwargs):
        # Calculate total price
        self.total_price = self.meal.price * self.quantity
        super().save(*args, **kwargs)


class Review(models.Model):
    """Buyer feedback left after pickup for a specific reservation."""
    reservation = models.OneToOneField(Reservation, on_delete=models.CASCADE, related_name='review')
    meal = models.ForeignKey(Meal, on_delete=models.CASCADE, related_name='reviews')
    seller = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_reviews')
    buyer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='written_reviews')
    rating = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Review {self.rating}/5 by {self.buyer.username} for {self.meal.title}"
