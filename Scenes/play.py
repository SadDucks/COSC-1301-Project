from PySide6 import QtCore;
from PySide6 import QtGui;
from PySide6 import QtWidgets;


class gameplayScene(QtWidgets.QWidget):

    def __init__(self, config=None):
        super().__init__();
        self.config = config;
        self.background = QtGui.QPixmap("Assets/gamePlayScene/background.jpeg");

    #Setting scene background
    def paintEvent(self, event):
        super().paintEvent(event);
        painter = QtGui.QPainter(self);
        painter.drawPixmap(self.rect(), self.background.scaled(
            self.size(),
            QtCore.Qt.AspectRatioMode.IgnoreAspectRatio,
            QtCore.Qt.TransformationMode.SmoothTransformation
        ))
        