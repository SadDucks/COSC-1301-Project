import json;
import ipaddress;
from pathlib import Path;

import time;
import uuid;

from PySide6 import QtCore;
from PySide6 import QtGui;
from PySide6 import QtMultimedia;
from PySide6 import QtNetwork;
from PySide6 import QtWidgets;

from LAN.client import Client;
from LAN.host import Host;

from Deck import Combat;
from Deck.cards import attackCard, prizeCard, supportCard;
from Player.game import game;
from Scenes.Gameplay import visualHand;

class multiplayerSetup(QtWidgets.QWidget):
    discoveryPort = 55556;
    refreshInterval = 5000;

    def __init__(self, config=None, windowRef=None):
        super().__init__();
        self.config = config;
        self.windowRef = windowRef;
        self.hostServer = None;
        self.client = None;
        self.discoverySocket = None;
        self.sessionId = None;
        self.games = {};
        self.connectedPlayers = {};

        self.setStyleSheet(
            "QWidget { background-color: #173b27; color: white; }"
            "QPushButton { background-color: #34533d; color: white; "
            "border: 1px solid #d9c98b; border-radius: 4px; padding: 8px 18px; }"
            "QPushButton:hover { background-color: #456b50; }"
            "QListWidget { background-color: #20372a; border: 1px solid #71896e; }"
        );

        self.pages = QtWidgets.QStackedWidget(self);
        self.pages.addWidget(self._createModePage());
        self.pages.addWidget(self._createJoinPage());
        self.pages.addWidget(self._createHostPage());

        layout = QtWidgets.QVBoxLayout(self);
        layout.addWidget(self.pages);

        self.refreshTimer = QtCore.QTimer(self);
        self.refreshTimer.setInterval(self.refreshInterval);
        self.refreshTimer.timeout.connect(self._refreshGames);

        self.connectionTimeout = QtCore.QTimer(self);
        self.connectionTimeout.setSingleShot(True);
        self.connectionTimeout.setInterval(10000);
        self.connectionTimeout.timeout.connect(self._connectionTimedOut);

    def _createModePage(self):
        page = QtWidgets.QWidget();
        layout = QtWidgets.QVBoxLayout(page);
        layout.addStretch();

        title = QtWidgets.QLabel("Multiplayer");
        title.setStyleSheet("font-size: 28px; font-weight: bold;");
        title.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter);
        layout.addWidget(title);

        prompt = QtWidgets.QLabel("Would you like to host or join a game?");
        prompt.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter);
        layout.addWidget(prompt);

        hostButton = QtWidgets.QPushButton("Host a Game");
        hostButton.clicked.connect(self._startHosting);
        layout.addWidget(hostButton, 0, QtCore.Qt.AlignmentFlag.AlignHCenter);

        joinButton = QtWidgets.QPushButton("Join a Game");
        joinButton.clicked.connect(self._startJoining);
        layout.addWidget(joinButton, 0, QtCore.Qt.AlignmentFlag.AlignHCenter);

        backButton = QtWidgets.QPushButton("Back to Main Menu");
        backButton.clicked.connect(self._returnToMenu);
        layout.addWidget(backButton, 0, QtCore.Qt.AlignmentFlag.AlignHCenter);
        layout.addStretch();
        return page;

    def _createJoinPage(self):
        page = QtWidgets.QWidget();
        layout = QtWidgets.QVBoxLayout(page);

        title = QtWidgets.QLabel("Join a Game");
        title.setStyleSheet("font-size: 24px; font-weight: bold;");
        title.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter);
        layout.addWidget(title);

        self.joinStatus = QtWidgets.QLabel("Searching your local network...");
        self.joinStatus.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter);
        layout.addWidget(self.joinStatus);

        self.joinNetworkInfo = QtWidgets.QLabel();
        self.joinNetworkInfo.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter);
        self.joinNetworkInfo.setWordWrap(True);
        layout.addWidget(self.joinNetworkInfo);

        self.gameList = QtWidgets.QListWidget();
        self.gameList.itemDoubleClicked.connect(self._joinSelectedGame);
        layout.addWidget(self.gameList, 1);

        buttons = QtWidgets.QHBoxLayout();
        joinButton = QtWidgets.QPushButton("Join Selected Game");
        joinButton.clicked.connect(lambda: self._joinSelectedGame());
        buttons.addWidget(joinButton);

        backButton = QtWidgets.QPushButton("Back");
        backButton.clicked.connect(self._showModePage);
        buttons.addWidget(backButton);
        layout.addLayout(buttons);
        return page;

    def _createHostPage(self):
        page = QtWidgets.QWidget();
        layout = QtWidgets.QVBoxLayout(page);

        title = QtWidgets.QLabel("Hosted Game");
        title.setStyleSheet("font-size: 24px; font-weight: bold;");
        title.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter);
        layout.addWidget(title);

        self.hostStatus = QtWidgets.QLabel("Starting game session...");
        self.hostStatus.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter);
        layout.addWidget(self.hostStatus);

        self.hostNetworkInfo = QtWidgets.QLabel();
        self.hostNetworkInfo.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter);
        self.hostNetworkInfo.setWordWrap(True);
        layout.addWidget(self.hostNetworkInfo);

        self.playerList = QtWidgets.QListWidget();
        layout.addWidget(self.playerList, 1);

        backButton = QtWidgets.QPushButton("Stop Hosting");
        backButton.clicked.connect(self._showModePage);
        layout.addWidget(backButton, 0, QtCore.Qt.AlignmentFlag.AlignHCenter);
        return page;

    def _prepareDiscoverySocket(self, port):
        print(f"[LAN lobby] Opening UDP discovery socket on port {port or 'dynamic'}...")
        self.discoverySocket = QtNetwork.QUdpSocket(self);
        self.discoverySocket.readyRead.connect(self._readDiscoveryPackets);
        address = QtNetwork.QHostAddress(
            QtNetwork.QHostAddress.SpecialAddress.AnyIPv4
        );
        flags = (
            QtNetwork.QAbstractSocket.BindFlag.ShareAddress
            | QtNetwork.QAbstractSocket.BindFlag.ReuseAddressHint
        );
        if not self.discoverySocket.bind(address, port, flags):
            error = self.discoverySocket.errorString();
            print(f"[LAN lobby] Failed to open UDP discovery socket: {error}");
            self.discoverySocket.deleteLater();
            self.discoverySocket = None;
            raise OSError(f"Could not start LAN discovery: {error}");
        print(
            f"[LAN lobby] UDP discovery socket bound to port "
            f"{self.discoverySocket.localPort()}"
        );

    @staticmethod
    def _getNetworkInfo():
        networks = [];
        requiredFlags = (
            QtNetwork.QNetworkInterface.InterfaceFlag.IsUp
            | QtNetwork.QNetworkInterface.InterfaceFlag.IsRunning
        );
        for interface in QtNetwork.QNetworkInterface.allInterfaces():
            flags = interface.flags();
            if (
                flags & requiredFlags != requiredFlags
                or flags & QtNetwork.QNetworkInterface.InterfaceFlag.IsLoopBack
            ):
                continue;

            for entry in interface.addressEntries():
                address = entry.ip();
                netmask = entry.netmask();
                if (
                    address.protocol()
                    != QtNetwork.QAbstractSocket.NetworkLayerProtocol.IPv4Protocol
                    or netmask.protocol()
                    != QtNetwork.QAbstractSocket.NetworkLayerProtocol.IPv4Protocol
                ):
                    continue;

                ipAddress = ipaddress.IPv4Address(address.toIPv4Address());
                network = ipaddress.IPv4Network(
                    f"{ipAddress}/{netmask.toString()}",
                    strict=False,
                );
                if ipAddress.is_link_local:
                    continue;
                networks.append(
                    f"{interface.humanReadableName()}: "
                    f"{network.network_address}/{network.prefixlen} "
                    f"(IP {ipAddress})"
                );

        if not networks:
            return "No active non-loopback IPv4 network found.";
        return "Network Details: " + " | ".join(networks);

    def _startHosting(self):
        print("[LAN lobby] Starting host setup")
        self._closeSession();
        self.sessionId = str(uuid.uuid4());
        self.hostServer = Host(
            port=55555,
            on_message=self._handleHostMessage,
            on_connect=self._playerConnected,
            on_disconnect=self._playerDisconnected,
        );
        try:
            _, port = self.hostServer.start();
            self._prepareDiscoverySocket(self.discoveryPort);
        except OSError as error:
            print(f"[LAN lobby] Host setup failed: {error}");
            if self.hostServer is not None:
                self.hostServer.close();
                self.hostServer = None;
            QtWidgets.QMessageBox.critical(self, "Hosting Failed", str(error));
            return;

        print(
            f"[LAN lobby] Hosting session {self.sessionId} on TCP port {port}; "
            f"discovery uses UDP port {self.discoveryPort}"
        );
        self.pages.setCurrentIndex(2);
        self.hostNetworkInfo.setText(self._getNetworkInfo());
        self.hostStatus.setText(
            f"Your game is available on this local network (port {port}). "
            "Waiting for players to join..."
        );
        self._announceGame();
        self.refreshTimer.start();

    def _startJoining(self):
        print("[LAN lobby] Starting join setup")
        self._closeSession();
        try:
            self._prepareDiscoverySocket(0);
        except OSError as error:
            print(f"[LAN lobby] Join setup failed: {error}");
            QtWidgets.QMessageBox.critical(self, "LAN Discovery Failed", str(error));
            return;

        self.games.clear();
        self.gameList.clear();
        self.joinNetworkInfo.setText(self._getNetworkInfo());
        self.joinStatus.setText("Searching your local network...");
        self.pages.setCurrentIndex(1);
        self._refreshGames();
        self.refreshTimer.start();

    def _refreshGames(self):
        if self.discoverySocket is None:
            return;

        now = time.monotonic();
        expired = [
            sessionId for sessionId, found in self.games.items()
            if now - found["lastSeen"] > 15
        ];
        for sessionId in expired:
            del self.games[sessionId];

        self._updateGameList();
        if self.pages.currentIndex() == 2:
            self._announceGame();
            return;

        print("[LAN lobby] Broadcasting LAN game discovery request")
        request = json.dumps({"type": "discover"}).encode("utf-8");
        result = self.discoverySocket.writeDatagram(
            request,
            QtNetwork.QHostAddress(
                QtNetwork.QHostAddress.SpecialAddress.Broadcast
            ),
            self.discoveryPort,
        );
        if result < 0:
            print(f"[LAN lobby] LAN discovery request failed: {self.discoverySocket.errorString()}");
            self.joinStatus.setText(
                f"LAN search failed: {self.discoverySocket.errorString()}"
            );

    def _announceGame(self, address=None, port=None):
        if self.discoverySocket is None or self.hostServer is None:
            return;

        advertisement = json.dumps({
            "type": "game",
            "session_id": self.sessionId,
            "name": QtNetwork.QHostInfo.localHostName(),
            "port": self.hostServer.port,
        }).encode("utf-8");
        destination = address or QtNetwork.QHostAddress(
            QtNetwork.QHostAddress.SpecialAddress.Broadcast
        );
        destinationPort = port or self.discoveryPort;
        result = self.discoverySocket.writeDatagram(
            advertisement, destination, destinationPort
        );
        if result < 0:
            print(f"[LAN lobby] Game advertisement failed: {self.discoverySocket.errorString()}");
            self.hostStatus.setText(
                f"LAN advertisement failed: {self.discoverySocket.errorString()}"
            );
        else:
            print(
                f"[LAN lobby] Advertised game {self.sessionId} to "
                f"{destination.toString()}:{destinationPort}"
            );

    def _readDiscoveryPackets(self):
        if self.discoverySocket is None:
            return;

        while self.discoverySocket.hasPendingDatagrams():
            datagram = self.discoverySocket.receiveDatagram();
            try:
                message = json.loads(bytes(datagram.data()).decode("utf-8"));
            except (json.JSONDecodeError, UnicodeDecodeError):
                continue;
            if not isinstance(message, dict):
                continue;

            if message.get("type") == "discover" and self.hostServer is not None:
                print(
                    f"[LAN lobby] Discovery request received from "
                    f"{datagram.senderAddress().toString()}"
                );
                self._announceGame(datagram.senderAddress(), datagram.senderPort());
            elif message.get("type") == "game" and self.pages.currentIndex() == 1:
                sessionId = message.get("session_id");
                port = message.get("port");
                name = message.get("name");
                if (
                    not isinstance(sessionId, str)
                    or not isinstance(port, int)
                    or not 0 < port < 65536
                    or not isinstance(name, str)
                ):
                    continue;
                hostAddress = datagram.senderAddress().toString();
                self.games[sessionId] = {
                    "host": hostAddress,
                    "port": port,
                    "name": name,
                    "lastSeen": time.monotonic(),
                };
                print(
                    f"[LAN lobby] Discovered game {name} at "
                    f"{hostAddress}:{port} (session {sessionId})"
                );
                self._updateGameList();

    def _updateGameList(self):
        selectedSession = None;
        selectedItem = self.gameList.currentItem();
        if selectedItem is not None:
            selectedSession = selectedItem.data(
                QtCore.Qt.ItemDataRole.UserRole
            );

        self.gameList.clear();
        for sessionId, found in sorted(
            self.games.items(), key=lambda item: item[1]["name"].casefold()
        ):
            item = QtWidgets.QListWidgetItem(
                f'{found["name"]} ({found["host"]}:{found["port"]})'
            );
            item.setData(QtCore.Qt.ItemDataRole.UserRole, sessionId);
            self.gameList.addItem(item);
            if sessionId == selectedSession:
                self.gameList.setCurrentItem(item);

        if self.games:
            self.joinStatus.setText(
                f"Found {len(self.games)} game(s). The list refreshes every 5 seconds."
            );
        else:
            self.joinStatus.setText(
                "No games found yet. Searching again every 5 seconds..."
            );

    def _joinSelectedGame(self, item=None):
        item = item or self.gameList.currentItem();
        if item is None:
            self.joinStatus.setText("Select a game before joining.");
            return;
        if self.client is not None:
            return;

        sessionId = item.data(QtCore.Qt.ItemDataRole.UserRole);
        found = self.games.get(sessionId);
        if found is None:
            self.joinStatus.setText("That game is no longer available.");
            return;

        print(
            f"[LAN lobby] Joining {found['name']} at "
            f"{found['host']}:{found['port']}"
        );
        self.refreshTimer.stop();
        self.client = Client(
            found["host"],
            found["port"],
            on_disconnect=self._clientDisconnected,
            parent=self,
        );
        self.client.connected.connect(self._clientConnected);
        self.client.socket.errorOccurred.connect(self._clientError);
        self.joinStatus.setText(f'Connecting to {found["name"]}...');
        self.connectionTimeout.start();
        self.client.connect();

    def _clientConnected(self):
        self.connectionTimeout.stop();
        if self.client is None:
            return;
        print("[LAN lobby] TCP connection established; sending join handshake")
        try:
            self.client.send({
                "type": "join",
                "player_name": QtNetwork.QHostInfo.localHostName(),
            });
        except ConnectionError as error:
            print(f"[LAN lobby] Could not send join handshake: {error}");
            self.joinStatus.setText(f"Could not join game: {error}");
            self.client.close();
            self.client = None;
            return;
        self.joinStatus.setText(
            "Connected to the host lobby."
        );
        print("[LAN lobby] Join handshake sent successfully")

    def _clientError(self, error):
        if self.client is None:
            return;
        self.connectionTimeout.stop();
        message = f"{error}: {self.client.socket.errorString()}";
        print(f"[LAN lobby] Client socket error: {message}");
        client = self.client;
        self.client = None;
        client.disconnected.disconnect(self._clientDisconnected);
        client.close();
        client.deleteLater();
        self.refreshTimer.start();
        self.joinStatus.setText(f"Could not connect to game: {message}");
        QtWidgets.QMessageBox.warning(self, "Connection Failed", message);

    def _connectionTimedOut(self):
        if self.client is None:
            return;
        print("[LAN lobby] Timed out while connecting to host")
        client = self.client;
        self.client = None;
        client.disconnected.disconnect(self._clientDisconnected);
        client.close();
        client.deleteLater();
        self.joinStatus.setText("Connection timed out. Select a game to try again.");
        self.refreshTimer.start();

    def _clientDisconnected(self):
        self.connectionTimeout.stop();
        if self.client is None:
            return;
        client = self.client;
        self.client = None;
        client.deleteLater();
        self.refreshTimer.start();
        if self.pages.currentIndex() == 1:
            self.joinStatus.setText("Disconnected from the host.");

    def _playerConnected(self, address):
        print(f"[LAN lobby] Player connected from {address[0]}:{address[1]}")
        self.connectedPlayers[address] = f"{address[0]}:{address[1]}";
        self._updatePlayerList();

    def _playerDisconnected(self, address):
        print(f"[LAN lobby] Player disconnected from {address[0]}:{address[1]}")
        self.connectedPlayers.pop(address, None);
        self._updatePlayerList();

    def _handleHostMessage(self, address, message):
        if not isinstance(message, dict) or message.get("type") != "join":
            return;
        playerName = message.get("player_name");
        if isinstance(playerName, str) and playerName.strip():
            print(
                f"[LAN lobby] Join request received from "
                f"{playerName.strip()[:40]} at {address[0]}:{address[1]}"
            );
            self.connectedPlayers[address] = playerName.strip()[:40];
            self._updatePlayerList();

    def _updatePlayerList(self):
        self.playerList.clear();
        for playerName in self.connectedPlayers.values():
            self.playerList.addItem(playerName);
        if self.connectedPlayers:
            self.hostStatus.setText(
                f"Connected players: {len(self.connectedPlayers)}. "
                "Your game is visible on the local network."
            );
        elif self.hostServer is not None:
            self.hostStatus.setText(
                f"Your game is available on this local network "
                f"(port {self.hostServer.port}). Waiting for players to join..."
            );

    def _showModePage(self):
        self._closeSession();
        self.pages.setCurrentIndex(0);

    def _closeSession(self):
        if self.client is not None or self.hostServer is not None or self.discoverySocket is not None:
            print("[LAN lobby] Closing lobby networking")
        self.refreshTimer.stop();
        self.connectionTimeout.stop();

        client = self.client;
        self.client = None;
        if client is not None:
            client.close();
            client.deleteLater();

        hostServer = self.hostServer;
        self.hostServer = None;
        if hostServer is not None:
            hostServer.close();

        if self.discoverySocket is not None:
            self.discoverySocket.close();
            self.discoverySocket.deleteLater();
            self.discoverySocket = None;
        self.connectedPlayers.clear();
        self.playerList.clear();

    def _returnToMenu(self):
        self._closeSession();
        if self.windowRef is None:
            return;
        from Scenes.menu import mainMenu;
        self.windowRef.changeScene(mainMenu);

    def closeEvent(self, event):
        self._closeSession();
        super().closeEvent(event);

