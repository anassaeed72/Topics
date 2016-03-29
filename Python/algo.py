import StringIO
import time
import pycurl
import stem.control
import sys
import string
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

	print len(relay_fingerprints)

	entry_guards = [desc for desc in relay_fingerprints if if_guard(desc.flags)]

	print len(entry_guards)

	exit_nodes = [desc for desc in relay_fingerprints if if_exit(desc.flags)]

	print len(exit_nodes)

	middle_nodes = [desc for desc in relay_fingerprints if desc not in set(exit_nodes) and desc not in set(entry_guards)]

	print len(middle_nodes)

	entry_trie = datrie.Trie(string.printable)
	middle_trie = datrie.Trie(string.printable)
	exit_trie = datrie.Trie(string.printable)

	insert_in_trie(entry_guards,entry_trie)
	insert_in_trie(middle_nodes,middle_trie)
	insert_in_trie(exit_nodes,exit_trie)

	# print trie.has_keys_with_prefix(u'123')
	# if u'1234' in trie:
	# 	print "True"
	# else:
	# 	print "False"
