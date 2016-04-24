import StringIO
import time
import sys
import pycurl

import stem.control

SOCKS_PORT = 9050
CONNECTION_TIMEOUT = 30  # timeout before we give up on a circuit
fd = open('original_tor.txt', 'w')


def query(url):
  """
  Uses pycurl to fetch a site using the proxy on the SOCKS_PORT.
  """

  output = StringIO.StringIO()

  query = pycurl.Curl()
  query.setopt(pycurl.URL, url)
  query.setopt(pycurl.PROXY, '127.0.0.1')
  query.setopt(pycurl.PROXYPORT, SOCKS_PORT)
  query.setopt(pycurl.PROXYTYPE, pycurl.PROXYTYPE_SOCKS5_HOSTNAME)
  query.setopt(pycurl.CONNECTTIMEOUT, CONNECTION_TIMEOUT)
  query.setopt(pycurl.WRITEFUNCTION, output.write)

  try:
    print "Starting Curl Perform"
    query.perform()
    print "Curl Finished"
    # fd.write(output.getvalue())
    return output.getvalue()
  except pycurl.error as exc:
    raise ValueError("Unable to reach %s (%s)" % (url, exc))


def scan(controller,curCircuit, url):
  # print all_circuits

# circuit_id = controller.new_circuit(path, await_build = True)
  # print curCircuit.path[0][0]
  # sys.exit("Stopping Program")

  def attach_stream(stream):
    if stream.status == 'NEW':
      controller.attach_stream(stream.id, curCircuit.id)
    # else:
    #   print stream.status

  controller.add_event_listener(attach_stream, stem.control.EventType.STREAM)

  try:
    controller.set_conf('__LeaveStreamsUnattached', '1')  # leave stream management to us
    start_time = time.time()
    print "Check 1"
    check_page = query(url)
    fd.write(check_page)
    print "Check 2"
    # if 'Congratulations. This browser is configured to use Tor.' not in check_page:
    #   raise ValueError("Request didn't have the right content")

    print "Check 3"
    return time.time() - start_time
  finally:
    print "In finally: scan.py"
    controller.remove_event_listener(attach_stream)
    controller.reset_conf('__LeaveStreamsUnattached')


# with stem.control.Controller.from_port() as controller:
#   controller.authenticate()

#   all_circuits = controller.get_circuits()

#   for curCircuit in all_circuits:
#     if curCircuit.path > 2:
#       print curCircuit.path
#       try:
#         time_taken = scan(controller,curCircuit, 'https://www.google.com.pk')
#         print('%0.2f seconds' % (time_taken))
#         sys.exit('Done once')
#       except Exception as exc:
#         print "im in scan.py"
#         print "Error occured"
