import StringIO
import time
import sys
import pycurl

import stem.control

# Static exit for us to make 2-hop circuits through. Picking aurora, a
# particularly beefy one...
#
#   https://atlas.torproject.org/#details/379FB450010D17078B3766C2273303C358C3A442

# EXIT_FINGERPRINT = '379FB450010D17078B3766C2273303C358C3A442'
EXIT_FINGERPRINT = 'F983AC52963654F3A1EC3EC0AE899AF259225483'

SOCKS_PORT = 9050
CONNECTION_TIMEOUT = 30  # timeout before we give up on a circuit

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
    print "Starting Curl Perform"
    query.perform()
    print query.getinfo(pycurl.EFFECTIVE_URL)
    print "Curl Finished"
    return output.getvalue()
  except pycurl.error as exc:
    raise ValueError("Unable to reach %s (%s)" % (url, exc))


def scan(controller):
  """
  Fetch check.torproject.org through the given path of relays, providing back
  the time it took.
  """

  all_circuits = controller.get_circuits()
  # print all_circuits

  for curCircuit in all_circuits:
  # circuit_id = controller.new_circuit(path, await_build = True)
    print curCircuit.path
    # sys.exit("Stopping Program")
    def attach_stream(stream):
      if stream.status == 'NEW':
        controller.attach_stream(stream.id, curCircuit.id)
      else:
        print stream.status

    controller.add_event_listener(attach_stream, stem.control.EventType.STREAM)

    try:
      controller.set_conf('__LeaveStreamsUnattached', '1')  # leave stream management to us
      start_time = time.time()
      print "Check 1"
      check_page = query('https://www.google.com.pk/')
      print "Check 2"
      # if 'Congratulations. This browser is configured to use Tor.' not in check_page:
      #   raise ValueError("Request didn't have the right content")

      print "Check 3"
      return time.time() - start_time
    finally:
      controller.remove_event_listener(attach_stream)
      controller.reset_conf('__LeaveStreamsUnattached')


with stem.control.Controller.from_port() as controller:
  controller.authenticate()

  # relay_fingerprints = [desc.fingerprint for desc in controller.get_network_statuses()]
  try:
    time_taken = scan(controller)
    print('%0.2f seconds' % (time_taken))
  except Exception as exc:
    print "Error occured"
  # try:
  #     time_taken = scan(controller, [])
  #     print time_taken
  #     # print('%s => %0.2f seconds' % (fingerprint, time_taken))
  #   except Exception as exc:
  #     print('%s => %s' % (fingerprint, ex


  # while (len(relay_fingerprints) > 3):
  #   fingerprint = relay_fingerprints[:3]
  #   del relay_fingerprints[:3]
  #   try:
  #     time_taken = scan(controller, fingerprint)
  #     print('%s => %0.2f seconds' % (fingerprint, time_taken))
  #   except Exception as exc:
  #     print('%s => %s' % (fingerprint, exc))

  # for fingerprint in relay_fingerprints:
  #   print "Attempting now"
  #   try:
  #     time_taken = scan(controller, [fingerprint, EXIT_FINGERPRINT])
  #     print('%s => %0.2f seconds' % (fingerprint, time_taken))
  #   except Exception as exc:
  #     print('%s => %s' % (fingerprint, exc))
