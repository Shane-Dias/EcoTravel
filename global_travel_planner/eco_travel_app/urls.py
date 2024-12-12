from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.homepage, name='home'),
    path('homepage', views.homepage, name='homepage'),
    path('feedback/', views.feedback, name='feedback'),
    path('home', views.home, name='home'),
    path('register/', views.register_user, name='register'),
    path('logout/', views.logout_user, name='logout'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    path('login/', views.login_user, name='login'),
    path('map/', views.destination_map, name='map'),
    path('results/', views.search_destination, name='search_results'),  # Displays search results
    path('plan_trip/<int:destination_id>/', views.plan_trip, name='plan_trip'),  # For planning a trip
    path('destination/<int:pk>/', views.destination_detail, name='destination_detail'),  # Destination detail page
    path('destination/<int:destination_id>/plan/', views.plan_trip, name='plan_trip'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    path('dashboard/', views.dashboard, name='dashboard'),  # for the dashboard
    path('search_form', views.search_destination, name='search_destination'),  # Homepage for searching destinations
    path('carbon-footprint.html', views.carbonfootprint, name='carbon-footprint'),
    path('upload_image', views.upload_image, name='upload_image'),
    path('trip_success/<int:trip_id>', views.trip_success, name='trip_success'),
    path('blog', views.blog, name='blog'),
    path('search-destinations/', views.search_destinations, name='search_destinations'),
    path('uploaded-plan-trip/', views.uploaded_plan_trip, name='uploaded_plan_trip'),
    path('eco_tips', views.eco_tips, name='eco_tips'),
    path('ecobot', views.ecobot, name='ecobot'),
    path('plan-trip/', views.plan_trip2, name='plan_trip'),

]

if settings.DEBUG:  # Only for development
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)