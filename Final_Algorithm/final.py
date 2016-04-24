from proximity import ProximitySearch
from history import*
from scan import scan
import sys
from relays import get_relays
from geoip import geolite2
import stem.control
import ipgetter
from midpoint import midpointCalculator
with stem.control.Controller.from_port() as controller:
    pass


def main():
    history = get_top_visited(get_history(), 1)
    # print history[0]
    # sys.exit()
    controller.authenticate()
    relays = get_relays(controller)
    entry = relays[0];
    middle = relays[1];
    exit = relays[2];

    history[0] = 'google.com.pk'

    dest_Address =  geolite2.lookup(socket.gethostbyname(history[0]))

    exit_prox = ProximitySearch(exit)

    exit_nodes = exit_prox.get_points_nearby(dest_Address.location, 2)

    # print [exit[x] for x in exit_nodes]

    myIP = ipgetter.myip();
    # print myIP

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
    print "\n ******************* \n"
    print test.path
    # sys.exit("exiting here")
    # print controller.get_circuit(circuit_id).path
    # sys.exit('In final, exiting program')
    url = 'https://www.' + history[0]
    print 'Accessing url: ' + url
    time_taken = scan(controller, test, url)
    print('%0.2f seconds' % (time_taken))
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
