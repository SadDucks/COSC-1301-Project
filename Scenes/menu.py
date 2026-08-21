from PySide6 import QtCore
from PySide6 import QtWidgets


class mainMenu(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()

        title = QtWidgets.QLabel("COSC 1301 Group Project");
        title.setObjectName = "title";
        title.setStyleSheet("font-size: 24px; font-weight: bold;");
        title.setAlignment(QtCore.Qt.AlignmentFlag.AlignTop | QtCore.Qt.AlignmentFlag.AlignHCenter);
        title.show();

        layout = QtWidgets.QVBoxLayout();
        layout.addWidget(title);
        self.setLayout(layout);