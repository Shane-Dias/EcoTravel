from django.shortcuts import render, get_object_or_404
from eco_travel_app.forms import TripForm
from .models import Destination, Accommodation, Trip, Review, Transportation
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from .models import Profile
from django.contrib.auth.decorators import login_required
from django.conf import settings
import requests
from django.shortcuts import render, get_object_or_404, redirect
from .forms import DestinationSearchForm
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Profile
from .forms import ProfileForm
from django.shortcuts import render, redirect
from .models import Profile, Images
from .forms import ProfileForm
from django.contrib.auth.decorators import login_required
from .utils import get_location
from datetime import datetime
from . import utils
from decimal import Decimal

GOOGLE_MAPS_API_KEY = 'AIzaSyBYzXj5wF4L6mChyyc5xwfb2QT1QEZ9VN8'

def register_user(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        email = request.POST['email']
        
        # Create user manually
        user = User.objects.create(username=username, password=make_password(password), email=email)
        return redirect('login')  # Redirect to login after successful registration
    
    return render(request, 'register.html')

def login_user(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        
        # Authenticate manually
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect('dashboard')  # Redirect to user dashboard
    
    return render(request, 'login.html')

def logout_user(request):
    logout(request)
    return redirect('login')

@login_required
def dashboard(request):
    trips = Trip.objects.filter(user=request.user)
    # total_miles_saved = sum([trip.destination.distance for trip in trips])  # Assume destination has a 'distance' field
    total_co2_saved = sum([trip.co2 for trip in trips])
    profile, created = Profile.objects.get_or_create(user=request.user)

    return render(request, 'dashboard.html', {
        # 'total_miles_saved': total_miles_saved,
        'total_co2_saved': total_co2_saved,
        'trips': trips,
        'profile': profile,
    })

@login_required
def edit_profile(request):
    # Ensure user profile exists
    profile, created = Profile.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            return redirect('dashboard')  # Redirect to the dashboard after saving changes
    else:
        form = ProfileForm(instance=profile)

    return render(request, 'edit_profile.html', {'form': form, 'profile': profile})

# View for homepage displaying popular destinations
def homepage(request):
    return render(request, 'homepage.html')

def feedback(request):
    return render(request, 'feedback.html')

def carbonfootprint(request):
    return render(request, 'carbon-footprint.html')

def homie(request):
    return render(request, 'home.html')

# View for homepage displaying popular destinations
def home(request):
    destinations = Destination.objects.all()[:7]  # Display top 5 destinations
    return render(request, 'home.html', {'destinations': destinations})

# View for detailed destination page
def destination_detail(request, pk):
    destination = get_object_or_404(Destination, pk=pk)
    accommodations = destination.accommodations.all()
    return render(request, 'destination_detail.html', {'destination': destination, 'accommodations': accommodations})

# View for trip planning
def plan_trip(request, destination_id):
    destination = get_object_or_404(Destination, id=destination_id)
    hotels = Accommodation.objects.filter(destination=destination)
    transportation = Transportation.objects.filter(destination=destination)

    if request.method == 'POST':
        # Manually handle form data
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        people = int(request.POST.get('people', 1))  # Ensure 'people' is an integer
        selected_transportation_id = request.POST.get('transportation')
        selected_hotel_id = request.POST.get('hotel')

        # Calculate the number of nights for the accommodation
        nights = (datetime.strptime(end_date, "%Y-%m-%d") - datetime.strptime(start_date, "%Y-%m-%d")).days

        # Initialize total cost
        total_cost = 0

        # Create the trip object without saving it yet
        trip = Trip(
            start_date=start_date,
            end_date=end_date,
            people=people,
            user=User.objects.get(pk=request.user.pk),
            destination=destination
        )

        transportation_instance = Transportation.objects.get(id=selected_transportation_id)
        trip.transportation = transportation_instance

        accommodation_instance = Accommodation.objects.get(id=selected_hotel_id)
        trip.accommodation = accommodation_instance
        total_cost += accommodation_instance.price_per_night * nights

        # Add any other costs here if needed (e.g., destination fees, activities, etc.)
        emission_factors = {
        'car': 0.2,
        'bus': 0.05,
        'train': 0.1,
        'flight': 0.15,
        'ship': 0.07,
        }
        origin = "Mumbai, India"
        try:
            origin_coords = utils.get_coordinates(origin, utils.API_KEY)
            destination_coords = utils.get_coordinates(trip.destination, utils.API_KEY)
            distance = utils.great_circle_distance(origin_coords[0],origin_coords[1], destination_coords[0], destination_coords[1])
        except Exception as e:
                distance = 0  # Default to 0 if there's an error
                print(f"Error calculating distance: {e}")
        co2_emission = ((distance*emission_factors[transportation_instance.transport_type])/trip.people)*1000
        trip.co2=co2_emission

        # Assign accommodation and calculate its cost if selected

        

                # Assign transportation and calculate its cost if selected
        total_cost += transportation_instance.price_per_km * Decimal(distance)

        # Save the trip
        trip.total_cost = total_cost  # Assuming the Trip model has a total_cost field
        trip.save()

        # Redirect or display a success message after saving the trip
        return redirect('trip_success', trip_id=trip.id)

    else:
        # If GET request, display empty form
        return render(request, 'plan_trip.html', {
            'destination': destination,
            'hotels': hotels,
            'transportation_options': transportation
        })

    

def search_eco_friendly_destinations(query, location, radius):
    api_key = settings.GOOGLE_MAPS_API_KEY  # Access the key from settings
    url = f"https://maps.googleapis.com/maps/api/place/textsearch/json?query={query}&location={location}&radius={radius}&key={api_key}"
    
    response = requests.get(url)
    results = response.json().get('results', [])
    
    return results

from django.shortcuts import render
from .models import Destination

def destination_map(request):
    destinations = Destination.objects.all()  # Fetch all destinations from the database
    return render(request, 'map.html', {'destinations': destinations})


import json

def search_destination(request):
    form = DestinationSearchForm()

    if request.method == 'POST':
        form = DestinationSearchForm(request.POST)
        if form.is_valid():
            destination = form.cleaned_data['destination']
            transport_mode = form.cleaned_data['transport_mode']
            
            # Google Places API - Search for eco-friendly destinations
            api_key = settings.GOOGLE_MAPS_API_KEY
            url = f"https://maps.googleapis.com/maps/api/place/textsearch/json?query=eco-friendly+{destination}&key={api_key}"
            response = requests.get(url)
            destinations = response.json().get('results', [])
            
            # Log the destinations response to see what's returned
            print("Destinations Response:", json.dumps(destinations, indent=4))
            
            # Google Directions API - Find routes with the selected transport mode
            origin = 'user_location'  # Example: get user's location dynamically
            url = f"https://maps.googleapis.com/maps/api/directions/json?origin={origin}&destination={destination}&mode={transport_mode}&key={api_key}"
            directions_response = requests.get(url)
            routes = directions_response.json().get('routes', [])
            
            # Log the routes response
            print("Routes Response:", json.dumps(routes, indent=4))
            
            # Google Distance Matrix API - Calculate distance between origin and destination
            distance_url = f"https://maps.googleapis.com/maps/api/distancematrix/json?origins={origin}&destinations={destination}&key={api_key}"
            distance_response = requests.get(distance_url)
            distance_data = distance_response.json()

            # Log the distance matrix API response for debugging
            print("Distance Matrix API Response:", json.dumps(distance_data, indent=4))

            #weather_url = f"http://api.openweathermap.org/data/2.5/weather?q={Destination}&appid=YOUR_WEATHER_API_KEY"
            #weather_response = requests.get(weather_url)
            #weather_data = weather_response.json()
            
            # Handling the distance data safely
            if distance_data.get('rows') and distance_data['rows'][0].get('elements'):
                distance = distance_data['rows'][0]['elements'][0]['distance'].get('text', 'Not Available')
            else:
                distance = "Distance not available"
            
            # Calculate carbon emissions if distance is available
            if distance != "Distance not available":
                try:
                    distance_value = float(distance.split()[0])  # Assuming the first part is a numeric value
                    emission_factors = {'driving': 0.043, 'transit': 0.041, 'walking': 0, 'bicycling': 0}
                    carbon_emission = distance_value * emission_factors.get(transport_mode, 0)
                except Exception as e:
                    print(f"Error calculating carbon emission: {e}")
                    carbon_emission = "N/A"
            else:
                carbon_emission = "N/A"

            # Log final results to make sure everything is working
            print(f"Distance: {distance}, Carbon Emission: {carbon_emission}")

            return render(request, 'search_results.html', {
                'destinations': destinations,
                'routes': routes,
                'distance': distance,
                'carbon_emission': carbon_emission,
                #'weather': weather_data['weather'][0]['description'],
                #'temperature': weather_data['main']['temp'],
            })

    return render(request, 'search_form.html', {'form': form})


def upload_image(request):
    if request.method == 'POST' and request.FILES.get('image'):
        # Get the uploaded file
        image_file = request.FILES['image']
        # Save the file details to the model
        uploaded_image = Images.objects.create(image=image_file)
        # Replace with your logic to analyze the image
        location = get_location(uploaded_image.image.path)
        
        return render(request, 'index.html', {'city': location['city'],'country': location['ai_country'], 'image_url': uploaded_image.image.url})
    
    return render(request, 'index.html')


def trip_success(request, trip_id):
    trip = Trip.objects.get(id=trip_id)
    cost = "{:,.2f}".format(trip.total_cost)
    co2 = "{:,.2f}".format(trip.co2)
    return render(request, 'trip_success.html', {'trip': trip, "cost":cost, "co2": co2})


def blog(request):
    return render(request, 'blog.html')