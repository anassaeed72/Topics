import StringIO
import time
import sys
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
import ipgetter

# Static exit for us to make 2-hop circuits through. Picking aurora, a
# particularly beefy one...
#
#   https://atlas.torproject.org/#details/379FB450010D17078B3766C2273303C358C3A442

# EXIT_FINGERPRINT = '379FB450010D17078B3766C2273303C358C3A442'
EXIT_FINGERPRINT = 'F983AC52963654F3A1EC3EC0AE899AF259225483'

SOCKS_PORT = 9050
CONNECTION_TIMEOUT = 100  # timeout before we give up on a circuit
distanceBetweenRelays = 0
def query(url):
  """
  Uses pycurl to fetch a site using the proxy on the SOCKS_PORT.
  """

  output = StringIO.StringIO()

  query = pycurl.Curl()
  query.setopt(pycurl.URL, url)
  query.setopt(pycurl.PROXY, 'localhost')
  query.setopt(pycurl.PROXYPORT, SOCKS_PORT)
  query.setopt(pycurl.PROXYTYPE, pycurl.PROXYTYPE_SOCKS5_HOSTNAME)
  query.setopt(pycurl.CONNECTTIMEOUT, CONNECTION_TIMEOUT)
  query.setopt(pycurl.WRITEFUNCTION, output.write)

  try:
    # print "Starting Curl Perform"
    query.perform()
    # print query.getinfo(pycurl.EFFECTIVE_URL)

    # print query.getinfo(pycurl.PRIMARY_IP)
    # print "Curl Finished"
    return output.getvalue()
  except pycurl.error as exc:
    print "Raising unable to reach error"
    raise ValueError("Unable to reach %s (%s)" % (url, exc))


def scan(controller,curCircuit):
  """
  Fetch check.torproject.org through the given path of relays, providing back
  the time it took.
  """

  def attach_stream(stream):
    if stream.status == 'NEW':
      controller.attach_stream(stream.id, curCircuit.id)
    else:
      print stream.status

  controller.add_event_listener(attach_stream, stem.control.EventType.STREAM)

  try:
    controller.set_conf('__LeaveStreamsUnattached', '1')  # leave stream management to us
    start_time = time.time()
    # print "Check 1"
    check_page = query(sys.argv[1])

    # print "Check 3"
    return time.time() - start_time
  finally:
    controller.remove_event_listener(attach_stream)
    controller.reset_conf('__LeaveStreamsUnattached')

def getTupleFromCountry(locationFunction):
  # print "check 1"
  # print "check 2"
  # print locationFunction.location[0]
  # print locationFunction
  functionTuple = (locationFunction.location[0],locationFunction.location[0])
  # print "check 3"
  return functionTuple

def getTupleOther(locationFunction):
  functionTuple = (locationFunction.longitude,locationFunction.latitude)
  return functionTuple
def calculateDistanceBetweenLocs(intialDistance, locationIntial, locationFinal):
  finalDistance = intialDistance + vincenty(getTupleFromCountry(locationIntial),getTupleOther( locationFinal)).miles
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
  # print "in writeRelayInformation"
  global distanceBetweenRelays
  writeGeoInfoToFile(relayObject,fileObject)
  writeCoordinatesToFile(locationOfRelay,fileObject)
  # print "check 4"
  distanceBetweenRelays = calculateDistanceBetweenLocs(distanceBetweenRelays,relayObject,otherLocatoin)
  # print "check 5"
  fileObject.write(",")
  fileObject.write(str(distanceBetweenRelays))
  # print "Check 6"
  fileObject.write(",")
  return locationOfRelay

def getobj(controller,cirObject):
  # print "Inside Function"
  # print cirObject[0]
  
  try:
    temp = controller.get_network_status(cirObject[0])
  except ValueError as exc:
    sys.exit("Error in getting network object")
  except stem.DescriptorUnavailable as exc:
    sys.exit("Error in getting network object2")
  except stem.ControllerError as exc:
    sys.exit("Error in getting network object3")
  except Exception as exc:
    print exc
    sys.exit("Something else")

  # print "Got object"
  # print tempErr
  return temp

