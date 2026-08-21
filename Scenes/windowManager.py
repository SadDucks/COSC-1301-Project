from PySide6 import QtWidgets
from PySide6 import QtGui


class mainWindow(QtWidgets.QMainWindow):
    def __init__(self, name, scene):
        super().__init__();
        self.setWindowTitle(name);
        self.setGeometry(100, 100, 800, 600); 
        self.setCentralWidget(scene());
        self.setWindowIcon(QtGui.QIcon("Assets/windowIcon/icon.png"));


    def changeTitle(self, new_title):
        self.setWindowTitle(new_title);

    def changeScene(self, new_scene):
        self.setCentralWidget(new_scene());