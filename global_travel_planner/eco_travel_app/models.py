from django.db import models
from django.contrib.auth.models import User  # Use Django's built-in User model

# Profile Model
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(blank=True)
    location = models.CharField(max_length=100, blank=True)
    preferences = models.JSONField(default=dict)  # Store user preferences like favorite destinations, transport modes
    profile_pic = models.ImageField(upload_to='profile_pics/', blank=True)
    travel_miles_saved = models.FloatField(default=0)
    co2_saved = models.FloatField(default=0)  # Carbon footprint saved through eco-friendly travel
    date_joined = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.username

# Destination Model
class Destination(models.Model):
    name = models.CharField(max_length=200)
    country = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    description = models.TextField()
    image = models.ImageField(upload_to='static/', blank=True)  # Path corrected
    eco_rating = models.FloatField(default=0)  # User-assigned eco-friendliness rating
    best_season = models.CharField(max_length=100, blank=True)
    activities = models.TextField()  # Eco-friendly activities, e.g., hiking, cycling, etc.
    
    def __str__(self):
        return f"{self.name}, {self.city}"

# Accommodation Model
class Accommodation(models.Model):
    name = models.CharField(max_length=200)
    destination = models.ForeignKey(Destination, on_delete=models.CASCADE, related_name='accommodations')
    description = models.TextField()
    eco_certifications = models.CharField(max_length=255, blank=True)  # e.g., LEED, Green Key
    price_per_night = models.DecimalField(max_digits=10, decimal_places=2)
    availability = models.BooleanField(default=True)
    image = models.ImageField(upload_to='accommodation_images/', blank=True)
    website_url = models.URLField(blank=True)
    
    def __str__(self):
        return self.name

# Transportation Model
class Transportation(models.Model):
    TRANSPORT_TYPE_CHOICES = [
        ('car', 'Car'),
        ('electric_car', 'Electric Car'),
        ('bus', 'Bus'),
        ('train', 'Train'),
        ('cycle', 'Bicycle'),
        ('walk', 'Walk'),
        ('flight', 'Flight'),
    ]
    
    name = models.CharField(max_length=200)
    transport_type = models.CharField(max_length=50, choices=TRANSPORT_TYPE_CHOICES)
    co2_per_km = models.FloatField(help_text='CO2 emission per km in grams')  # Store CO2 per km for calculation
    available = models.BooleanField(default=True)
    destination = models.ForeignKey(Destination, on_delete=models.CASCADE, related_name='transport_options')
    price_per_km = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    
    def __str__(self):
        return f"{self.name} - {self.transport_type}"

# Trip Model
class Trip(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='trips')  # Use Django's User model
    destination = models.ForeignKey(Destination, on_delete=models.CASCADE, related_name='trips')
    accommodation = models.ForeignKey(Accommodation, on_delete=models.SET_NULL, null=True, blank=True)
    transportation = models.ForeignKey(Transportation, on_delete=models.SET_NULL, null=True, blank=True)
    start_date = models.DateField()
    end_date = models.DateField()
    total_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    co2 = models.Field(default=0)  # Calculated by comparing eco-friendly choices to alternatives
    people = models.IntegerField(default=1, null=False)  # Calculated by comparing eco-friendly choices to alternatives


    def __str__(self):
        return f"{self.user.username}'s Trip to {self.destination.name}"

# Review Model For users to review eco-friendly destinations, accommodations, and transport options.
class Review(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews')  # Use Django's User model
    destination = models.ForeignKey(Destination, on_delete=models.CASCADE, related_name='reviews', null=True, blank=True)
    accommodation = models.ForeignKey(Accommodation, on_delete=models.CASCADE, related_name='reviews', null=True, blank=True)
    transportation = models.ForeignKey(Transportation, on_delete=models.CASCADE, related_name='reviews', null=True, blank=True)
    rating = models.PositiveSmallIntegerField(default=1)  # Rating from 1 to 5
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.username}'s review"

# Badge and Achievement Models To handle gamification like eco-friendly achievements and badges.
class Badge(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    icon = models.ImageField(upload_to='badge_icons/', blank=True)

    def __str__(self):
        return self.name

class Achievement(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='achievements')  # Use Django's User model
    badge = models.ForeignKey(Badge, on_delete=models.CASCADE)
    date_awarded = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.username} earned {self.badge.name}"

# Carbon Offset Model For users to offset their travel carbon footprint.
class CarbonOffset(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='carbon_offsets')  # Use Django's User model
    amount_offset = models.FloatField(help_text="Amount of CO2 offset in kilograms")
    offset_provider = models.CharField(max_length=255)  # Provider for carbon offset, e.g., an NGO or project
    purchase_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} offset {self.amount_offset} kg of CO2"
    
# Admin Dashboard Model
class AdminDashboard(models.Model):
    admin_user = models.OneToOneField(User, on_delete=models.CASCADE, limit_choices_to={'is_staff': True})  # Use Django's User model
    created_at = models.DateTimeField(auto_now_add=True)
    total_users = models.PositiveIntegerField(default=0)
    total_trips_planned = models.PositiveIntegerField(default=0)
    total_carbon_saved = models.FloatField(default=0)  # Sum of all carbon reductions from user trips

    def __str__(self):
        return f"Admin Dashboard - {self.admin_user.username}"


class Images(models.Model):
    id = models.AutoField(primary_key=True)
    image = models.ImageField(upload_to="images/")
    date = models.DateTimeField(auto_now_add=True)

