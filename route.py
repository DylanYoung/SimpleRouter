from socket import (
			socket, AF_INET,
			SOCK_STREAM, SOL_SOCKET, 
			SO_REUSEADDR, gethostname
			)
from threading import Thread, Timer, Lock
from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter
import os
import sys

ACCESS_ADDR = ''
PORT = 23456
FOUND = "FOUND\0\0\0\0"
NOTFOUND = "NOTFOUND\0"
RESERVED = -1
lock = Lock()

def parseargs(args):
	verbose = "verbose output"
	pars = ArgumentParser(
		formatter_class=ArgumentDefaultsHelpFormatter,
	    fromfile_prefix_chars='<',
	    description='Route messages between clients. Tested with Python 2.7.6'
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
		version='%(prog)s 0.1'
	)
	pars.add_argument(
		'--size',
		type=int,
		nargs=1,
		choices=(3,15,63,255,511,1023),
		default=255,
		help="The maximum number of clients to accept"
	)


	return pars.parse_args(args)

def serversocket(port):
	s = socket(AF_INET, SOCK_STREAM)
	s.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
	s.bind((ACCESS_ADDR,port))
	return s

class ConnectionHandler:
	def __init__(self, port = PORT, size = 255, verbose=False):
		self.server = serversocket(port)
		self.connections = {}
		self.free = {i for i in range(size)}
		self.free.remove(0)
		self.__len__ = size
		self.verbose = verbose

	def __repr__(self):
		return str(self.connections)

	def __str__(self):
		return str(self.connections)

	def __parse_message__(self, msg):
		mtuple = msg.split(":", 2)
		try: 
			mtuple[0] = int(mtuple[0])
			mtuple[1] = mtuple[1].strip(" ")
		except ValueError as e:
			return -1
		return mtuple

	def __len__(self):
		return len(connections)

	def add(self, client):
		try:
			n = self.free.pop()
		except KeyError:
			client[0].send("Sorry. The router is full.\r\n")
			client[0].close()
			print "Error: connection rejected"
			return
		client[0].send(str(n)+"\r\n")
		self.connections[n] = client
		if self.verbose:
			print "Client " + str(n) + " added: " + str(client)
		t = Thread(target=self.route, args=(client[0],n,))
		t.start()

	def remove(self,key):
		self.free.add(key);
		c = self.connections.pop(key, None)
		if c != None:
			if self.verbose:
				print "Removed address " + str(key) + ": " + str(c)
				print "Free addresses: " + str(self.free)
			c[0].close()

	def route(self, client, n):
		while 1:
			try:
				msg = client.recv(2048)
				mtuple = self.__parse_message__(msg)
				if mtuple == -1:
					client.send("Error: invalid message \"" + msg.strip() + "\"\r\n")
				elif mtuple[0] < 1 or mtuple[0] > self.__len__:
					print "Error: " + str(mtuple[0]) + " not found"
					client.send("Error: " + str(mtuple[0]) + " not found")
				elif mtuple[0] == self.__len__:
					self.broadcast(msg)
				else:
					if mtuple[1][0] == '0' and len(mtuple[1]) == 3:
						self.remove(mtuple[0]) 
						if mtuple[0] == n: return
					else: 
						msg = str(n) + ": " + mtuple[1]
						if self.verbose: print "Sending "+ msg
						self.connections[mtuple[0]][0].send(msg)
			except:
				break
		self.remove(n)

	def broadcast(self, msg):
		if self.verbose: print "Broadcasting " + msg.strip()
		for key, connection in self.connections.iteritems():
			if self.verbose: print "Sending to " + str(connection)
			connection[0].send(msg)

	def run(self):
		self.server.listen(5)
		while 1:
			client = self.server.accept()
			self.add(client)
		self.close()

	def close(self):
		for key in self.connections:
			self.remove(key)
		self.server.close()
		del(self)

def main():

	args = parseargs(sys.argv[1:])
	handle = ConnectionHandler(port=args.PORT, 
								size=args.size, 
								verbose=args.verbose)
	handle.run()

if __name__ == '__main__':  
	main()