class gameplayScene(QtWidgets.QWidget):

    def __init__(self, config = None, windowRef = None, playerCount = None):
        #Creating scene
        super().__init__();
        self.setFocusPolicy(QtCore.Qt.FocusPolicy.StrongFocus);
        self.config = config;
        self.windowRef = windowRef;
        self.settingsStatus = False;
        self.scoreOverlay = None;

        self.activeStatus = False

        #Audio
        self.audioOutput = QtMultimedia.QAudioOutput(self);
        self.audioOutput.setVolume(self.config.getVolume() / 100);

        self.soundEffectsOutput = QtMultimedia.QAudioOutput(self);
        self.soundEffectsOutput.setVolume(self.audioOutput.volume());
        self.audioOutput.volumeChanged.connect(self.soundEffectsOutput.setVolume);

        #Background Music
        self.backgroundMusic = QtMultimedia.QMediaPlayer(self);
        self.backgroundMusic.setAudioOutput(self.audioOutput);
        self.backgroundMusic.setSource(QtCore.QUrl.fromLocalFile("Assets/Sound/Music/wondersOfTheEarth.mp3"));
        self.backgroundMusic.setLoops(QtMultimedia.QMediaPlayer.Loops.Infinite);
        self.backgroundMusic.play();

        #Card Draw Sound & card back

        self.cardBack = QtGui.QPixmap("Assets/gamePlayScene/cardBack.png");

        self.cardDrawSound = QtMultimedia.QMediaPlayer(self);
        self.cardDrawSound.setAudioOutput(self.soundEffectsOutput);
        self.cardDrawSound.setSource(QtCore.QUrl.fromLocalFile("Assets/Sound/SFX/cardDealt.mp3"));

        #Creating player layout and logic variables
        self.background = QtGui.QPixmap("Assets/gamePlayScene/background.jpeg");
        self.playAreas = playArea();

        self.playerCount = playerCount;

        self.game = game(playerCount, 3);
        self.game.drawStartingHands();

        self.botTurnHandler = handleBotTurn(self.game, self);
        self.playerActions = playerActions(self.game, self);

        self.playerLayout = QtWidgets.QGridLayout();
        self.activeCardSource = QtGui.QPixmap();

        self.activeCard = None;
        self.activeCardLabel = visualHand.cardImageLabel(None, self);
        self.activeCardLabel.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter);
        self.activeCardLabel.setCursor(QtCore.Qt.CursorShape.PointingHandCursor);
        self.activeCardLabel.clicked.connect(self.showPassiveCard);
        self.activeCardLabel.setStyleSheet(
            "QLabel { background: transparent; border: none; }"
        );
        self.activeCardLabel.hide();

        #Adding play areas to grid
        self.playerLayout.addLayout(self.playAreas.player2(), 0, 1);
        self.playerLayout.addLayout(self.playAreas.player3(), 1, 0);
        self.playerLayout.addLayout(self.playAreas.player4(), 1, 2);
        self.playerLayout.addLayout(self.playAreas.player1(), 2, 1);
        self.playerLayout.addWidget(
            self.activeCardLabel, 1, 1,
            QtCore.Qt.AlignmentFlag.AlignBottom | QtCore.Qt.AlignmentFlag.AlignHCenter
        );

        energyDisplay = self.playAreas.playerEnergyAttribute(self.game.players[0]);
        self.playerLayout.addWidget(
            energyDisplay, 0, 2,
            QtCore.Qt.AlignmentFlag.AlignTop | QtCore.Qt.AlignmentFlag.AlignRight
        );

        self.endTurnButton = QtWidgets.QPushButton("End Turn");
        self.endTurnButton.clicked.connect(self.endTurn);
        self.endTurnButton.setStyleSheet(
            "QPushButton { "
            "background-color: rgba(128, 0, 0, 220); "
            "color: black; "
            "padding: 5px 10px; "
            "border-radius: 5px; "
            "} "
            "QPushButton:hover { "
            "background-color: rgba(102, 0, 0, 240); "
            "}");

        self.scoreButton = QtWidgets.QPushButton("Score");
        self.scoreButton.setObjectName("scoreButton");
        self.scoreButton.clicked.connect(self.showScores);
        self.scoreButton.setStyleSheet(
            "QPushButton { "
            "background-color: rgba(35, 105, 170, 210); "
            "color: black; "
            "padding: 5px 10px; "
            "border-radius: 5px; "
            "} "
            "QPushButton:hover { "
            "background-color: rgba(48, 130, 200, 230); "
            "}");

        self.playerLayout.addWidget(
            self.scoreButton, 2, 0,
            QtCore.Qt.AlignmentFlag.AlignBottom | QtCore.Qt.AlignmentFlag.AlignLeft
        );
        self.playerLayout.addWidget(
            self.endTurnButton, 2, 2,
            QtCore.Qt.AlignmentFlag.AlignBottom | QtCore.Qt.AlignmentFlag.AlignRight
        );
        self.updateEndTurnButton();

        self.playerLayout.setColumnStretch(0, 1);
        self.playerLayout.setColumnStretch(1, 1);
        self.playerLayout.setColumnStretch(2, 1);
        
        self.playerLayout.setRowStretch(0, 1);
        self.playerLayout.setRowStretch(1, 1);
        self.playerLayout.setRowStretch(2, 1);

        self.setLayout(self.playerLayout);
        self.playAreas.resize(self.size());

        self.playAreas.showHand(self.game.players, self.cardBack);
        self.playAreas.handWidgets[1].cardSelected.connect(self.showPassiveCard);
        self.playAreas.showActiveCards(self.game.players, self);
        self.passiveCardPreview = None;


    #Settings

    def openSettings(self):
        from Scenes.menu import settingsOverlayMenu;

        self.settingsOverlay = settingsOverlayMenu(self, self.audioOutput, self.config);
        self.settingsStatus = True;
        self.settingsOverlay.setGeometry(self.rect());
        self.settingsOverlay.raise_();
        self.settingsOverlay.show();

    def showEvent(self, event):
        super().showEvent(event);
        self.setFocus();
        self.playerLayout.activate();
        self.playAreas.showActiveCards(self.game.players, self);

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key.Key_Escape:
            if self.scoreOverlay is not None and self.scoreOverlay.isVisible():
                self.scoreOverlay.close();
            elif self.settingsStatus:
                self.settingsOverlay.close();
            else:
                self.openSettings();
        else:
            super().keyPressEvent(event);

    def resizeEvent(self, event):
        super().resizeEvent(event);
        self.playAreas.resize(self.size());
        self.resizeActiveCard();
        self.playerLayout.activate();
        self.playAreas.showActiveCards(self.game.players, self);

        if hasattr(self, "settingsOverlay"):
            self.settingsOverlay.setGeometry(self.rect());
        if self.scoreOverlay is not None:
            self.scoreOverlay.setGeometry(self.rect());
        if self.passiveCardPreview is not None:
            self.passiveCardPreview.reposition();

    #Card Preview -- On call action upon clicking a card in the hand, shows a larger image of the card with its name and type
    def showPassiveCard(self, card):
        if (
            self.game.currentPlayer is not self.game.players[0]
            and not isinstance(card, prizeCard)
        ):
            if self.passiveCardPreview is not None:
                self.passiveCardPreview.hide();
            return;

        if self.passiveCardPreview is None:
            self.passiveCardPreview = showPassiveCard(self);
        self.passiveCardPreview.setCard(card);
        self.passiveCardPreview.show();
        self.passiveCardPreview.raise_();

    #End Turn button handling
    def endTurn(self):
        if self.game.currentPlayer is not self.game.players[0]:
            return;

        self.playerActions.cancelAttackSelection();
        if self.passiveCardPreview is not None:
            self.passiveCardPreview.hide();

        drawnCard = self.game.nextTurn();
        self.playDrawSound(drawnCard);

        if self.showWinnerIfAny():
            return;
        self.botTurnHandler.handleBotTurn();

    def playDrawSound(self, drawnCard):
        if drawnCard is None:
            return;

        self.cardDrawSound.stop();
        self.cardDrawSound.setPosition(0);
        self.cardDrawSound.play();
        self.playAreas.showHand(self.game.players, self.cardBack);
        self.playAreas.handWidgets[1].cardSelected.connect(self.showPassiveCard);

    def showWinnerIfAny(self):
        winner = self.game.checkWinCondition();
        if winner is None:
            return False;

        self.playerActions.cancelAttackSelection();
        self.endTurnButton.setEnabled(False);
        QtWidgets.QMessageBox.information(
            self,
            "Game Over",
            f"{winner.name} wins with {len(winner.prizeCards)} prize cards!"
        );
        return True;

    def showScores(self):
        if self.scoreOverlay is not None:
            self.scoreOverlay.close();
            self.scoreOverlay.deleteLater();

        self.scoreOverlay = scoreOverlayMenu(self, self.game.players);
        self.scoreOverlay.setGeometry(self.rect());
        self.scoreOverlay.raise_();
        self.scoreOverlay.show();

    def updateEndTurnButton(self):
        self.endTurnButton.setVisible(self.game.currentPlayer is self.game.players[0]);
        self.endTurnButton.setEnabled(
            self.game.currentPlayer is self.game.players[0]
            and not self.botTurnHandler.botTurnInProgress
            and self.game.winner is None
        );

    def showActiveCard(self, card):
        self.activeCard = card;
        self.activeCardLabel.card = card;
        imagePath = Path(card.image);
        if not imagePath.is_absolute():
            imagePath = Path(__file__).resolve().parents[2] / imagePath;
        self.activeCardSource = QtGui.QPixmap(str(imagePath));
        self.activeCardLabel.setToolTip(card.name);
        self.activeCardLabel.setStyleSheet(
            "QLabel { background: transparent; border: 2px solid black; }"
        );
        self.resizeActiveCard();
        self.playAreas.showActiveCards(self.game.players, self);

    def resizeActiveCard(self):
        if self.activeCard is None:
            self.activeCardLabel.hide();
            return;

        cardSize = QtCore.QSize(
            max(1, round(70 * self.playAreas.scale)),
            max(1, round(98 * self.playAreas.scale))
        );
        self.activeCardLabel.setFixedSize(cardSize);
        if self.activeCardSource.isNull():
            self.activeCardLabel.setPixmap(QtGui.QPixmap());
            self.activeCardLabel.setText(self.activeCardLabel.toolTip());
            self.activeCardLabel.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter);
            self.activeCardLabel.show();
            return;

        self.activeCardLabel.setText("");
        self.activeCardLabel.setPixmap(self.activeCardSource.scaled(
            cardSize,
            QtCore.Qt.AspectRatioMode.KeepAspectRatio,
            QtCore.Qt.TransformationMode.SmoothTransformation
        ));
        self.activeCardLabel.show();

    #Setting scene background
    def paintEvent(self, event):
        super().paintEvent(event);
        painter = QtGui.QPainter(self);
        painter.drawPixmap(self.rect(), self.background.scaled(
            self.size(),
            QtCore.Qt.AspectRatioMode.IgnoreAspectRatio,
            QtCore.Qt.TransformationMode.SmoothTransformation
        ));

