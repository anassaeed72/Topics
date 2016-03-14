from geopy.geocoders import Nominatim
from geopy.distance import vincenty
import StringIO
import time
import io

import pycurl

import stem.control
import socks
import ftplib 
import telnetlib 
import urllib2
import sys
from stem import CircStatus
from stem.control import Controller
import itertools
from geoip import geolite2
from geopy.geocoders import Nominatim

geolocator = Nominatim()
EXIT_FINGERPRINT = '379FB450010D17078B3766C2273303C358C3A442'

SOCKS_PORT = 9050
CONNECTION_TIMEOUT = 10000  # timeout before we give up on a circuit
sockProxyIp = '103.246.87.147'
sockProxyPort = 34002

def query(url):
  """
  Uses pycurl to fetch a site using the proxy on the SOCKS_PORT.
  """
  output = io.BytesIO()

  curl = pycurl.Curl()
  curl.setopt( pycurl.URL, url )
  curl.setopt( pycurl.PROXY, sockProxyIp )
  curl.setopt( pycurl.PROXYPORT, sockProxyPort )
  curl.setopt( pycurl.PROXYTYPE, pycurl.PROXYTYPE_SOCKS5_HOSTNAME )
  curl.setopt(pycurl.CONNECTTIMEOUT, CONNECTION_TIMEOUT)
  temp = curl.getinfo(pycurl.PRIMARY_IP)
  print temp
  try:
    curl.perform()
    return output.getvalue()
  except pycurl.error as exc:
    raise ValueError("Unable to reach %s (%s)" % (url, exc))



locationLahore = geolocator.geocode("Lahore")
locationIslamabad = geolocator.geocode("Karachi")


newport_ri = (locationLahore.latitude, locationLahore.longitude)

cleveland_oh = (locationIslamabad.latitude, locationIslamabad.longitude)

# print(vincenty(newport_ri, cleveland_oh).miles)
query("https://www.google.com")

