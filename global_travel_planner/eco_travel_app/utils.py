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
api_key = "5b3ce3597851110001cf6248c3e5474dc5b64991afad8ceec07950da"

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

def chatbot():
    import google.generativeai as genai
    import time
    genai.configure(api_key='AIzaSyDv7RThoILjeXAryluncDRZ1QeFxAixR7Q')
    model = genai.GenerativeModel("gemini-1.5-flash")
    prompt = 'Hello'
    while(prompt!='exit'):
        prompt = input("Enter prompt: ")
        response = model.generate_content(prompt)
    return response

def get_route(lat1, lon1, lat2, lon2, mode):
#     Driving Modes:

# driving-car: Route for regular cars (automobiles).
# driving-hgv: Route for heavy goods vehicles (trucks), with consideration for vehicle restrictions (e.g., height, weight, cargo).
# driving-tractor: Route for tractors, designed for agricultural vehicles.
# Cycling Modes:

# cycling-regular: Route for regular cyclists (bicycles).
# cycling-mountain: Route optimized for mountain biking, focusing on rugged or off-road trails.
# Walking Modes:

# foot-walking: Route for pedestrians, considering footpaths and walking-friendly routes.
# Wheelchair Mode:

# wheelchair: Route optimized for wheelchair users, with an emphasis on accessible paths.
# Public Transport Modes:

# public_transport: Route using public transportation (buses, trams, trains, etc.).
# bus: Route using only buses.
    ORS_URL = "https://api.openrouteservice.org/v2/directions/driving-car"
    # Define the request parameters
    params = {
        "api_key": API_KEY,
        "start": f"{lat1},{lon1}",
        "end": f"{lat2},{lon2}"
    }

    # Send the GET request
    response = requests.get(ORS_URL, params=params)

    if response.status_code == 200:
        data = response.json()
        return data["features"][0]["geometry"]
    else:
        print("Error:", response.status_code, response.text)