class scoreOverlayMenu(QtWidgets.QWidget):
    def __init__(self, parent, players):
        super().__init__(parent);
        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_StyledBackground, True);
        self.setStyleSheet("background-color: rgba(0, 0, 0, 150);");

        panel = QtWidgets.QWidget();
        panelWidth = max(280, min(900, parent.width() - 80));
        panelHeight = max(260, min(560, parent.height() - 80));
        panel.setFixedSize(panelWidth, panelHeight);
        panel.setStyleSheet(
            "QWidget#scorePanel { "
            "background-color: rgba(20, 38, 29, 245); "
            "border: 2px solid #d9c98b; "
            "border-radius: 8px; "
            "color: white; "
            "} "
            "QLabel { background: transparent; border: none; color: white; }"
        );
        panel.setObjectName("scorePanel");

        panelLayout = QtWidgets.QVBoxLayout(panel);
        panelLayout.setContentsMargins(16, 12, 16, 12);
        panelLayout.setSpacing(8);

        title = QtWidgets.QLabel("Scoreboard");
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: #f1d985;");
        title.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter);
        panelLayout.addWidget(title);

        subtitle = QtWidgets.QLabel("Prize cards collected (6 to win)");
        subtitle.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter);
        subtitle.setStyleSheet("color: #d5dfd4;");
        panelLayout.addWidget(subtitle);

        scoreList = QtWidgets.QWidget();
        scoreListLayout = QtWidgets.QVBoxLayout(scoreList);
        scoreListLayout.setContentsMargins(0, 0, 0, 0);
        scoreListLayout.setSpacing(8);

        for player in players:
            playerPanel = QtWidgets.QFrame();
            playerPanel.setStyleSheet(
                "QFrame { "
                "background-color: rgba(44, 68, 52, 230); "
                "border: 1px solid #71896e; "
                "border-radius: 5px; "
                "} "
                "QLabel { color: white; border: none; background: transparent; }"
            );
            playerPanelLayout = QtWidgets.QVBoxLayout(playerPanel);
            playerPanelLayout.setContentsMargins(10, 7, 10, 7);
            playerPanelLayout.setSpacing(5);

            playerType = "You" if not player.isBot else "Bot";
            scoreLabel = QtWidgets.QLabel(
                f"{player.name} ({playerType})    "
                f"Score: {len(player.prizeCards)} / 6"
            );
            scoreLabel.setStyleSheet(
                "font-size: 15px; font-weight: bold; color: #f1d985;"
            );
            playerPanelLayout.addWidget(scoreLabel);

            if player.prizeCards:
                cardRow = QtWidgets.QHBoxLayout();
                cardRow.setAlignment(QtCore.Qt.AlignmentFlag.AlignLeft);
                cardRow.setSpacing(8);
                for card in player.prizeCards:
                    cardLabel = visualHand.cardImageLabel(card);
                    cardLabel.setFixedSize(82, 115);
                    cardLabel.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter);
                    cardLabel.setCursor(QtCore.Qt.CursorShape.PointingHandCursor);
                    cardLabel.setToolTip(f"{card.name} - click to view");
                    cardLabel.setStyleSheet(
                        "QLabel { border: 1px solid #d9c98b; border-radius: 3px; }"
                    );
                    imagePath = Path(card.image);
                    if not imagePath.is_absolute():
                        imagePath = Path(__file__).resolve().parents[2] / imagePath;
                    pixmap = QtGui.QPixmap(str(imagePath));
                    if pixmap.isNull():
                        cardLabel.setText(card.name);
                    else:
                        cardLabel.setPixmap(pixmap.scaled(
                            cardLabel.size(),
                            QtCore.Qt.AspectRatioMode.KeepAspectRatio,
                            QtCore.Qt.TransformationMode.SmoothTransformation
                        ));
                    cardLabel.clicked.connect(parent.showPassiveCard);
                    cardRow.addWidget(cardLabel);
                playerPanelLayout.addLayout(cardRow);
            else:
                noCardsLabel = QtWidgets.QLabel("No prize cards yet");
                noCardsLabel.setStyleSheet("color: #c8d2c7; font-style: italic;");
                playerPanelLayout.addWidget(noCardsLabel);

            scoreListLayout.addWidget(playerPanel);

        scoreListLayout.addStretch();
        scrollArea = QtWidgets.QScrollArea();
        scrollArea.setWidgetResizable(True);
        scrollArea.setFrameShape(QtWidgets.QFrame.Shape.NoFrame);
        scrollArea.setStyleSheet(
            "QScrollArea { background: transparent; border: none; }"
            "QScrollBar:vertical { background: #20372a; width: 10px; }"
            "QScrollBar::handle:vertical { background: #71896e; border-radius: 4px; }"
        );
        scrollArea.setWidget(scoreList);
        panelLayout.addWidget(scrollArea, 1);

        closeButton = QtWidgets.QPushButton("Close");
        closeButton.setStyleSheet(
            "QPushButton { "
            "background-color: #34533d; color: white; "
            "border: 1px solid #d9c98b; border-radius: 4px; padding: 6px 18px; "
            "} "
            "QPushButton:hover { background-color: #456b50; }"
        );
        closeButton.clicked.connect(self.close);
        panelLayout.addWidget(closeButton, 0, QtCore.Qt.AlignmentFlag.AlignRight);

        overlayLayout = QtWidgets.QVBoxLayout(self);
        overlayLayout.addWidget(panel, 0, QtCore.Qt.AlignmentFlag.AlignCenter);

