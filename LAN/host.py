import json

from PySide6 import QtCore
from PySide6 import QtNetwork


class Host(QtCore.QObject):
	messageReceived = QtCore.Signal(object, object)
	clientConnected = QtCore.Signal(object)
	clientDisconnected = QtCore.Signal(object)

	def __init__(self, host="0.0.0.0", port=55555, on_message=None,
				 on_connect=None, on_disconnect=None, parent=None):
		super().__init__(parent)
		self.host = host
		self.port = port
		self.on_message = on_message
		self.on_connect = on_connect
		self.on_disconnect = on_disconnect
		self.server = QtNetwork.QTcpServer(self)
		self.server.newConnection.connect(self._accept_clients)
		self.clients = {}
		self.buffers = {}

	def start(self):
		address = QtNetwork.QHostAddress(self.host)
		print(f"[LAN host] Opening TCP listener on {self.host}:{self.port}...")
		
		if not self.server.listen(address, self.port):
			print(f"[LAN host] Failed to open TCP listener: {self.server.errorString()}")
			raise OSError(self.server.errorString())
		
		self.port = self.server.serverPort()
		print(f"[LAN host] TCP listener ready on {self.host}:{self.port}")
		return self.server.serverAddress().toString(), self.port

	def _accept_clients(self):
		while self.server.hasPendingConnections():
			client_socket = self.server.nextPendingConnection()
			address = (client_socket.peerAddress().toString(), client_socket.peerPort())
			print(f"[LAN host] Accepted connection from {address[0]}:{address[1]}")
			self.clients[client_socket] = address
			self.buffers[client_socket] = bytearray()
            
			client_socket.readyRead.connect(lambda client=client_socket: self._read_messages(client))
			client_socket.disconnected.connect(lambda client=client_socket: self._remove_client(client))
			self.clientConnected.emit(address)
			
			if self.on_connect:
				self.on_connect(address)

	def _read_messages(self, client_socket):
		buffer = self.buffers.get(client_socket)
		if buffer is None:
			return
		buffer.extend(bytes(client_socket.readAll()))
		while b"\n" in buffer:
			line, _, remaining = buffer.partition(b"\n")
			buffer[:] = remaining
			if not line:
				continue
			try:
				message = json.loads(line.decode("utf-8"))
			except (json.JSONDecodeError, UnicodeDecodeError):
				continue
			address = self.clients.get(client_socket)
			self.messageReceived.emit(address, message)
			if self.on_message:
				self.on_message(address, message)

	def _remove_client(self, client_socket):
		address = self.clients.pop(client_socket, None)
		self.buffers.pop(client_socket, None)
		if address is None:
			return
		print(f"[LAN host] Client disconnected: {address[0]}:{address[1]}")
		self.clientDisconnected.emit(address)
		if self.on_disconnect:
			self.on_disconnect(address)

	def send(self, message, client=None):
		payload = json.dumps(message).encode("utf-8") + b"\n"
		if client is None:
			recipients = list(self.clients)
		elif client in self.clients:
			recipients = [client]
		else:
			recipients = [
				client_socket
				for client_socket, address in self.clients.items()
				if address == client
			]
		sent = 0
		
		for recipient in recipients:
			if recipient in self.clients and recipient.write(payload) >= 0:
				sent += 1
		return sent

	def close(self):
		print(f"[LAN host] Closing TCP listener on {self.host}:{self.port}")
		self.server.close()
		
		for client in list(self.clients):
			client.readyRead.disconnect()
			client.disconnected.disconnect()
			client.abort()
			
		self.clients.clear()
		self.buffers.clear()
