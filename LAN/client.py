import json

from PySide6 import QtCore
from PySide6 import QtNetwork


class Client(QtCore.QObject):
	messageReceived = QtCore.Signal(object)
	connected = QtCore.Signal()
	disconnected = QtCore.Signal()

	def __init__(self, host, port=55555, on_message=None, on_disconnect=None,
				 parent=None):
		super().__init__(parent)
		self.host = host
		self.port = port
		self.on_message = on_message
		self.on_disconnect = on_disconnect
		self.socket = QtNetwork.QTcpSocket(self)
		self.buffer = bytearray()
		self.socket.connected.connect(self.connected.emit)
		self.socket.readyRead.connect(self._read_messages)
		self.socket.disconnected.connect(self._handle_disconnected)

	def connect(self):
		print(f"[LAN client] Connecting to {self.host}:{self.port}...")
		self.socket.connectToHost(self.host, self.port)

	def _read_messages(self):
		self.buffer.extend(bytes(self.socket.readAll()))
		while b"\n" in self.buffer:
			line, _, remaining = self.buffer.partition(b"\n")
			self.buffer[:] = remaining
			if not line:
				continue
			try:
				message = json.loads(line.decode("utf-8"))
			except (json.JSONDecodeError, UnicodeDecodeError):
				continue
			self.messageReceived.emit(message)
			if self.on_message:
				self.on_message(message)

	def _handle_disconnected(self):
		print(f"[LAN client] Disconnected from {self.host}:{self.port}")
		self.buffer.clear()
		self.disconnected.emit()
		if self.on_disconnect:
			self.on_disconnect()

	def send(self, message):
		if self.socket.state() != QtNetwork.QAbstractSocket.SocketState.ConnectedState:
			raise ConnectionError("Client is not connected")

		print(f"[LAN client] Sending {message.get('type', 'message')} message")
		payload = json.dumps(message).encode("utf-8") + b"\n"
		if self.socket.write(payload) < 0:
			raise ConnectionError(self.socket.errorString())

	def close(self):
		print(f"[LAN client] Closing connection to {self.host}:{self.port}")
		self.socket.connected.disconnect()
		self.socket.readyRead.disconnect()
		self.socket.disconnected.disconnect()
		self.socket.abort()
