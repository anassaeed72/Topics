import StringIO
import time
import pycurl
import stem.control
import sys
import string
from geoip import geolite2
import datrie

def determine(flags):
	if ('Fast' and 'Stable' and 'Running' and 'Stable' and 'Valid') in flags:
		return True
	else:
		return False

def if_guard(flags):
	if 'Guard' in flags:
		return True
	else:
		return False

def if_exit(flags):
	if 'Exit' in flags:
		return True
	else:
		return False

def if_middle(flags):
	if 'Guard' not in flags and 'Exit' not in flags:
		return True
	else:
		return False

def insert_in_trie(relay_list,trie):
	for relay in relay_list:
		trie[relay.address] = relay.fingerprint

with stem.control.Controller.from_port() as controller:
	controller.authenticate()

	relay_fingerprints = [desc for desc in controller.get_network_statuses() if determine(desc.flags)]

	# print len(relay_fingerprints)

	entry_guards = [desc for desc in relay_fingerprints if if_guard(desc.flags)]

	print len(entry_guards)

	exit_nodes = [desc for desc in relay_fingerprints if if_exit(desc.flags)]

	print len(exit_nodes)

	middle_nodes = [desc for desc in relay_fingerprints if desc not in set(exit_nodes) and desc not in set(entry_guards)]

	print len(middle_nodes)

	entry_dict = {}
	middle_dict = {}
	exit_dict = {}

	# counter = 0
	for relay in entry_guards:
		# print relay.address
		my_Address = geolite2.lookup(relay.address)
		# print my_Address.location
		if my_Address is not None:
			entry_dict[geolite2.lookup(relay.address).location] = relay.fingerprint
		# else:
		# 	counter = counter + 1

	for relay in middle_nodes:
		# print relay.address
		my_Address = geolite2.lookup(relay.address)
		# print my_Address.location
		if my_Address is not None:
			middle_dict[geolite2.lookup(relay.address).location] = relay.fingerprint

	for relay in exit_nodes:
		# print relay.address
		my_Address = geolite2.lookup(relay.address)
		# print my_Address.location
		if my_Address is not None:
			exit_dict[geolite2.lookup(relay.address).location] = relay.fingerprint

	# print counter
	# entry_trie = datrie.Trie(string.printable)
	# middle_trie = datrie.Trie(string.printable)
	# exit_trie = datrie.Trie(string.printable)

	# insert_in_trie(entry_guards,entry_trie)
	# insert_in_trie(middle_nodes,middle_trie)
	# insert_in_trie(exit_nodes,exit_trie)

# Step 3
	middle_trie = datrie.Trie(string.printable)
	insert_in_trie(middle_nodes,middle_trie)

	temp_exit_nodes = exit_nodes[:5]

	temp_exit_nodes = [desc.address for desc in temp_exit_nodes] # Change it later

	print temp_exit_nodes
