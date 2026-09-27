from PySide6 import QtCore;
from PySide6 import QtGui;
from PySide6 import QtMultimedia;
from PySide6 import QtWidgets;

from Player.game import game;
from Scenes.Gameplay import visualHand;

class gameplayScene(QtWidgets.QWidget):

    def __init__(self, config = None, windowRef = None):
        #Creating scene
        super().__init__();
        self.setFocusPolicy(QtCore.Qt.FocusPolicy.StrongFocus);
        self.config = config;
        self.windowRef = windowRef;
        self.settingsStatus = False;

        #Audio
        self.audioOutput = QtMultimedia.QAudioOutput(self);
        self.audioOutput.setVolume(self.config.getVolume() / 100);

        self.backgroundMusic = QtMultimedia.QMediaPlayer(self);
        self.backgroundMusic.setAudioOutput(self.audioOutput);
        self.backgroundMusic.setSource(QtCore.QUrl.fromLocalFile("Assets/Sound/Music/wondersOfTheEarth.mp3"));
        self.backgroundMusic.setLoops(QtMultimedia.QMediaPlayer.Loops.Infinite);
        self.backgroundMusic.play();

        #Creating player layout
        self.background = QtGui.QPixmap("Assets/gamePlayScene/background.jpeg");
        self.playAreas = playArea();
        self.game = game(4);
        self.game.drawStartingHands();
        self.playerLayout = QtWidgets.QGridLayout();

        #Adding play areas to grid
        self.playerLayout.addLayout(self.playAreas.player2(), 0, 1);
        self.playerLayout.addLayout(self.playAreas.player3(), 1, 0);
        self.playerLayout.addLayout(self.playAreas.player4(), 1, 2);
        self.playerLayout.addLayout(self.playAreas.player1(), 2, 1);
        energyDisplay = self.playAreas.playerEnergyAttribute(self.game.players[0]);
        self.playerLayout.addWidget(
            energyDisplay, 0, 2,
            QtCore.Qt.AlignmentFlag.AlignTop | QtCore.Qt.AlignmentFlag.AlignRight
        );

        self.playerLayout.setColumnStretch(0, 1);
        self.playerLayout.setColumnStretch(1, 1);
        self.playerLayout.setColumnStretch(2, 1);
        
        self.playerLayout.setRowStretch(0, 1);
        self.playerLayout.setRowStretch(1, 1);
        self.playerLayout.setRowStretch(2, 1);

        self.setLayout(self.playerLayout);
        self.playAreas.resize(self.size());

        self.playAreas.showHand(self.game.players);


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

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key.Key_Escape:
            if self.settingsStatus:
                self.settingsOverlay.close();
            else:
                self.openSettings();
        else:
            super().keyPressEvent(event);

    def resizeEvent(self, event):
        super().resizeEvent(event);
        self.playAreas.resize(self.size());

        if hasattr(self, "settingsOverlay"):
            self.settingsOverlay.setGeometry(self.rect());

    #Setting scene background
    def paintEvent(self, event):
        super().paintEvent(event);
        painter = QtGui.QPainter(self);
        painter.drawPixmap(self.rect(), self.background.scaled(
            self.size(),
            QtCore.Qt.AspectRatioMode.IgnoreAspectRatio,
            QtCore.Qt.TransformationMode.SmoothTransformation
        ));

#Creating play area
class playArea:

    def __init__(self):
        self.playerFrames = [];
        self.playerHandLayouts = {};
        self.handWidgets = {};
        self.scale = 1.0;

    #creates the frame for the play area & resize function
    def createFrame(self, width, height, playerNumber):
        rect = QtWidgets.QFrame();
        rect.setStyleSheet("background-color: #026012; border: 3px solid black;");
        handLayout = QtWidgets.QHBoxLayout(rect);
        handLayout.setContentsMargins(0, 0, 0, 0);
        self.playerHandLayouts[playerNumber] = handLayout;
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

    def resizeHands(self):
        for playerNumber, handWidget in self.handWidgets.items():
            baseWidth, baseHeight = (66, 92) if playerNumber in (3, 4) else (70, 98);
            handWidget.setCardSize(QtCore.QSize(
                max(1, round(baseWidth * self.scale)),
                max(1, round(baseHeight * self.scale))
            ));

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

    def showHand(self, players=None):
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
                rotation=rotations[playerNumber]
            );
            handLayout.addWidget(handWidget);
            self.handWidgets[playerNumber] = handWidget;

        self.resizeHands();

    #Player energy and healthdisplay
    def playerEnergyAttribute(self, player):
        playerEnergyAttributeFrame = QtWidgets.QFrame();

        playerEnergyAttributeFrame.setFixedSize(64, 64);
        playerEnergyAttributeFrame.setStyleSheet(
            "QFrame { background-color: #23408E; border: 3px solid black; }"
            "QLabel { color: white; border: none; font-size: 32px;}"
        );
        energyLayout = QtWidgets.QHBoxLayout(playerEnergyAttributeFrame);
        energyLayout.setContentsMargins(0, 0, 0, 0);

        self.energyLabel = QtWidgets.QLabel(str(player.getEnergy()));
        self.energyLabel.setAlignment(QtCore.Qt.AlignmentFlag.AlignHCenter | QtCore.Qt.AlignmentFlag.AlignVCenter);
        energyLayout.addWidget(self.energyLabel);

        return playerEnergyAttributeFrame;
