def query_head(url):
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
  query.setopt(pycurl.HEADER, True)
  query.setopt(pycurl.NOBODY, True)
  try:
    print "Starting Curl Perform"
    query.perform()
    print "Curl Finished"
    # fd.write(output.getvalue())
    return output.getvalue()
  except pycurl.error as exc:
    print("Unable to reach ", url)
    return -1

def scan_head(controller,curCircuit, url):
  def attach_stream(stream):
    if stream.status == 'NEW':
      controller.attach_stream(stream.id, curCircuit.id)
  controller.add_event_listener(attach_stream, stem.control.EventType.STREAM)
  try:
    controller.set_conf('__LeaveStreamsUnattached', '1')  # leave stream management to us
    start_time = time.time()
    check_page = query_head(url)
    if check_page == -1:
      return -1
    print check_page
    return time.time() - start_time
  finally:
    controller.remove_event_listener(attach_stream)
    controller.reset_conf('__LeaveStreamsUnattached')