def get_location(image_path):
     # First, pip install picarta 
    from picarta import Picarta

    api_token = "4RUX4AOFPACRMKF6CBFW"
    localizer = Picarta(api_token)

    # Geolocate a local image worldwide
    result = localizer.localize(img_path=image_path)
    return result

import requests, math


# Geoapify API Key
API_KEY = "fabe86e749c44aa2a8ae60c68c2e3c6f"

# Function to get coordinates from Geoapify Geocoding API
def get_coordinates(location, api_key):
    url = f"https://api.geoapify.com/v1/geocode/search?text={location}&apiKey={api_key}"
    response = requests.get(url)
    data = response.json()
    if data['features']:
        coords = data['features'][0]['geometry']['coordinates']
        return coords[1], coords[0]  # Return latitude, longitude
    else:
        raise ValueError(f"Could not find coordinates for location: {location}")

# Function to calculate route distance using Geoapify Route API
def great_circle_distance(lat1, lon1, lat2, lon2):
    # Convert degrees to radians
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    
    # Haversine formula
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat / 2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    
    # Earth radius in kilometers
    R = 6371.0
    distance = R * c
    return distance

def populate_co2_emitted(apps, schema_editor):
    Transportation = apps.get_model('eco_travel_app', 'Transportation')
    for transportation in Transportation.objects.all():
        transportation.co2_emitted = 0.0  # Default value as a float
        transportation.save()