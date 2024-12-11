def get_location(image_path):
     # First, pip install picarta 
    from picarta import Picarta

    api_token = "4RUX4AOFPACRMKF6CBFW"
    localizer = Picarta(api_token)

    # Geolocate a local image worldwide
    result = localizer.localize(img_path=image_path)
    return result

import requests

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
def calculate_route_distance(origin_coords, destination_coords, api_key, mode):
    url = f"https://api.geoapify.com/v1/routing?waypoints={origin_coords[0]},{origin_coords[1]}|{destination_coords[0]},{destination_coords[1]}&mode={mode}&apiKey={api_key}"
    response = requests.get(url)
    data = response.json()
    if 'features' in data and len(data['features']) > 0:
        distance_meters = data['features'][0]['properties']['distance']
        distance_km = distance_meters / 1000  # Convert to kilometers
        return distance_km
    else:
        raise ValueError("Could not calculate the route distance.")
