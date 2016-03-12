import StringIO
import time

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


# url fileName Count

# Static exit for us to make 2-hop circuits through. Picking aurora, a
# particularly beefy one...
#
#   https://atlas.torproject.org/#details/379FB450010D17078B3766C2273303C358C3A442

EXIT_FINGERPRINT = '379FB450010D17078B3766C2273303C358C3A442'

SOCKS_PORT = 9050
CONNECTION_TIMEOUT = 10000  # timeout before we give up on a circuit

def query(url):
  """
  Uses pycurl to fetch a site using the proxy on the SOCKS_PORT.
  """
  output = StringIO.StringIO()

  curl = pycurl.Curl()
  curl.setopt( pycurl.URL, url )
  curl.setopt( pycurl.PROXY, '188.120.228.106' )
  curl.setopt( pycurl.PROXYPORT, 1080 )
  curl.setopt( pycurl.PROXYTYPE, pycurl.PROXYTYPE_SOCKS5_HOSTNAME )
  curl.setopt(pycurl.CONNECTTIMEOUT, CONNECTION_TIMEOUT)

  try:
    curl.perform()
    return output.getvalue()
  except pycurl.error as exc:
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
    try:
      time_taken = scan(controller, [oneRelay.fingerprint,middleRelay.fingerprint, exitRelay.fingerprint])
      print "After time"
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
        
      print('%s => %0.2f seconds' % (oneRelay.fingerprint, time_taken))
    except Exception as exc:
      print('Exception => %s' % ( exc))