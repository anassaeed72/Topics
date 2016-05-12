from proximity import ProximitySearch
import os
from history import*
from scan import*
import sys
from relays import get_relays
from geoip import geolite2
import stem.control
import ipgetter
from midpoint import midpointCalculator
from math import radians, cos, sin, asin, sqrt
import shutil
from UserURLHistory import getFetechableURLsFromPage
with stem.control.Controller.from_port() as controller:
    pass

# Get the ccomplete page including all src urls embedded in the page
def get_page(url, controller, circuit):
    hostname = url.split(".")[1]
    path = os.path.join(os.getcwd(), hostname)
    if (os.path.exists(path)):
        shutil.rmtree(path)
    os.mkdir(path)
    os.chdir(path)
    fd = open(hostname + ".html", "w")
    fd_read = open(hostname + ".html", "r")
    time_taken = scan(controller, circuit, url, 
        fd)
    fetchable = getFetechableURLsFromPage(fd_read.read())
    fetchable = list(set(fetchable))
    urls = map(convert_src_to_url, fetchable)
    query_parallel(urls)
# convert from for "src="xyz"" to xyz

def totalDistance(path):
    distance = 0
    for x in xrange(1, path):
        distance += haversine(path[x][0], path[x][1], path[x-1][0], path[x-1][1])
    return distance

def haversine(lon1, lat1, lon2, lat2):
    """
    Calculate the great circle distance between two points 
    on the earth (specified in decimal degrees)
    """
    # convert decimal degrees to radians 
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
    # haversine formula 
    dlon = lon2 - lon1 
    dlat = lat2 - lat1 
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a)) 
    km = 6367 * c
    return km

def convert_src_to_url(str):
    return str[5:len(str)-1]

def main():
    history = get_top_visited(get_history(), 10)
    controller.authenticate()
    relays = get_relays(controller)
    entry = relays[0];
    middle = relays[1];
    exit = relays[2];
    history[0] = 'yahoo.com'

    dest_Address =  geolite2.lookup(socket.gethostbyname(history[0]))
    if ()
    exit_prox = ProximitySearch(exit)
    exit_nodes = exit_prox.get_points_nearby(dest_Address.location, 2)
    myIP = ipgetter.myip();
    my_Address =  geolite2.lookup(socket.gethostbyname(myIP))
    # print my_Address

    # sys.exit()
    entry_prox = ProximitySearch(entry)
    entry_nodes = entry_prox.get_points_nearby(my_Address.location, 2)
    # print [entry[x] for x in entry_nodes]

    middleLocation = midpointCalculator(dest_Address.location, my_Address.location)
    middle_prox = ProximitySearch(middle)
    middle_nodes = middle_prox.get_points_nearby(middleLocation, 2)
    # print [middle[x] for x in middle_nodes]

    # print 'is oops?'
    path = [entry[entry_nodes[1]], middle[middle_nodes[1]], exit[exit_nodes[1]]]
    print path
    # sys.exit()

    circuit_id = controller.new_circuit(path, await_build = True)
    test = controller.get_circuit(circuit_id)
    test = controller.get_circuits() # Return a list of circuits
    path = test[0].path # Hardcoded to take the first path, change it later
    res_list = [controller.get_network_status(x[0]).address for x in path] # Get ip addresses from fingerprints
    locations = [geolite2.lookup(x) for x in res_list] # Do lookups

    print "\n ******************* \n"
    print test.path
    # sys.exit("exiting here")
    # print controller.get_circuit(circuit_id).path
    # sys.exit('In final, exiting program')
    url = 'https://www.' + history[0]
    print 'Accessing url: ' + url
    get_page(url, controller, test)
    sys.exit()


    # print history

    # temp_node = controller.get_network_statuses()
    # relay_fingerprints = [desc for desc in controller.get_network_statuses()]
    # for relays in relay_fingerprints:
    #     # if relays.exit_policy is not None:
    #     print  relays.exit_policy
        # sys.exit('Exiting here')
    # temp_node = controller.get_network_status('071B31EB66FE259AB37404DFD142BEDEB53B9056')
    # print temp_node.exit_policy


    # print entry
    # controller.authenticate()
    # all_circuits = controller.get_circuits()
    #
    # for circ in all_circuits:
    #     print circ.path
    #     if len(circ.path) < 3:
    #         continue
    #     try:
    #         time_taken = scan(controller, circ, 'https://www.torproject.org')
    #         print('%0.2f seconds' % (time_taken))
    #     except Exception as e:
    # 		print "im in final.py"
    # 		print "Error occured"


if __name__ == "__main__":
    main()