#Creating play area
class playArea:
    def __init__(self):
        self.playerFrames = [];
        self.playerAreaFrames = {};
        self.playerHandLayouts = {};
        self.handWidgets = {};
        self.activeCardLabels = {};
        self.activeCardHealthLabels = {};
        self.scale = 1.0;
        self.energyFrame = None;
        self.energyLabel = None;

    #creates the frame for the play area & resize function
    def createFrame(self, width, height, playerNumber):
        rect = QtWidgets.QFrame();
        rect.setStyleSheet("background-color: #026012; border: 3px solid black;");
        frameLayout = QtWidgets.QHBoxLayout(rect);
        frameLayout.setContentsMargins(0, 0, 0, 0);
        frameLayout.setSpacing(2);

        activeCardLabel = visualHand.cardImageLabel(None, rect);
        activeCardLabel.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter);
        activeCardLabel.setStyleSheet("QLabel { background: transparent; border: 2px solid black; }");
        activeCardLabel.hide();
        self.activeCardLabels[playerNumber] = activeCardLabel;

        healthLabel = QtWidgets.QLabel(rect);
        healthLabel.setAlignment(
            QtCore.Qt.AlignmentFlag.AlignCenter
        );
        healthLabel.setStyleSheet(
            "QLabel { "
            "color: #77dd77; "
            "background-color: rgba(0, 0, 0, 190); "
            "border: 1px solid #77dd77; "
            "border-radius: 4px; "
            "padding: 2px; "
            "}"
        );
        healthLabel.hide();

        self.activeCardHealthLabels[playerNumber] = healthLabel;
        self.playerAreaFrames[playerNumber] = rect;
        self.playerHandLayouts[playerNumber] = frameLayout;
        self.playerFrames.append((rect, width, height));
        return rect;

    def resize(self, size):
        scale = min(size.width() / 960, size.height() / 540);
        self.scale = scale;
        for rect, width, height in self.playerFrames:
            rect.setFixedSize(
                max(1, round(width * scale)),
                max(1, round(height * scale))
            );

        self.resizeHands();
        self.resizeEnergyAttribute();

    def resizeEnergyAttribute(self):
        if self.energyFrame is not None:
            scale = self.scale;
            self.energyFrame.setFixedSize(
                max(1, round(64 * scale)),
                max(1, round(64 * scale))
            );
            borderWidth = max(1, round(3 * scale));
            self.energyFrame.setStyleSheet(
                f"QFrame {{ background-color: #23408E; border: {borderWidth}px solid black; }}"
            );
            self.energyLabel.setStyleSheet("QLabel { color: white; border: none; }");
            font = self.energyLabel.font();
            font.setPixelSize(max(1, round(32 * scale)));
            self.energyLabel.setFont(font);

    def resizeHands(self):
        for playerNumber, handWidget in self.handWidgets.items():
            baseWidth, baseHeight = (66, 92) if playerNumber in (3, 4) else (70, 98);
            handWidget.setCardSize(QtCore.QSize(
                max(1, round(baseWidth * self.scale)),
                max(1, round(baseHeight * self.scale))
            ));

    def showActiveCards(self, players, parent):
        for playerNumber, player in enumerate(players, start=1):
            activeCardLabel = self.activeCardLabels.get(playerNumber);
            if activeCardLabel is None:
                continue;

            frame = self.playerAreaFrames[playerNumber];
            card = player.activeCard;
            healthLabel = self.activeCardHealthLabels[playerNumber];
            if card is None:
                activeCardLabel.clear();
                activeCardLabel.hide();
                healthLabel.hide();
                if playerNumber == 1:
                    parent.activeCard = None;
                    parent.activeCardSource = QtGui.QPixmap();
                    parent.activeCardLabel.card = None;
                    parent.activeCardLabel.clear();
                    parent.activeCardLabel.hide();
                continue;

            if playerNumber == 1:
                activeCardLabel.hide();
                cardPosition = parent.activeCardLabel.mapTo(
                    parent, QtCore.QPoint(0, 0)
                );
                self.showActiveCardHealth(
                    healthLabel,
                    card,
                    cardPosition,
                    parent.activeCardLabel.size(),
                    playerNumber,
                    parent
                );
                continue;

            activeCardLabel.card = card;
            if not getattr(activeCardLabel, "targetSelectionConnected", False):
                activeCardLabel.clicked.connect(parent.playerActions.selectTarget);
                activeCardLabel.targetSelectionConnected = True;

            if activeCardLabel.parentWidget() is not parent:
                activeCardLabel.setParent(parent);
            framePosition = frame.mapTo(parent, QtCore.QPoint(0, 0));
            cardSize = QtCore.QSize(
                max(1, round(70 * self.scale)),
                max(1, round(98 * self.scale))
            );
            activeCardLabel.setToolTip(card.name);

            imagePath = Path(card.image);
            if not imagePath.is_absolute():
                imagePath = Path(__file__).resolve().parents[2] / imagePath;
            pixmap = QtGui.QPixmap(str(imagePath));
            if pixmap.isNull():
                activeCardLabel.setFixedSize(cardSize);
                activeCardLabel.setPixmap(QtGui.QPixmap());
                activeCardLabel.setText(card.name);
            else:
                pixmap = pixmap.scaled(
                    cardSize,
                    QtCore.Qt.AspectRatioMode.KeepAspectRatio,
                    QtCore.Qt.TransformationMode.SmoothTransformation
                );
                rotation = {2: 180, 3: 90, 4: 270}[playerNumber];
                if rotation:
                    pixmap = pixmap.transformed(
                        QtGui.QTransform().rotate(rotation),
                        QtCore.Qt.TransformationMode.SmoothTransformation
                    );
                activeCardLabel.setFixedSize(pixmap.size());
                activeCardLabel.setText("");
                activeCardLabel.setPixmap(pixmap);

            labelWidth = activeCardLabel.width();
            labelHeight = activeCardLabel.height();
            frameCenterX = framePosition.x() + frame.width() // 2;
            frameCenterY = framePosition.y() + frame.height() // 2;
            if playerNumber == 2:
                position = QtCore.QPoint(
                    frameCenterX - labelWidth // 2,
                    framePosition.y() + frame.height() + 8
                );
            elif playerNumber == 3:
                position = QtCore.QPoint(
                    framePosition.x() + frame.width() + 8,
                    frameCenterY - labelHeight // 2
                );
            else:
                position = QtCore.QPoint(
                    framePosition.x() - labelWidth - 8,
                    frameCenterY - labelHeight // 2
                );
            activeCardLabel.move(position);
            activeCardLabel.show();
            activeCardLabel.raise_();

            self.showActiveCardHealth(
                healthLabel,
                card,
                position,
                activeCardLabel.size(),
                playerNumber,
                parent
            );

    def showActiveCardHealth(self, healthLabel, card, cardPosition, cardSize, playerNumber, parent):

        currentHealth = getattr(card, "currentHealth", None);
        maximumHealth = getattr(card, "health", None);
        if currentHealth is None or maximumHealth is None:
            healthLabel.hide();
            return;

        if healthLabel.parentWidget() is not parent:
            healthLabel.setParent(parent);
        healthLabel.setText(f"HP {currentHealth}/{maximumHealth}");
        healthLabel.setFixedSize(
            max(70, round(88 * self.scale)),
            max(20, round(24 * self.scale))
        );
        font = healthLabel.font();
        font.setPixelSize(max(8, round(12 * self.scale)));
        healthLabel.setFont(font);

        if playerNumber in (1, 2):
            position = QtCore.QPoint(
                cardPosition.x() + cardSize.width() + 4,
                cardPosition.y() + (cardSize.height() - healthLabel.height()) // 2
            );
        else:
            position = QtCore.QPoint(
                cardPosition.x() + (cardSize.width() - healthLabel.width()) // 2,
                cardPosition.y() + cardSize.height() + 4
            );
        healthLabel.move(position);
        healthLabel.show();
        healthLabel.raise_();

    def setAttackTargets(self, players, enabled):
            for playerNumber, player in enumerate(players, start=1):
                activeCardLabel = self.activeCardLabels.get(playerNumber);
                if activeCardLabel is None or activeCardLabel.isHidden():
                    continue;

                isAttackTarget = (
                    enabled
                    and playerNumber != 1
                    and player.activeCard is not None
                    and player.activeCard.currentHealth > 0
                );
                if isAttackTarget:
                    glow = QtWidgets.QGraphicsDropShadowEffect(activeCardLabel);
                    glow.setBlurRadius(24);
                    glow.setColor(QtGui.QColor(255, 255, 255, 255));
                    glow.setOffset(0, 0);
                    activeCardLabel.setGraphicsEffect(glow);
                    activeCardLabel.setCursor(QtCore.Qt.CursorShape.PointingHandCursor);
                else:
                    activeCardLabel.setGraphicsEffect(None);
                    activeCardLabel.setCursor(QtCore.Qt.CursorShape.ArrowCursor);

    #P1 area
    def player1(self):
        player1Area = QtWidgets.QHBoxLayout();
        rect = self.createFrame(600, 100, 1);
        player1Area.setAlignment(QtCore.Qt.AlignmentFlag.AlignBottom);
        player1Area.addWidget(rect, 0, QtCore.Qt.AlignmentFlag.AlignCenter);

        return player1Area;
    #P2 area
    def player2(self):
        player2Area = QtWidgets.QHBoxLayout();
        rect = self.createFrame(600, 100, 2);

        player2Area.setAlignment(QtCore.Qt.AlignmentFlag.AlignTop);
        player2Area.addWidget(rect, 0, QtCore.Qt.AlignmentFlag.AlignHCenter);

        return player2Area;
    #P3 area
    def player3(self):
        player3Area = QtWidgets.QHBoxLayout();
        rect = self.createFrame(100, 300, 3);

        player3Area.setAlignment(QtCore.Qt.AlignmentFlag.AlignLeft);
        player3Area.addWidget(rect, 0, QtCore.Qt.AlignmentFlag.AlignHCenter);

        return player3Area;
    #P4 area
    def player4(self):
        player4Area = QtWidgets.QHBoxLayout();
        rect = self.createFrame(100, 300, 4);

        player4Area.setAlignment(QtCore.Qt.AlignmentFlag.AlignRight);
        player4Area.addWidget(rect, 0, QtCore.Qt.AlignmentFlag.AlignHCenter);

        return player4Area;

    def showHand(self, players=None, cardBack=None):
        if players is None:
            players = [None];
        elif hasattr(players, "hand") or hasattr(players, "cards"):
            players = [players];
        else:
            players = list(players);

        for playerNumber, handLayout in self.playerHandLayouts.items():
            handWidget = self.handWidgets.pop(playerNumber, None);
            if handWidget is not None:
                handLayout.removeWidget(handWidget);
                handWidget.deleteLater();

        rotations = {1: 0, 2: 180, 3: 90, 4: 270};
        for playerNumber, player in enumerate(players, start=1):
            handLayout = self.playerHandLayouts.get(playerNumber);
            if handLayout is None:
                break;

            cardHand = getattr(player, "hand", player);
            handWidget = visualHand.visualHand(
                cardHand,
                handLayout.parentWidget(),
                rotation=rotations[playerNumber],
                selectable=playerNumber == 1,
                reveal_cards=playerNumber == 1,
                card_back=cardBack
            );
            handLayout.addWidget(handWidget);
            self.handWidgets[playerNumber] = handWidget;

        self.resizeHands();

    #Player energy display
    def playerEnergyAttribute(self, player):
        playerEnergyAttributeFrame = QtWidgets.QFrame();
        energyLayout = QtWidgets.QHBoxLayout(playerEnergyAttributeFrame);
        energyLayout.setContentsMargins(0, 0, 0, 0);

        self.energyLabel = QtWidgets.QLabel(str(player.getEnergy()));
        self.energyFrame = playerEnergyAttributeFrame;
        self.energyLabel.setAlignment(QtCore.Qt.AlignmentFlag.AlignHCenter | QtCore.Qt.AlignmentFlag.AlignVCenter);
        energyLayout.addWidget(self.energyLabel);
        self.resizeEnergyAttribute();

        return playerEnergyAttributeFrame;

