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
    if request.user.is_authenticated:
        # Delete the user account from the database
        user = request.user
        logout(request)  # End the session
        user.delete()    # Delete the user from the database
    
    return redirect('login')

@login_required
def dashboard(request):

    # Get the logged-in user's trips, sorted by co2_saved in descending order
    trips = Trip.objects.filter(user=request.user).order_by('-co2_saved')
    profile, created = Profile.objects.get_or_create(user=request.user)

    return render(request, 'dashboard.html', {
        # 'total_miles_saved': total_miles_saved,
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
        'cycle': 0
        }
        origin = "Mumbai, India"
        try:
            origin_coords = utils.get_coordinates(origin, utils.API_KEY)
            destination_coords = utils.get_coordinates(trip.destination, utils.API_KEY)
            distance = utils.great_circle_distance(origin_coords[0],origin_coords[1], destination_coords[0], destination_coords[1])
        except Exception as e:
                distance = 0  # Default to 0 if there's an error
                print(f"Error calculating distance: {e}")
        co2_emission = distance*emission_factors[transportation_instance.transport_type]*transportation_instance.co2_per_km
        trip.co2=co2_emission
        co2_saved = co2_emission
        for transport in transportation:
            if (transport.co2_per_km*distance*emission_factors[transport.transport_type]) > co2_emission:
                co2_saved = (transport.co2_per_km*distance*emission_factors[transport.transport_type]) - co2_emission
        trip.co2_saved=co2_saved if co2_saved!=co2_emission else 0

        user = request.user
        if hasattr(user, 'profile'):  # Assuming user profile has a `co2_saved` field
            user.profile.co2_saved = user.profile.co2_saved + trip.co2_saved
            user.profile.save()
        else:
            print("User profile or co2_saved field not found.")

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
    transportation = Transportation.objects.filter(destination=trip.destination).count()
    cost = "{:,.2f}".format(trip.total_cost)
    co2 = "{:,.2f}".format(trip.co2)
    co2_saved = "{:,.2f}".format(trip.co2_saved)
    saved = 1 if (trip.co2_saved!=0 or transportation==1) else 0
    return render(request, 'trip_success.html', {'trip': trip, "cost":cost, "co2": co2, 'co2_saved':co2_saved, "saved":saved})


def blog(request):
    return render(request, 'blog.html')

import requests
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import UploadedPlanTrip
from .forms import UploadedPlanTripForm

@login_required
def upload_plan_trip(request):
    if request.method == 'POST':
        form = UploadedPlanTripForm(request.POST, request.FILES)
        if form.is_valid():
            # Save the image instance
            uploaded_trip = form.save(commit=False)
            uploaded_trip.user = request.user
            uploaded_trip.save()

            # Fetch data from Picarta API
            picarta_api_url = "https://api.picarta.com/example-endpoint"  # Replace with actual endpoint
            headers = {'Authorization': '4RUX4AOFPACRMKF6CBFW'}
            response = requests.get(picarta_api_url)
            if response.status_code == 200:
                data = response.json()
                # Populate fields from API response
                uploaded_trip.destination_name = data.get('destination_name', 'Unknown')
                uploaded_trip.description = data.get('description', 'No description available.')
                uploaded_trip.country = data.get('country', 'Unknown')
                uploaded_trip.city = data.get('city', 'Unknown')
                uploaded_trip.eco_rating = data.get('eco_rating', 0)
                uploaded_trip.save()

            return redirect('uploaded_plan_trip')  # Redirect to the list page after saving

    else:
        form = UploadedPlanTripForm()
    return render(request, 'index.html', {'form': form})

@login_required
def uploaded_plan_trip(request):
    uploaded_trips = UploadedPlanTrip.objects.filter(user=request.user)
    return render(request, 'uploaded_plan_trip.html', {'uploaded_trips': uploaded_trips})


def travel_advisor(request):
    if request.method=='POST':
        source = request.POST.get('source')
        destination = request.POST.get('destination')
        try:
            origin_coords = utils.get_coordinates(source, utils.API_KEY)
            destination_coords = utils.get_coordinates(destination, utils.API_KEY)
            modes = ['car', 'bike','foot']
            context = {"routes": []}

            emission_factors = {
            "car": 150,      # grams of CO2 per km
            "bike": 30,      # grams of CO2 per km
            "walking": 0     # grams of CO2 per km
        }
                # Fetch routes for each mode
            for mode in modes:
                route = utils.get_route(origin_coords, destination_coords, profile=mode)
                context["routes"].append({
                        "mode": mode,
                        "distance": f"{route['distance']:.2f} km",
                        "time": f"{route['time']:.2f} minutes",
                        "co2_emission":f"{(route['distance']*emission_factors[mode]):.2f}"
                    })
        except Exception as e:
            context = {"error": str(e)}

        # Render template with context
        return render(request, 'travel_advisor.html', context)
    return render(request, 'travel_advisor.html')

import requests
from django.shortcuts import render, redirect

def plan_trip2(request):
    # Automatically fetch data
    # Replace 'YOUR_API_KEY' with a valid API key for a geolocation service
    geolocation_url = "https://api.opencagedata.com/geocode/v1/json"
    params = {
        "q": "48.8566,2.3522",  # Example coordinates (Paris, France); replace with logic if dynamic
        "key": "4RUX4AOFPACRMKF6CBFW",
    }

    response = requests.get(geolocation_url, params=params)
    if response.status_code == 200:
        data = response.json()
        city = data['results'][0]['components'].get('city', 'Unknown City')
        country = data['results'][0]['components'].get('country', 'Unknown Country')
        image_url = "https://via.placeholder.com/600x400.png?text=Your+Trip+Image"  # Replace with your image-fetching logic

        # Save the fetched values to the session
        request.session['image_url'] = image_url
        request.session['city'] = city
        request.session['country'] = country
    else:
        # Fallback if API fails
        request.session['image_url'] = "https://via.placeholder.com/600x400.png?text=Fallback+Image"
        request.session['city'] = "Fallback City"
        request.session['country'] = "Fallback Country"

    return render(request, 'plan_trip.html', {
        'image_url': request.session['image_url'],
        'city': request.session['city'],
        'country': request.session['country'],
    })



import requests
from django.shortcuts import render, redirect
from .models import UploadedPlanTrip
from django.contrib.auth.decorators import login_required
import requests

@login_required
def upload_trip(request):
    if request.method == 'POST':
        image = request.FILES.get('image')  # Fetch the uploaded image
        user = request.user

        # Picarta API endpoint and your API key
        picarta_api_url = "https://api.picarta.example.com/analyze"
        api_key = "4RUX4AOFPACRMKF6CBFW"

        # Sending the image to Picarta API
        headers = {'Authorization': f'Bearer {api_key}'}
        files = {'image': image.file}
        response = requests.post(picarta_api_url, headers=headers, files=files)

        if response.status_code == 200:
            data = response.json()  # Parse Picarta API response
            destination_name = data.get('destination_name', 'Unknown')
            description = data.get('description', '')
            country = data.get('country', '')
            city = data.get('city', '')
            eco_rating = data.get('eco_rating', 0)

            # Save the data into UploadedPlanTrip model
            UploadedPlanTrip.objects.create(
                user=user,
                image=image,
                destination_name=destination_name,
                description=description,
                country=country,
                city=city,
                eco_rating=eco_rating,
            )

            return redirect('uploaded_plan_trip.html')  # Redirect after success
        else:
            return render(request, 'index.html', {
                'error': 'Failed to fetch data from Picarta API. Please try again later.'
            })

    return render(request, 'index.html')


def eco_tips(request):
    return render(request, 'tipsNtricks.html')

def ecobot(request):
    return render(request, 'ChatbotWhite.html')
