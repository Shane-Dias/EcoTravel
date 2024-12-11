 # First, pip install picarta 
from picarta import Picarta

api_token = "4RUX4AOFPACRMKF6CBFW"
localizer = Picarta(api_token)

# Geolocate a local image worldwide
result = localizer.localize(img_path="./static/timessquare.jpg")
city = result['city']
country = result['ai_country']
print(city, country)
