# from proximity import ProximitySearch
# from history import*
from scan import scan
import sys
from relays import get_relays
import stem.control
with stem.control.Controller.from_port() as controller:
    pass


def main():
    controller.authenticate()
    relays = get_relays(controller)
    entry = relays[0];
    middle = relays[1];
    exit = relays[2];
    print middle

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
