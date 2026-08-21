#import system functions
import sys;

#Graphical Interface
from PySide6 import QtWidgets;

#The games windows Manager
import Scenes.windowManager as windowManager;\
from Scenes import menu as menu;

#Opening Application
app = QtWidgets.QApplication(sys.argv);
window = windowManager.mainWindow("Menu Test", menu.mainMenu);
window.show();

#Terminate process cleanly once event loop (GUI) ends
sys.exit(app.exec());

