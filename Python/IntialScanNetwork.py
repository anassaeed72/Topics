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


# url fileName Count

# Static exit for us to make 2-hop circuits through. Picking aurora, a
# particularly beefy one...
#
#   https://atlas.torproject.org/#details/379FB450010D17078B3766C2273303C358C3A442

# EXIT_FINGERPRINT = '379FB450010D17078B3766C2273303C358C3A442'

SOCKS_PORT = 9050
CONNECTION_TIMEOUT = 10000  # timeout before we give up on a circuit
# sockProxyIp = '103.246.87.147'
sockProxyIp='127.0.0.1'
sockProxyPort = 9050
def query(url):
  """
  Uses pycurl to fetch a site using the proxy on the SOCKS_PORT.
  """
  output = io.BytesIO()
  print "check 1"
  curl = pycurl.Curl()
  print "check 2"
  curl.setopt( pycurl.URL, url )
  print "check 3"
  curl.setopt( pycurl.PROXY, sockProxyIp )
  print "check 4"
  curl.setopt( pycurl.PROXYPORT, sockProxyPort )
  print "check 5"
  curl.setopt( pycurl.PROXYTYPE, pycurl.PROXYTYPE_SOCKS5_HOSTNAME )
  print "check 6"
  curl.setopt(pycurl.CONNECTTIMEOUT, CONNECTION_TIMEOUT)
  print "check 7"
  curl.setopt(pycurl.WRITEFUNCTION, output.write)
  print "check 8"

  try:
    print "check 9"
    curl.perform()
    print "check 10"
    return output.getvalue()
  except pycurl.error as exc:
    print "check 11"
    raise ValueError("Unable to reach %s (%s)" % (url, exc))


def scan(controller, path):
  print "Tor Circuit Path"
  print path
  with open(sys.argv[2], 'a') as f:
    f.write("\n")
    mystring = ",".join(str(x) for x in path)
    f.write(mystring)
  """
  Fetch check.torproject.org through the given path of relays, providing back
  the time it took.
  """
  print "Circuit Construction Started"
  circuit_id = controller.new_circuit(path, await_build = True)
  print "Circuit Construction Done"

  try:
    controller.set_conf('__LeaveStreamsUnattached', '1')  # leave stream management to us
    start_time = time.time()
    print "Query for Page Started"
    check_page = query(sys.argv[1])
    print "Query for Page Done"
    # if 'Congratulations. This browser is configured to use Tor.' not in check_page:
      # raise ValueError("Request didn't have the right content")

    return time.time() - start_time
  finally:
    # controller.remove_event_listener(attach_stream)
    controller.reset_conf('__LeaveStreamsUnattached')


with stem.control.Controller.from_port() as controller:
  controller.authenticate()
  geolocator = Nominatim()
  matchSockProxy = geolite2.lookup(sockProxyIp)
  # locationSockProxy = geolocator.geocode(matchSockProxy.country)
  # relay_fingerprints = [desc.fingerprint for desc in controller.get_network_statuses()]
  relay_information = controller.get_network_statuses()
  # print relay_fingerprints
  count = int(sys.argv[3])
  for oneRelay in relay_information:
    count = count +1
    if count >int(sys.argv[4]):
      sys.exit(1)
    middleRelay= next(itertools.islice(relay_information, count, count + 1))
    exitRelay= next(itertools.islice(relay_information, count+1, count + 2))
	# location = geolocator.geocode("Lahore")
	# print((location.latitude, location.longitude))
    try:
      time_taken = scan(controller, [oneRelay.fingerprint,middleRelay.fingerprint, exitRelay.fingerprint])
      print "After time"
      matchOneRelay = geolite2.lookup(oneRelay.address)
      matchMiddleRelay = geolite2.lookup(middleRelay.address)
      matchExitRelay = geolite2.lookup(exitRelay.address)
      with open(sys.argv[2], 'a') as f:
        f.write(",")
        f.write(oneRelay.address)
        f.write(",")
        f.write(middleRelay.address)
        f.write(",")
        f.write(exitRelay.address)
        f.write(",")
        f.write(str(time_taken))
        f.write(",")
        f.write(str(count))
        f.write(",")
        f.write(matchOneRelay.country)
        f.write(",")
        f.write(matchOneRelay.continent)
        f.write(",")
        f.write(matchOneRelay.timezone)
        f.write(",")
        f.write(str(matchOneRelay.subdivisions))
        f.write(",")
        location = geolocator.geocode(matchOneRelay.country)
        f.write(str(location.latitude))
        f.write(",")
        f.write(str(location.longitude))
        f.write(",")
        f.write(matchMiddleRelay.country)
        f.write(",")
        f.write(matchMiddleRelay.continent)
        f.write(",")
        f.write(matchMiddleRelay.timezone)
        f.write(",")
        f.write(str(matchMiddleRelay.subdivisions))
        f.write(",")
        location = geolocator.geocode(matchMiddleRelay.country)
        f.write(str(location.latitude))
        f.write(",")
        f.write(str(location.longitude))
        f.write(",")
        f.write(matchExitRelay.country)
        f.write(",")
        f.write(matchExitRelay.continent)
        f.write(",")
        f.write(matchExitRelay.timezone)
        f.write(",")
        f.write(str(matchExitRelay.subdivisions))
        f.write(",")
        location = geolocator.geocode(matchExitRelay.country)
        f.write(str(location.latitude))
        f.write(",")
        f.write(str(location.longitude))
        f.write(",")
        f.write(sockProxyIp)
        f.write(",")
        f.write(str(sockProxyPort))
        f.write(",")
        f.write(matchSockProxy.country)
        f.write(",")
        f.write(matchSockProxy.continent)
        f.write(",")
        f.write(matchSockProxy.timezone)
        f.write(",")
        f.write(str(matchSockProxy.subdivisions))
        f.write(",")
        f.write(str(locationSockProxy.latitude))
        f.write(",")
        f.write(str(locationSockProxy.longitude))

      print('%s => %0.2f seconds' % (oneRelay.fingerprint, time_taken))
    except Exception as exc:
      print('Exception => %s' % ( exc))