#Adding card preview to the gameplay scene, which shows a larger image of the card with its name and 
#type when a card is clicked in the hand
#and actions that can be performed with the card
class showPassiveCard(QtWidgets.QFrame):
    def __init__(self, parent=None):
        super().__init__(parent);
        self.cardPreviewSource = QtGui.QPixmap();
        self.setStyleSheet(
            "QFrame { background-color: rgba(12, 20, 16, 225); border: 2px solid #d9c98b; }"
            "QLabel { color: white; border: none; }"
            "QPushButton { color: white; background-color: #34533d; border: 1px solid #d9c98b; padding: 3px 8px; }"
        );
        previewLayout = QtWidgets.QVBoxLayout(self);
        previewLayout.setContentsMargins(10, 10, 10, 10);

        header = QtWidgets.QHBoxLayout();
        self.actions = QtWidgets.QHBoxLayout();

        #Header section for the card preview, contains card name, type, and health
        self.nameLabel = QtWidgets.QLabel();
        self.typeLabel = QtWidgets.QLabel();
        self.healthLabel = QtWidgets.QLabel();

        header.addWidget(self.nameLabel, 1);
        header.addWidget(self.typeLabel);
        header.addWidget(self.healthLabel);
        previewLayout.addLayout(header);

        #Image section for the card preview, shows the card image
        self.imageLabel = QtWidgets.QLabel();
        self.imageLabel.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter);
        previewLayout.addWidget(self.imageLabel, 1);
        previewLayout.addLayout(self.actions);

    def setCard(self, card):
        self.nameLabel.setText(card.name);
        self.typeLabel.setText("Type: " + self.getCardType(card));

        if hasattr(card, "health"):
            currentHealth = getattr(card, "currentHealth", card.health);
            self.healthLabel.setText(
                f"Health: {currentHealth}"
            );
        else:
            self.healthLabel.hide();

        for index in reversed(range(self.actions.count())):
            item = self.actions.takeAt(index);
            widget = item.widget();
            if widget is not None:
                widget.deleteLater();

        #Obtaining card type and setting appropriate action buttons
        match self.getCardType(card):
            case "Attack":
                if not card.isActive:
                    setActiveButton = QtWidgets.QPushButton("Set Active");
                    self.actions.addWidget(setActiveButton, 1);
                    setActiveButton.clicked.connect(
                        lambda checked=False, selectedCard=card: (
                            self.parentWidget().playerActions.setActive(selectedCard)
                        )
                    );
                else:
                    attackButton = QtWidgets.QPushButton("Attack");
                    self.actions.addWidget(attackButton, 1);
                    attackButton.clicked.connect(self.parentWidget().playerActions.attack);
            case "Support":
                useButton = QtWidgets.QPushButton("Use");
                self.actions.addWidget(useButton, 1);
                useButton.clicked.connect(lambda: (self.parentWidget().playerActions.useSupportCard(card)));

        closeButton = QtWidgets.QPushButton("Close");
        closeButton.clicked.connect(self.hide);
        self.actions.addWidget(closeButton);

        self.healthLabel.setStyleSheet(
            "QLabel { "
            "color: #77dd77; "
            "background-color: rgba(30, 55, 38, 220); "
            "border: 2px solid #d9c98b; "
            "border-radius: 5px; "
            "padding: 3px 6px; "
            "font-weight: bold; "
            "}"
        );

        imagePath = Path(card.image);
        if not imagePath.is_absolute():
            imagePath = Path(__file__).resolve().parents[2] / imagePath;
        self.cardPreviewSource = QtGui.QPixmap(str(imagePath));
        self.reposition();

    def getCardType(self, card):
        if isinstance(card, attackCard):
            color = "#c3214b";
            self.nameLabel.setStyleSheet(self.headerLabelStyle(color));
            self.typeLabel.setStyleSheet(self.headerLabelStyle(color));
            return "Attack"
        if isinstance(card, prizeCard):
            color = "#ffd700";
            self.nameLabel.setStyleSheet(self.headerLabelStyle(color));
            self.typeLabel.setStyleSheet(self.headerLabelStyle(color));
            return "Prize"
        if isinstance(card, supportCard):
            color = "#1e90ff";
            self.nameLabel.setStyleSheet(self.headerLabelStyle(color));
            self.typeLabel.setStyleSheet(self.headerLabelStyle(color));
            return "Support"
        return "Unknown"

    def headerLabelStyle(self, color):
        return (
            "QLabel { "
            f"color: {color}; "
            "background-color: rgba(30, 55, 38, 220); "
            "border: 2px solid #d9c98b; "
            "border-radius: 5px; "
            "padding: 3px 6px; }"
        )

    # Reposition the card preview panel within the parent widget
    def reposition(self):
        parent = self.parentWidget();
        if parent is None:
            return;

        panelWidth = min(280, max(1, parent.width() - 40));
        panelHeight = min(400, max(1, parent.height() - 40));
        self.setGeometry(
            parent.width() - panelWidth - 20,
            (parent.height() - panelHeight) // 2,
            panelWidth,
            panelHeight
        );
        imageSize = QtCore.QSize(max(1, panelWidth - 32), max(1, panelHeight - 120));
        pixmap = self.cardPreviewSource.scaled(
            imageSize,
            QtCore.Qt.AspectRatioMode.KeepAspectRatio,
            QtCore.Qt.TransformationMode.SmoothTransformation
        );
        self.imageLabel.setPixmap(pixmap);

