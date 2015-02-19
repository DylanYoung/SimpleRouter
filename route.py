from socket import (
			socket, AF_INET,
			SOCK_STREAM, SOL_SOCKET, 
			SO_REUSEADDR, gethostname
			)
from threading import Thread, Timer, Lock
from argparse import ArgumentParser
import os

ACCESS_ADDR = 'localhost'
PORT = 23456
FOUND = "FOUND\0\0\0\0"
NOTFOUND = "NOTFOUND\0"
RESERVED = -1
lock = Lock()

def parseargs():
	verbose = "verbose output"
	pars = ArgumentParser(
		prog='CacheHTTP',
	    fromfile_prefix_chars='<'
	)
	pars.add_argument(
		'-v','--verbose', 
		help=verbose,
		action='store_true'
	) 

	pars.add_argument(
		'--version', 
		action='version', 
		version='%(prog)s 2.0'
	)
	
	pars.add_argument(
		'--port', '-p',
		nargs='?',
		default=PORT,
		const=PORT
	)

	return pars.parse_args()

def serversocket(port):
	s = socket(AF_INET, SOCK_STREAM)
	s.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
	s.bind((ACCESS_ADDR,port))
	return s

class ConnectionHandler(Thread):
	def __init__(self, port = PORT, size = 255):
		self.server = serversocket(port)
		self.connections = {}
		self.free = {i for i in range(size)}
		self.connections[0] = RESERVED
		self.free.remove(0)
		self.__len__ = size

	def __repr__(self):
		return str(self.connections)

	def __str__(self):
		return str(self.connections)

	def __parse_message__(self, message):
		mtuple = message.split(":", 2)
		try: 
			mtuple[0] = int(mtuple[0])
			mtuple[1].trim()
		except ValueError as e:
			return -1
		return mtuple

	def __len__(self):
		return self.__len__

	def add(self, client):
		try:
			n = self.free.pop()
		except KeyError:
			print "Error: connection rejected"
			return
		client.send("n\r\n")
		self.connections[n] = client
		t = Thread(target=route, args=(self, client,n,))
		t.start()

	def remove(self,key):
		self.free.add(key);
		self.connections.pop(key, ()).close()

	def route(self, client, n):
		while 1:
			try:
				msg = client.recv(80)
				mtuple = __parse_message__(message)
				if mtuple == -1:
					client.send("Error: invalid message \"" + message + "\"")
				elif mtuple[0] < 1 or > len(self):
					client.send("Error: " + mtuple[0] + " not found"
				elif mtuple[0] == len(self):
					self.broadcast(message)
				else:
					if mtuple[1][0] == '0' and len(mtuple[1]) == 1:
						self.remove(mtuple[0]) 
					else: 
						msg = str(n) + ": " + mtuple[1]
						self.connections[mtuple[0]].send(msg)
			except:
				break
		self.remove(n)

	def broadcast(self, msg):
		for key, connection in self.connections.iteritems():
			connection.send(msg)

	def run(self):
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

	parse_args()
	handle = ConnectionHandler()
	handle.start()
	handle.join()

if __name__ == '__main__':  
	main()