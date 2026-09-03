#import system functions
import sys;
import setproctitle;

#Graphical Interface
from PySide6 import QtWidgets;

#Configuration
setproctitle.setproctitle("COSC 1301 Project");
from config import Config;

#Load saved configuration
config = Config("config.json");
config.loadConfig();

#The games windows Manager
import Scenes.windowManager as windowManager;
from Scenes import menu as menu;

#Opening Application
app = QtWidgets.QApplication(sys.argv);
window = windowManager.mainWindow("COSC 1301 Project", menu.mainMenu, config);
window.show();

#Terminate process cleanly once event loop (GUI) ends
sys.exit(app.exec());