class playerActions(QtCore.QObject):
    def __init__(self, game, scene):
        super().__init__();
        self.game = game;
        self.scene = scene;
        self.selectingTarget = False;

        # Set the given card as the active card for the current player
    def setActive(self, card):
        scene = self.scene;
        if scene is None or scene.game.currentPlayer is not scene.game.players[0]:
            return;
        self.cancelAttackSelection();

        player = scene.game.currentPlayer;
        if not isinstance(card, attackCard) or card not in player.hand.cards:
            return;

        handWidget = scene.playAreas.handWidgets.get(1);
        if handWidget is None:
            raise RuntimeError("The human player's hand is not displayed");

        if player.activeCard is not None:
            player.activeCard.isActive = False;
            player.hand.addCard(player.activeCard);
            handWidget.addCard(player.activeCard);
        if not handWidget.removeCard(card):
            raise RuntimeError(f"Could not remove {card.name} from the displayed hand");
        player.setActiveCard(card);
        card.isActive = True;
        scene.showActiveCard(card);
        if scene.passiveCardPreview is not None:
            scene.passiveCardPreview.hide();

    #Attack related functions
    def attack(self):
        if self.selectingTarget:
            self.cancelAttackSelection();
            return;

        if self.game.currentPlayer is not self.game.players[0]:
            return;

        attacker = self.game.currentPlayer.activeCard;
        if not isinstance(attacker, attackCard) or self.game.currentPlayer.attacked:
            return;
        if self.game.currentPlayer.energy < attacker.energy:
            return;

        targets = [
            player for player in self.game.players
            if (
                player is not self.game.currentPlayer
                and player.activeCard is not None
                and player.activeCard.currentHealth > 0
            )
        ];
        if not targets:
            return;

        self.scene.playAreas.setAttackTargets(self.game.players, True);
        self.selectingTarget = True;
        if self.scene.passiveCardPreview is not None:
            self.scene.passiveCardPreview.hide();

    def cancelAttackSelection(self):
        self.selectingTarget = False;
        self.scene.playAreas.setAttackTargets(self.game.players, False);

    def selectTarget(self, targetCard):
        if not self.selectingTarget:
            return;

        attackerPlayer = self.game.currentPlayer;
        attacker = attackerPlayer.activeCard;
        targetPlayer = next(
            (
                player for player in self.game.players
                if player is not attackerPlayer and player.activeCard is targetCard
            ),
            None
        );
        if (
            attackerPlayer is not self.game.players[0]
            or not isinstance(attacker, attackCard)
            or attackerPlayer.attacked
            or targetPlayer is None
            or targetCard.currentHealth <= 0
            or attackerPlayer.energy < attacker.energy
        ):
            return;

        attackerPlayer.energy -= attacker.energy;
        damage = Combat.attack(attacker, targetCard);
        attackerPlayer.attacked = True;
        if targetCard.currentHealth <= 0:
            targetCard.currentHealth = 0;
        Combat.reportAttack(attackerPlayer, attacker, targetCard, damage);
        if targetCard.currentHealth == 0:
            self.game.resolveActiveCardDefeat(attackerPlayer, targetPlayer);

        self.cancelAttackSelection();
        self.scene.playAreas.energyLabel.setText(str(attackerPlayer.getEnergy()));
        self.scene.playAreas.showActiveCards(self.game.players, self.scene);
        if self.scene.passiveCardPreview is not None:
            self.scene.passiveCardPreview.hide();

    # Support card related use
    def useSupportCard(self, selectedCard):
        currentPlayer = self.game.currentPlayer;
        if currentPlayer is not self.game.players[0]:
            return;

        if not isinstance(selectedCard, supportCard):
            return;

        if selectedCard not in currentPlayer.hand.cards:
            return;

        handWidget = self.scene.playAreas.handWidgets.get(1);
        if handWidget is None:
            raise RuntimeError("The human player's hand is not displayed");
        if not handWidget.removeCard(selectedCard):
            raise RuntimeError(
                f"Could not remove {selectedCard.name} from the displayed hand"
            );

        selectedCard.applyEffect(currentPlayer);
        self.scene.playAreas.energyLabel.setText(str(currentPlayer.getEnergy()));
        self.scene.playAreas.showActiveCards(self.game.players, self.scene);
        if self.scene.passiveCardPreview is not None:
            self.scene.passiveCardPreview.hide();

