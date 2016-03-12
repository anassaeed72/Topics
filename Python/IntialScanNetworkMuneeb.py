import StringIO
import time

import pycurl

import stem.control
import socks
import ftplib 
import telnetlib 
import urllib2


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
  curl.setopt( pycurl.URL, 'https://check.torproject.org/' )
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
  with open('fileMuneeb.csv', 'a') as f:
    mystring = ",".join(str(x) for x in path)
    f.write(mystring)
  """
  Fetch check.torproject.org through the given path of relays, providing back
  the time it took.
  """
  print "Circuit Construction Started"
  circuit_id = controller.new_circuit(path, await_build = True)
  print "Circuit Construction Done"

  # def attach_stream(stream):
  #   if stream.status == 'NEW':
  #     controller.attach_stream(stream.id, circuit_id)

  # controller.add_event_listener(attach_stream, stem.control.EventType.STREAM)

  try:
    controller.set_conf('__LeaveStreamsUnattached', '1')  # leave stream management to us
    start_time = time.time()
    print "Query for Page Started"
    check_page = query('https://www.google.com/')
    print "Query for Page Done"
    # if 'Congratulations. This browser is configured to use Tor.' not in check_page:
      # raise ValueError("Request didn't have the right content")

    return time.time() - start_time
  finally:
    # controller.remove_event_listener(attach_stream)
    controller.reset_conf('__LeaveStreamsUnattached')


with stem.control.Controller.from_port() as controller:
  controller.authenticate()

  relay_fingerprints = [desc.fingerprint for desc in controller.get_network_statuses()]
  # print relay_fingerprints
  count = 0
  for fingerprint in relay_fingerprints:
    count = count +1
    if count <1000:
    	continue
    print "Current fingerprint "+ fingerprint
    try:
      time_taken = scan(controller, [fingerprint,relay_fingerprints[count], EXIT_FINGERPRINT])
      print "After time"
      with open('fileMuneeb.csv', 'a') as f:
        f.write(",")
        f.write(str(time_taken))
        f.write(",")
        f.write(str(count))
        f.write("\n")
      print('%s => %0.2f seconds' % (fingerprint, time_taken))
    except Exception as exc:
      print('%s => %s' % (fingerprint, exc))