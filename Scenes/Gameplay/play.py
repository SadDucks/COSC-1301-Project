from PySide6 import QtCore;
from PySide6 import QtGui;
from PySide6 import QtMultimedia;
from PySide6 import QtWidgets;



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
        self.backgroundMusic.play();

        #Creating player layout
        self.background = QtGui.QPixmap("Assets/gamePlayScene/background.jpeg");
        self.playAreas = playArea();
        self.playerLayout = QtWidgets.QGridLayout();

        self.playerLayout.addLayout(self.playAreas.player2(), 0, 1);
        self.playerLayout.addLayout(self.playAreas.player3(), 1, 0);
        self.playerLayout.addLayout(self.playAreas.player4(), 1, 2);
        self.playerLayout.addLayout(self.playAreas.player1(), 2, 1);

        self.playerLayout.setColumnStretch(0, 1);
        self.playerLayout.setColumnStretch(1, 1);
        self.playerLayout.setColumnStretch(2, 1);
        
        self.playerLayout.setRowStretch(0, 1);
        self.playerLayout.setRowStretch(1, 1);
        self.playerLayout.setRowStretch(2, 1);

        self.setLayout(self.playerLayout)
        self.playAreas.resize(self.size());


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

class playArea:

    def __init__(self):
        self.playerFrames = [];

    def createFrame(self, width, height):
        rect = QtWidgets.QFrame();
        rect.setStyleSheet("background-color: #026012; border: 3px solid black;");
        self.playerFrames.append((rect, width, height));
        return rect;

    def resize(self, size):
        scale = min(size.width() / 960, size.height() / 540);
        for rect, width, height in self.playerFrames:
            rect.setFixedSize(
                max(1, round(width * scale)),
                max(1, round(height * scale))
            );

    #P1 area
    def player1(self):
        player1Area = QtWidgets.QHBoxLayout();
        rect = self.createFrame(600, 100);

        player1Area.setAlignment(QtCore.Qt.AlignmentFlag.AlignBottom);
        player1Area.addWidget(rect, 0, QtCore.Qt.AlignmentFlag.AlignCenter);

        return player1Area;

    def player2(self):
        player2Area = QtWidgets.QHBoxLayout();
        rect = self.createFrame(600, 100);

        player2Area.setAlignment(QtCore.Qt.AlignmentFlag.AlignTop);
        player2Area.addWidget(rect, 0, QtCore.Qt.AlignmentFlag.AlignHCenter);

        return player2Area;

    def player3(self):
        player3Area = QtWidgets.QHBoxLayout();
        rect = self.createFrame(100, 300);

        player3Area.setAlignment(QtCore.Qt.AlignmentFlag.AlignLeft);
        player3Area.addWidget(rect, 0, QtCore.Qt.AlignmentFlag.AlignHCenter);

        return player3Area;

    def player4(self):
        player4Area = QtWidgets.QHBoxLayout();
        rect = self.createFrame(100, 300);

        player4Area.setAlignment(QtCore.Qt.AlignmentFlag.AlignRight);
        player4Area.addWidget(rect, 0, QtCore.Qt.AlignmentFlag.AlignHCenter);

        return player4Area;