# Handle the bot's turn in the game. Takes logic from bot.py
class handleBotTurn(QtCore.QObject):
    def __init__(self, game, scene):
        super().__init__();
        self.game = game;
        self.scene = scene;
        self.botTurnInProgress = False;

    def handleBotTurn(self, runBotAction=False):
        currentPlayer = self.game.currentPlayer;
        if not currentPlayer.isBot:
            self.botTurnInProgress = False;
            self.scene.updateEndTurnButton();
            self.scene.playAreas.energyLabel.setText(
                str(self.game.players[0].getEnergy())
            );
            return;

        self.botTurnInProgress = True;
        self.scene.updateEndTurnButton();
        if not runBotAction:
            QtCore.QTimer.singleShot(
                800,
                lambda: self.handleBotTurn(runBotAction=True)
            );
            return;

        if currentPlayer.bot is None:
            raise RuntimeError(
                f"{currentPlayer.name} is marked as a bot but has no bot controller"
            );

        currentPlayer.bot.takeTurn();
        self.scene.playAreas.showHand(self.game.players, self.scene.cardBack);
        self.scene.playAreas.handWidgets[1].cardSelected.connect(
            self.scene.showPassiveCard
        );

        self.scene.playAreas.showActiveCards(self.game.players, self.scene);
        drawnCard = self.game.nextTurn();
        self.scene.playDrawSound(drawnCard);
        if self.scene.showWinnerIfAny():
            return;
        self.handleBotTurn();