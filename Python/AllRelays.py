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
from geoip import geolite2


with stem.control.Controller.from_port() as controller:
  controller.authenticate()

  relay_information = controller.get_network_statuses()
  for oneItem in relay_information:
    match = geolite2.lookup(oneItem.address)
    # print match.country
    with open(sys.argv[1], 'a') as f:
      f.write(oneItem.nickname)
      f.write(":")
      f.write(oneItem.fingerprint)
      f.write(":")
      f.write(str(oneItem.published))
      f.write(":")
      f.write(oneItem.address)
      f.write(":")
      f.write(str(oneItem.or_port))
      f.write(":")
      f.write(str(oneItem.dir_port))
      f.write(":")
      f.write(str(oneItem.flags))
      f.write(":")
      f.write(str(oneItem.version))
      f.write(":")
      f.write(str(oneItem.version_line))      
      f.write(":")
      f.write(match.country)
      f.write(":")
      f.write(match.continent)
      f.write(":")
      f.write(match.timezone)
      f.write(":")
      f.write(str(match.subdivisions))
      f.write("\n")
 
  



