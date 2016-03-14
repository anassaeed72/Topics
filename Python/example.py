import io
import pycurl

import stem.process

from stem.util import term

SOCKS_PORT = 7000

class Storage:
  def __init__(self):
      self.contents = ''
      self.line = 0

  def store(self, buf):
      self.line = self.line + 1
      self.contents = "%s%i: %s" % (self.contents, self.line, buf)

  def __str__(self):
      return self.contents

def query(url):
  """
  Uses pycurl to fetch a site using the proxy on the SOCKS_PORT.
  """

  outputHeader = Storage()
  outputBody = Storage()

  query = pycurl.Curl()
  query.setopt(pycurl.URL, url)
  query.setopt(pycurl.PROXY, 'localhost')
  query.setopt(pycurl.PROXYPORT, SOCKS_PORT)
  query.setopt(pycurl.PROXYTYPE, pycurl.PROXYTYPE_SOCKS5_HOSTNAME)
  # query.setopt(pycurl.HEADER, 1)
  query.setopt(pycurl.WRITEFUNCTION, outputBody.store)
  # query.setopt(pycurl.HEADERFUNCTION, outputHeader.store)

  try:
    query.perform()
    # query.close()
    # print "Reached here"
    print query.getinfo(query.SIZE_DOWNLOAD)
    print query.getinfo(query.TOTAL_TIME)
    query.close()
    return
  except pycurl.error as exc:
    return "Unable to reach %s (%s)" % (url, exc)


# Start an instance of Tor configured to only exit through Russia. This prints
# Tor's bootstrap information as it starts. Note that this likely will not
# work if you have another Tor instance running.

def print_bootstrap_lines(line):
  if "Bootstrapped " in line:
    print(term.format(line, term.Color.BLUE))


print(term.format("Starting Tor:\n", term.Attr.BOLD))

tor_process = stem.process.launch_tor_with_config(
  config = {
    'ControlPort': '9051',
    'SocksPort': str(SOCKS_PORT),
    'ExitNodes': '{us}',
  },
  init_msg_handler = print_bootstrap_lines,
)

print(term.format("\nChecking our endpoint:\n", term.Attr.BOLD))
query("https://www.google.com")
# print(term.format(query("https://www.google.com"), term.Color.BLUE))

tor_process.kill()  # stops tor