with stem.control.Controller.from_port() as controller:

  # myIP = ipgetter.myip();

  try:
    controller.authenticate()
  except stem.connection.PasswordAuthFailed:
    sys.exit("Unable to authenticate, password is incorrect")

  geolocator = Nominatim()
  all_circuits = controller.get_circuits()
  locationMachine = locationOfRelay = geolocator.geocode("Lahore Pakistan")
  distanceBetweenRelays = 0
  matchMachine = geolocator.geocode("Lahore Pakistan")
  for curCircuit in all_circuits:
    if (len(curCircuit.path) != 3):
      continue
    distanceBetweenRelays = 0
    # print curCircuit.path
    # sys.exit("Terminating here")

    try:
      time_taken = scan(controller,curCircuit)

      # print "Reached here"

      # print "\nPrinting Circuit Now \n"
      # print curCircuit.path
      # print "\nEnd of Circuit \n"
      # print getobjAddress(controller,curCircuit.path[0])
      oneRelay = getobj(controller,curCircuit.path[0])
      middleRelay = getobj(controller,curCircuit.path[1])
      exitRelay = getobj(controller,curCircuit.path[2])

      matchOneRelay = geolite2.lookup(oneRelay.address)
      matchMiddleRelay = geolite2.lookup(middleRelay.address)
      matchExitRelay = geolite2.lookup(exitRelay.address)
      
      # # print machineIp
      # print "Iam here"
      # # print sys.argv
      # matchMachine = geolite2.lookup(sys.argv[3])
      # print matchMachine.country
      # print "Reached here 11"
      # # sys.exit("Terminating here1")
      # machineTuple = getTupleFromCountry(matchMachine.country)
      
      # print "Reached here 2"
      # # sys.exit("Terminating here2")

      with open(sys.argv[2], 'a') as f:
        # print "Reached here 5"
        f.write("\n")      
        f.write(",")
        f.write(oneRelay.address)
        f.write(",")
        f.write(middleRelay.address)
        f.write(",")
        f.write(exitRelay.address)
        f.write(",")
        f.write(str(time_taken))
        f.write(",")
 
        # print "Reached here 6"
        locationTemp = writeRelayInformation(matchOneRelay,f,matchMachine )
        # print "Reached here 7"
        locationTemp = writeRelayInformation(matchMiddleRelay,f,locationTemp)
        # print "Reached here 8"
        locationTemp = writeRelayInformation(matchExitRelay,f,locationTemp)
        # print "Reached here 3"

      #   locationOneRelay = writeRelayInformation(matchOneRelay,f,locationMachine)   
      #   writeGeoInfoToFile(matchMiddleRelay,f)
      #   locationMiddleRelay = geolocator.geocode(matchMiddleRelay.country)
      #   writeCoordinatesToFile(locationMiddleRelay,f)
      #   middleRelayTuple = getTupleFromCountry(matchMiddleRelay.country)
      #   distanceBetweenRelays = calculateDistanceBetweenLocs(distanceBetweenRelays,locationOneRelay,locationMiddleRelay)
      #   f.write(",")
        f.write(sys.argv[1])
        f.write(",")

      #   print "Reached here 4"

      #   writeGeoInfoToFile(matchExitRelay,f)
      #   locationExitRelay = geolocator.geocode(matchExitRelay.country)
      #   writeCoordinatesToFile(locationExitRelay,f)

      #   print "Reached here 5"
        
      #   exitReplayTuple = getTupleFromCountry(matchExitRelay.country)
      #   distanceBetweenRelays = distanceBetweenRelays + vincenty(locationMiddleRelay, exitReplayTuple).miles
        
      #   f.write(",")
      #   f.write(str(distanceBetweenRelays))
      #   f.write(",")
      # writeCoordinatesToFile(locationSockProxy,f)       
      #   f.write(sockProxyIp)
      #   f.write(",")
      #   f.write(str(sockProxyPort))
      #   f.write(",")
      #   writeGeoInfoToFile(matchSockProxy,f)
      #   writeCoordinatesToFile(locationSockProxy,f)


      # print('%0.2f seconds' % (time_taken))
    except Exception as exc:
      print exc
      continue
      # sys.exit("Error occured")
