from django.contrib import admin
from .models import User , Profile, Destination, Accommodation, Transportation, Trip, Review, Badge, Achievement, CarbonOffset, AdminDashboard, Images, UploadedPlanTrip

# Register your models here
admin.site.register(Profile)
admin.site.register(Destination)
admin.site.register(Accommodation)
admin.site.register(Transportation)
admin.site.register(Trip)
admin.site.register(Review)
admin.site.register(Badge)
admin.site.register(Achievement)
admin.site.register(CarbonOffset)
admin.site.register(AdminDashboard)
admin.site.register(Images)
admin.site.register(UploadedPlanTrip)