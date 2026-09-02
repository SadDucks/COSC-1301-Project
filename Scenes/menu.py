from PySide6 import QtCore;
from PySide6 import QtWidgets;
from PySide6 import QtMultimedia;

class mainMenu(QtWidgets.QWidget):
    def __init__(self, config=None):
        super().__init__();
        self.config = config;
        self.audioOutput = QtMultimedia.QAudioOutput(self)
        self.mediaPlayer = QtMultimedia.QMediaPlayer(self)
        self.mediaPlayer.setAudioOutput(self.audioOutput)
        self.audioOutput.setVolume(self.config.getVolume() / 100.0 if self.config else 0.5)

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
        self.settingsOverlay = settingsOverlayMenu(self, self.audioOutput, self.config);
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
    def __init__(self, parent=None, audio_output=None, config=None):
        super().__init__(parent);

        self.config = config;

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
        self.volumeSlider = QtWidgets.QSlider(QtCore.Qt.Orientation.Horizontal);

        #Configuration for Volume Slider
        self.volumeSlider.setObjectName("Volume");
        self.volumeSlider.setToolTip("Adjust the volume");
        self.volumeSlider.setRange(0, 100);
        self.volumeSlider.setValue(round(self.audioOutput.volume() * 100) if self.audioOutput else (config.getVolume() if config else 50));
        self.volumeSlider.valueChanged.connect(self.volume);

       #Label for the volume slider
        volumeSliderTitleText = QtWidgets.QLabel("Volume");
        volumeSliderTitleText.setStyleSheet("font-size: 12px;");

        self.volumeSliderPercentText = QtWidgets.QLabel(str(self.volumeSlider.value()) + "%");
        self.volumeSliderPercentText.setStyleSheet("font-size: 12px;");

        #Layout for the volume slider
        volumeLayout = QtWidgets.QHBoxLayout();
        volumeLayout.setAlignment(QtCore.Qt.AlignmentFlag.AlignTop);
        
        volumeLayout.addWidget(volumeSliderTitleText, 0, QtCore.Qt.AlignmentFlag.AlignVCenter);
        volumeLayout.addWidget(self.volumeSliderPercentText, 0, QtCore.Qt.AlignmentFlag.AlignVCenter);
        volumeLayout.addStretch();
        volumeLayout.addWidget(self.volumeSlider);

        #Reset, Save, Close Button
        reset = QtWidgets.QPushButton("Reset");
        reset.clicked.connect(self.reset);

        save = QtWidgets.QPushButton("Save");
        save.clicked.connect(self.save);

        close = QtWidgets.QPushButton("Close");
        close.clicked.connect(self.close);

        footerLayout = QtWidgets.QHBoxLayout();
        footerLayout.addWidget(save);
        footerLayout.addWidget(reset);
        footerLayout.addStretch();
        footerLayout.addWidget(close);

        #creates a separate panel
        settingsPanelLayout = QtWidgets.QVBoxLayout(settingsBackgroundPanel);
        settingsPanelLayout.addWidget(title);

        settingsPanelLayout.addLayout(volumeLayout);
        settingsPanelLayout.addLayout(footerLayout);

        #creates the overlay and sets it as the Layout
        overlayLayout = QtWidgets.QVBoxLayout(self);
        overlayLayout.setSpacing(10);
        overlayLayout.addWidget(settingsBackgroundPanel, 0, QtCore.Qt.AlignmentFlag.AlignCenter);
        self.setLayout(overlayLayout);

    # Volume function to update the volume slider and the audio output volume
    def volume(self, level):
        self.volumeSliderPercentText.setText(str(level) + "%");
        if self.audioOutput:
            self.audioOutput.setVolume(level / 100.0);

    # Close function to close the settings overlay and save the volume setting
    def close(self):
        self.audioOutput.setVolume(self.config.getVolume() / 100.0);

        super().close();

    # Save function to save the volume setting to the configuration file
    def save(self):
        if self.audioOutput and self.config:
            self.config.setVolume(round(self.audioOutput.volume() * 100));
            self.audioOutput.setVolume(self.config.getVolume() / 100.0);
        self.close();

    # Reset function to reset the volume setting to the default value
    def reset(self):
        if self.config:
            self.config.resetConfig();
            # Update slider to show reset value
            self.volumeSlider.setValue(self.config.getVolume());
            self.volumeSliderPercentText.setText(str(self.config.getVolume()) + "%");

class pauseMenu(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent);
        #placeholder for pause menu implementation