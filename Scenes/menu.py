from PySide6 import QtCore
from PySide6 import QtWidgets
from PySide6 import QtMultimedia


class mainMenu(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.audioOutput = QtMultimedia.QAudioOutput(self)
        self.audioOutput.setVolume(0.5)

        #Game Title
        title = QtWidgets.QLabel("COSC 1301 Group Project");
        title.setObjectName("title");
        title.setStyleSheet("font-size: 24px; font-weight: bold;");
        title.setAlignment(QtCore.Qt.AlignmentFlag.AlignTop | QtCore.Qt.AlignmentFlag.AlignHCenter);
        title.show();

        #Play Button
        play = QtWidgets.QPushButton("Play");
        play.setObjectName("play");
        play.clicked.connect(self.startGame);
        play.show();

        #Settings Button
        settings = QtWidgets.QPushButton("Settings");
        settings.setObjectName("settings");
        settings.clicked.connect(self.openSettings);
        settings.show();

        #Quit Button
        quit = QtWidgets.QPushButton("Quit");
        quit.setObjectName("quit");
        quit.clicked.connect(self.quitGame);
        quit.show();

        #Creating and Enabling layout
        layout = QtWidgets.QVBoxLayout();

        # Add the title to the layout
        layout.addWidget(title);

        #Adding buttons to layout
        layout.addWidget(play);
        layout.addWidget(settings);
        layout.addWidget(quit);

        self.setLayout(layout);

    #Button Functionality
    def startGame(self):
        #Placeholder for starting the game
        pass

    def openSettings(self):
        self.settingsOverlay = settingsOverlayMenu(self, self.audioOutput);
        self.settingsOverlay.setGeometry(self.rect());
        self.settingsOverlay.raise_();
        self.settingsOverlay.show();

    #Quit function
    def quitGame(self):
        QtWidgets.QApplication.quit();

    def resizeEvent(self, event):
        super().resizeEvent(event);
        if hasattr(self, 'settingsOverlay'):
            self.settingsOverlay.setGeometry(self.rect());

class settingsOverlayMenu(QtWidgets.QWidget):
    def __init__(self, parent=None, audio_output=None):
        super().__init__(parent);
        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_StyledBackground, True);
        self.audioOutput = audio_output;
        self.setStyleSheet("background-color: rgba(0, 0, 0, 120);");

        #creating the background panel for Settings
        settingsBackgroundPanel = QtWidgets.QWidget();
        settingsBackgroundPanel.setFixedSize(300, 300);
        settingsBackgroundPanel.setStyleSheet("background-color: rgb(30, 30, 30); color: white;");

        #Title for the settings panel
        title = QtWidgets.QLabel("Settings");
        title.setStyleSheet("font-size: 24px; font-weight: bold;");
        title.setAlignment(QtCore.Qt.AlignmentFlag.AlignTop | QtCore.Qt.AlignmentFlag.AlignHCenter);

        #Volume Slider
        volumeSlider = QtWidgets.QSlider(QtCore.Qt.Orientation.Horizontal);

        #Configuration for Volume Slider
        volumeSlider.setObjectName("Volume");
        volumeSlider.setToolTip("Adjust the volume");
        volumeSlider.setRange(0, 100);
        volumeSlider.setValue(round(self.audioOutput.volume() * 100) if self.audioOutput else 50);
        volumeSlider.valueChanged.connect(self.volume);

       #Label for the volume slider
        volumeSliderTitleText = QtWidgets.QLabel("Volume");
        volumeSliderTitleText.setStyleSheet("font-size: 12px;");

        self.volumeSliderPercentText = QtWidgets.QLabel(str(volumeSlider.value()) + "%");
        self.volumeSliderPercentText.setStyleSheet("font-size: 12px;");

        #Layout for the volume slider and its label
        volumeLayout = QtWidgets.QHBoxLayout();
        volumeLayout.addWidget(volumeSliderTitleText, 0, QtCore.Qt.AlignmentFlag.AlignVCenter);
        volumeLayout.addWidget(self.volumeSliderPercentText, 0, QtCore.Qt.AlignmentFlag.AlignVCenter);
        volumeLayout.addStretch();
        volumeLayout.addWidget(volumeSlider);

        #Close Button
        close = QtWidgets.QPushButton("Close");
        close.clicked.connect(self.close);

        #creates a separate panel
        settingsPanelLayout = QtWidgets.QVBoxLayout(settingsBackgroundPanel);
        settingsPanelLayout.addWidget(title);

        settingsPanelLayout.addLayout(volumeLayout);
        settingsPanelLayout.addWidget(close);

        #creates the overlay and sets it as the Layout
        overlayLayout = QtWidgets.QVBoxLayout(self);
        overlayLayout.setSpacing(10);
        overlayLayout.addWidget(settingsBackgroundPanel, 0, QtCore.Qt.AlignmentFlag.AlignCenter);
        self.setLayout(overlayLayout);

    def volume(self, level):
        self.volumeSliderPercentText.setText(str(level) + "%");
        if self.audioOutput:
            self.audioOutput.setVolume(level / 100.0);

class pauseMenu(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent);
        #placeholder for pause menu implementation