from PySide6 import QtCore
from PySide6 import QtWidgets


class mainMenu(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()

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

    def settings(self):
        #Placeholder for settings menu
        pass

    def quitGame(self):
        QtWidgets.QApplication.quit()