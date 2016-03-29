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
from geopy.distance import vincenty

# url fileName Count

# Static exit for us to make 2-hop circuits through. Picking aurora, a
# particularly beefy one...
#
#   https://atlas.torproject.org/#details/379FB450010D17078B3766C2273303C358C3A442

# EXIT_FINGERPRINT = '379FB450010D17078B3766C2273303C358C3A442'

SOCKS_PORT = 9050
CONNECTION_TIMEOUT = 90  # timeout before we give up on a circuit
sockProxyIp = '103.246.87.147'
# sockProxyIp='127.0.0.1'
sockProxyPort = 34002
machineIp = ""
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
  curl.setopt( pycurl.PROXYTYPE, pycurl.PROXYTYPE_SOCKS5_HOSTNAME)
  print "check 6"
  curl.setopt(pycurl.CONNECTTIMEOUT, CONNECTION_TIMEOUT)
  print "check 7"
  curl.setopt(pycurl.WRITEFUNCTION, output.write)
  print "check 8"

  try:
    print "check 9"
    curl.perform()
    print "check 10"
    machineIp = curl.getinfo(pycurl.PRIMARY_IP)
    print "check 11"
    return output.getvalue()
  except pycurl.error as exc:
    print "check 12"
    raise ValueError("Unable to reach %s (%s)" % (url, exc))


def scan(controller, path):
  print "Tor Circuit Path"
  print path
  with open(sys.argv[2], 'a') as f:
    f.write("\n")
    mystring = ",".join(str(x) for x in path)
    f.write(mystring)

  print "Circuit Construction Started"
  circuit_id = controller.new_circuit(path, await_build = True)
  print "Circuit Construction Done"

  try:
    controller.set_conf('__LeaveStreamsUnattached', '1')  # leave stream management to us
    start_time = time.time()
    print "Query for Page Started"
    check_page = query(sys.argv[1])
    print "Query for Page Done"
  
    return time.time() - start_time
  finally:
    # controller.remove_event_listener(attach_stream)
    controller.reset_conf('__LeaveStreamsUnattached')

def getTupleFromCountry(country):
  locationFunction = geolocator.geocode(country)
  functionTuple = (locationFunction.latitude,locationFunction.longitude)
  return functionTuple

def calculateDistanceBetweenLocs(intialDistance, locationIntial, locationFinal):
  finalDistance = intialDistance + vincenty(locationIntial, locationFinal).miles
  return finalDistance
  
def writeGeoInfoToFile(geoInformation,fileObject):
  fileObject.write(geoInformation.country)
  fileObject.write(",")
  fileObject.write(geoInformation.continent)
  fileObject.write(",")
  fileObject.write(geoInformation.timezone)
  fileObject.write(",")
  fileObject.write(str(geoInformation.subdivisions))
  fileObject.write(",")
def writeCoordinatesToFile(coordinates,fileObject):
  fileObject.write(str(coordinates.latitude))
  fileObject.write(",")
  fileObject.write(str(coordinates.longitude))
def writeRelayInformation(relayObject,fileObject,otherLocatoin):
  writeGeoInfoToFile(relayObject,fileObject)
  locationOfRelay = geolocator.geocode(relayObject.country)    
  writeCoordinatesToFile(locationOfRelay,fileObject)
  relayTuple = getTupleFromCountry(relayObject.country)
  distanceBetweenRelays = calculateDistanceBetweenLocs(distanceBetweenRelays,locationOfRelay,otherLocatoin)
  fileObject.write(",")
  fileObject.write(str(distanceBetweenRelays))
  fileObject.write(",")
  return locationOfRelay


with stem.control.Controller.from_port() as controller:
  try:
    controller.authenticate("wireless")
  except stem.connection.PasswordAuthFailed:
    print("Unable to authenticate, password is incorrect")
  geolocator = Nominatim()
  matchSockProxy = geolite2.lookup(sockProxyIp)
  relay_information = controller.get_network_statuses()
  count = int(sys.argv[3])

  for oneRelay in relay_information:
    distanceBetweenRelays=0
    count = count +1
    if count >int(sys.argv[4]):
      sys.exit(1)
    middleRelay= next(itertools.islice(relay_information, count, count + 1))
    exitRelay= next(itertools.islice(relay_information, count+1, count + 2))
    try:
      time_taken = scan(controller, [oneRelay.fingerprint,middleRelay.fingerprint, exitRelay.fingerprint])
      print "After time"
      matchOneRelay = geolite2.lookup(oneRelay.address)
      matchMiddleRelay = geolite2.lookup(middleRelay.address)
      matchExitRelay = geolite2.lookup(exitRelay.address)
      matchMachine = geolite2.lookup(machineIp)
      machineTuple = getTupleFromCountry(matchMachine.country)
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
        locationOneRelay = writeRelayInformation(matchOneRelay,f,locationMachine)                
        writeGeoInfoToFile(matchMiddleRelay,f)
        locationMiddleRelay = geolocator.geocode(matchMiddleRelay.country)
        writeCoordinatesToFile(locationMiddleRelay,f)
        middleRelayTuple = getTupleFromCountry(matchMiddleRelay.country)
        distanceBetweenRelays = calculateDistanceBetweenLocs(distanceBetweenRelays,locationOneRelay,locationMiddleRelay)
        f.write(",")
        f.write(str(distanceBetweenRelays))
        f.write(",")
        



        writeGeoInfoToFile(matchExitRelay,f)
        locationExitRelay = geolocator.geocode(matchExitRelay.country)
        writeCoordinatesToFile(locationExitRelay,f)
        
        exitReplayTuple = getTupleFromCountry(matchExitRelay.country)
        distanceBetweenRelays = distanceBetweenRelays + vincenty(locationMiddleRelay, exitReplayTuple).miles
        
        f.write(",")
        f.write(str(distanceBetweenRelays))
        f.write(",")
       
        f.write(sockProxyIp)
        f.write(",")
        f.write(str(sockProxyPort))
        f.write(",")
        writeGeoInfoToFile(matchSockProxy,f)
        writeCoordinatesToFile(locationSockProxy,f)
        

      print('%s => %0.2f seconds' % (oneRelay.fingerprint, time_taken))
    except Exception as exc:
      print('Exception here => %s' % ( exc))
