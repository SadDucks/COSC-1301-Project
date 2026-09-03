import os;
import json;

class Config:
    def __init__(self, configFilePath):
        self.configFilePath = configFilePath;
        self.configData = {};
        self.loadConfig();

    def loadConfig(self):
        if os.path.exists(self.configFilePath):
            with open(self.configFilePath, 'r') as file:
                self.configData = json.load(file);
        else:
            self.configData = {
                "comment": "Configuration file for the application. Do not edit manually unless you know what you're doing.",
                "volume": 50,
                "displayMode": "Windowed",
                "resolution": "800x600"
            };
            self.saveConfig();

    def saveConfig(self):
        with open(self.configFilePath, 'w') as file:
            json.dump(self.configData, file, indent=4);

    def getVolume(self):
        return self.configData.get("volume", 50);

    def setVolume(self, volume):
        self.configData["volume"] = volume;
        self.saveConfig();

    def isFullscreen(self):
        return self.configData.get("fullscreen", False);

    def setDisplayMode(self, displayMode):
        self.configData["displayMode"] = displayMode;
        self.saveConfig();

    def getDisplayMode(self):
        return self.configData.get("display_mode", "Windowed");

    def getResolution(self):
        return self.configData.get("resolution", "1920x1080");

    def setResolution(self, resolution):
        self.configData["resolution"] = resolution;
        self.saveConfig();

    def resetConfig(self):
        self.configData = {
            "comment": "Configuration file for the application. Do not edit manually unless you know what you're doing.",
            "volume": 50,
            "fullscreen": False,
            "resolution": "800x600"
        }
        self.saveConfig();