from geopy.geocoders import Nominatim
from geopy.distance import vincenty
geolocator = Nominatim()
locationLahore = geolocator.geocode("Lahore")
locationIslamabad = geolocator.geocode("Karachi")


newport_ri = (locationLahore.latitude, locationLahore.longitude)

cleveland_oh = (locationIslamabad.latitude, locationIslamabad.longitude)

print(vincenty(newport_ri, cleveland_oh).miles)

