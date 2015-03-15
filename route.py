#!/usr/bin/env python

"""Route messages between clients. \
				Tested with Python 2.7.6"""
##### Imports #####
from threading import Thread
from sys import argv
from socket import (
			socket, AF_INET,
			SOCK_STREAM, SOL_SOCKET,
			SHUT_RDWR,
			SO_REUSEADDR, gethostname,
			)
from argparse import (
			ArgumentParser,
			ArgumentDefaultsHelpFormatter
			)
####################

#### (Magic) Defaults ####
ACCESS_ADDR = ''
PORT = 23456
BUFFSIZE = 2048
SIZE = 255
VERSION = '1.0'
##########################

####### Argument Parser #######
def parseargs(args):
	verbose = "verbose output"
	pars = ArgumentParser(
		formatter_class=ArgumentDefaultsHelpFormatter,
	    fromfile_prefix_chars='<',
	    description=__doc__
	)
	pars.add_argument(
		'PORT',
		nargs = '?',
		default=PORT,
		help='The port number for the server',
		type=int
	)
	pars.add_argument(
		'-v','--verbose',
		help=verbose,
		action='store_true'
	)
	pars.add_argument(
		'--version',
		action='version',
		version='%(prog)s ' + VERSION
	)
	pars.add_argument(
		'--size',
		type=int,
		metavar='N',
		choices=range(3,1023),
		default=SIZE,
		help="The maximum number N of clients to \
				accept (2 < N < 1024).\
				Note: one client is reserved."
	)

	pars.add_argument(
			'--buffer', '-b',
			type=int,
			metavar='M',
			choices=range(2048,10240),
			default=BUFFSIZE,
			help="The maximum size M of messages to \
					accept (2048 < M < 10240)"
	)
	return pars.parse_args(args)
####################################################

# Create a server socket
def serversocket(port):
	s = socket(AF_INET, SOCK_STREAM)
	s.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
	s.bind((ACCESS_ADDR,port))
	return s

# This class handles all routing
class ConnectionHandler:

	# Constructor
	def __init__(self, port = PORT, size = SIZE, verbose=False):
		self.server = serversocket(port)
		# Active connections
		self.connections = {}
		# Available addresses
		self.free = {i for i in range(1, size)}
		# Max addresses available
		self.size = size
		# Verbose output
		self.verbose = verbose

### Boiler plate ###
	def __repr__(self):
		return str(self.connections)

	def __str__(self):
		return str(self.connections)

	def __len__(self):
		return len(connections)

	def __contains__(self, key):
		return (key in self.connections)

	def __getitem__(self, key):
			return self.connections[key]

	def __setitem__(self, key, value):
		if key > 0 and key < self.size:
			self.connections[key] = value
		else:
			raise KeyError

	def __delitem__(self, key):
		# Pop the connection and mark address available
		self.free.add(key);
		c = self.connections.pop(key, None)

		if c is not None:
			# Connection exists
			if self.verbose:
				print "Removed address " + str(key) + ": " + str(c)
			try:
				# Close the client
				c[0].shutdown(SHUT_RDWR)
				c[0].close()
			except:
				# Client is already closed
				pass

	def __missing__(self, key):
		return None

	# Broadcast a teardown and close the server
	def __del__(self):
		self.teardown()
		self.server.close()

#####################

	# Parse message into target and string
	def __parse_msg__(self, msg):
		mtuple = msg.split(":", 1)
		try:
			mtuple[0] = int(mtuple[0])
			mtuple[1] = mtuple[1].strip()
		except ValueError:
			return -1
		if mtuple[0] not in self and mtuple[0] != self.size:
			mtuple[1] = -1
		return mtuple

	# Add a new client if possible
	def add(self, client):
		try:
			# Get connection address
			n = self.free.pop()
		except KeyError:
			# No addresses available
			client[0].send("Sorry. The router is full :(\r\n")
			client[0].close()
			if self.verbose:
				print "Error: connection rejected"
			return
		# Send address and add connection
		client[0].send(str(n)+"\r\n")
		self[n] = client
		if self.verbose:
			print "Client " + str(n) + " added: " + str(client)
		# Route the client requests
		t = Thread(target=self.route, args=(n,))
		t.start()


	# Receive and route messages from client at
	#  address n.
	#  Should be threaded to avoid blocking
	def route(self, n):
		part = ""
		while 1:
			try:

				msgs = self.connections[n][0].recv(BUFFSIZE)
				msgs = msg.split("\n")
				msgs[0] = part + msgs[0]
				if len(msgs) > 1:
					part = msgs[-1]
					msgs = msgs[0:-1]
				print msgs
				for msg in msgs:
					mtuple = self.__parse_msg__(msg)
					# invalid message format
					if mtuple == -1:
						msg = "Error: invalid message \"" + msg + "\""
						self.send(n, msg)
					# address not found
					elif mtuple[1] == -1:
						msg = "Error: " + str(mtuple[0]) + " not found"
						self.send(n, msg)
					# No Errors
					else:
						if mtuple[1] == '0':
							# Teardown request
							if mtuple[0] == self.size:
								self.teardown()
								return
							# Close request
							else:
								del self[mtuple[0]]
								if mtuple[0] == n: return
						else:
							# Broadcast request
							if mtuple[0] == self.size:
								self.broadcast(msg.strip())
							# Message request
							else:
								msg = ": ".join([str(n), mtuple[1]])
								self.send(mtuple[0], msg)
			except:
				# gracefully clean up upon any exceptions
				break
		del self[n]

	# Handle broadcast requests
	def broadcast(self, msg):
		if self.verbose: print "Broadcasting " + msg
		for key, connection in self.connections.iteritems():
			if self.verbose: print "Sending to " + str(connection)
			connection[0].send(msg + "\r\n")

	# Send msg to client at address to
	def send(self, to, msg):
		if self.verbose:
			print "Sending to " + str(to) + ": " + msg
		self[to][0].send(msg + "\r\n")

	# Perform teardowns
	def teardown(self):
		if self.verbose: print "Tearing down\r\n"
		for key in self.connections:
			del self[key]


	# Start listening and accepting clients
	# callable instance
	def __call__(self):
		self.server.listen(5)
		while 1:
			try:
				client = self.server.accept()
				self.add(client)
			except:
				# oops
				break
		del self



def main():

	# parse args
	args = parseargs(argv[1:])

	# Create connection handler
	handle = ConnectionHandler(port=args.PORT,
								size=args.size,
								verbose=args.verbose)
	# Accept connections
	handle()

if __name__ == '__main__':
	main()
