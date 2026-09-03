from PySide6 import QtWidgets
from PySide6 import QtGui


class mainWindow(QtWidgets.QMainWindow):
    def __init__(self, name, scene, config=None):
        super().__init__();

        # Setting Resolution from config
        self.config = config;
        resolution = self.config.getResolution();
        width = int(resolution.split("x")[0]);
        height = int(resolution.split("x")[1]);
        del resolution;
        
        self.setWindowTitle(name);
        self.setGeometry(100, 100, width, height);
        self.setCentralWidget(scene(config));
        self.setWindowIcon(QtGui.QIcon("Assets/windowIcon/icon.png"));

class changeWindow:
    def __init__(self, window):
        self.window = window;

    def changeTitle(self, new_title):
        self.window.setWindowTitle(new_title);

    def changeScene(self, new_scene):
        self.window.setCentralWidget(new_scene());

    def changeResolution(self, new_resolution):
        width, height = map(int, new_resolution.split("x"));
        self.window.setGeometry(100, 100, width, height);