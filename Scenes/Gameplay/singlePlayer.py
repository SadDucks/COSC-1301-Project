from pathlib import Path;

from PySide6 import QtCore;
from PySide6 import QtGui;
from PySide6 import QtMultimedia;
from PySide6 import QtWidgets;

from Deck.cards import attackCard, prizeCard, supportCard;
from Player.game import game;
from Scenes.Gameplay import visualHand;

class gameplayScene(QtWidgets.QWidget):

    def __init__(self, config = None, windowRef = None):
        #Creating scene
        super().__init__();
        self.setFocusPolicy(QtCore.Qt.FocusPolicy.StrongFocus);
        self.config = config;
        self.windowRef = windowRef;
        self.settingsStatus = False;

        self.activeStatus = False

        #Audio
        self.audioOutput = QtMultimedia.QAudioOutput(self);
        self.audioOutput.setVolume(self.config.getVolume() / 100);

        #Background Music
        self.backgroundMusic = QtMultimedia.QMediaPlayer(self);
        self.backgroundMusic.setAudioOutput(self.audioOutput);
        self.backgroundMusic.setSource(QtCore.QUrl.fromLocalFile("Assets/Sound/Music/wondersOfTheEarth.mp3"));
        self.backgroundMusic.setLoops(QtMultimedia.QMediaPlayer.Loops.Infinite);
        self.backgroundMusic.play();

        #Card Draw Sound
        self.cardDrawSound = QtMultimedia.QMediaPlayer(self);
        self.cardDrawSound.setAudioOutput(self.audioOutput);
        self.cardDrawSound.setSource(QtCore.QUrl.fromLocalFile("Assets/Sound/SFX/cardDealt.mp3"));

        #Creating player layout
        self.background = QtGui.QPixmap("Assets/gamePlayScene/background.jpeg");
        self.playAreas = playArea();
        self.game = game(1, 3);
        self.game.drawStartingHands();
        self.playerLayout = QtWidgets.QGridLayout();
        self.activeCardSource = QtGui.QPixmap();
        self.activeCard = None;
        self.activeCardLabel = visualHand.cardImageLabel(None, self);
        self.activeCardLabel.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter);
        self.activeCardLabel.setCursor(QtCore.Qt.CursorShape.PointingHandCursor);
        self.activeCardLabel.clicked.connect(self.showCardPreview);
        self.activeCardLabel.setStyleSheet(
            "QLabel { background: transparent; border: none; }"
        );
        self.activeCardLabel.hide();

        #Adding play areas to grid
        self.playerLayout.addLayout(self.playAreas.player2(), 0, 1);
        self.playerLayout.addLayout(self.playAreas.player3(), 1, 0);
        self.playerLayout.addLayout(self.playAreas.player4(), 1, 2);
        self.playerLayout.addLayout(self.playAreas.player1(), 2, 1);
        self.playerLayout.addWidget(
            self.activeCardLabel, 1, 1,
            QtCore.Qt.AlignmentFlag.AlignBottom | QtCore.Qt.AlignmentFlag.AlignHCenter
        );

        energyDisplay = self.playAreas.playerEnergyAttribute(self.game.players[0]);
        self.playerLayout.addWidget(
            energyDisplay, 0, 2,
            QtCore.Qt.AlignmentFlag.AlignTop | QtCore.Qt.AlignmentFlag.AlignRight
        );

        self.endTurnButton = QtWidgets.QPushButton("End Turn");
        self.endTurnButton.clicked.connect(self.endTurn);
        self.endTurnButton.setStyleSheet(
            "QPushButton { "
            "background-color: rgba(128, 0, 0, 220); "
            "color: black; "
            "padding: 5px 10px; "
            "border-radius: 5px; "
            "} "
            "QPushButton:hover { "
            "background-color: rgba(102, 0, 0, 240); "
            "}");

        self.playerLayout.addWidget(
            self.endTurnButton, 2, 2,
            QtCore.Qt.AlignmentFlag.AlignBottom | QtCore.Qt.AlignmentFlag.AlignRight
        );
        self.updateEndTurnButton();

        self.playerLayout.setColumnStretch(0, 1);
        self.playerLayout.setColumnStretch(1, 1);
        self.playerLayout.setColumnStretch(2, 1);
        
        self.playerLayout.setRowStretch(0, 1);
        self.playerLayout.setRowStretch(1, 1);
        self.playerLayout.setRowStretch(2, 1);

        self.setLayout(self.playerLayout);
        self.playAreas.resize(self.size());

        self.playAreas.showHand(self.game.players);
        self.playAreas.handWidgets[1].cardSelected.connect(self.showCardPreview);
        self.cardPreview = None;


    #Settings

    def openSettings(self):
        from Scenes.menu import settingsOverlayMenu;

        self.settingsOverlay = settingsOverlayMenu(self, self.audioOutput, self.config);
        self.settingsStatus = True;
        self.settingsOverlay.setGeometry(self.rect());
        self.settingsOverlay.raise_();
        self.settingsOverlay.show();

    def showEvent(self, event):
        super().showEvent(event);
        self.setFocus();

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key.Key_Escape:
            if self.settingsStatus:
                self.settingsOverlay.close();
            else:
                self.openSettings();
        else:
            super().keyPressEvent(event);

    def resizeEvent(self, event):
        super().resizeEvent(event);
        self.playAreas.resize(self.size());
        self.resizeActiveCard();

        if hasattr(self, "settingsOverlay"):
            self.settingsOverlay.setGeometry(self.rect());
        if self.cardPreview is not None:
            self.cardPreview.reposition();

    #Card Preview -- On call action upon clicking a card in the hand, shows a larger image of the card with its name and type
    def showCardPreview(self, card):
        if self.game.currentPlayer is not self.game.players[0]:
            if self.cardPreview is not None:
                self.cardPreview.hide();
            return;

        if self.cardPreview is None:
            self.cardPreview = cardPreview(self);
        self.cardPreview.setCard(card);
        self.cardPreview.show();
        self.cardPreview.raise_();

    #End Turn button handling
    def endTurn(self):
        if self.game.currentPlayer is not self.game.players[0]:
            return;

        self.game.nextTurn();
        self.updateEndTurnButton();

    def updateEndTurnButton(self):
        self.endTurnButton.setVisible(self.game.currentPlayer is self.game.players[0]);

    def showActiveCard(self, card):
        self.activeCard = card;
        self.activeCardLabel.card = card;
        imagePath = Path(card.image);
        if not imagePath.is_absolute():
            imagePath = Path(__file__).resolve().parents[2] / imagePath;
        self.activeCardSource = QtGui.QPixmap(str(imagePath));
        self.activeCardLabel.setToolTip(card.name);
        self.activeCardLabel.setStyleSheet(
            "QLabel { background: transparent; border: 2px solid black; }"
        );
        self.resizeActiveCard();

    def resizeActiveCard(self):
        if self.activeCard is None:
            self.activeCardLabel.hide();
            return;

        cardSize = QtCore.QSize(
            max(1, round(70 * self.playAreas.scale)),
            max(1, round(98 * self.playAreas.scale))
        );
        self.activeCardLabel.setFixedSize(cardSize);
        if self.activeCardSource.isNull():
            self.activeCardLabel.setPixmap(QtGui.QPixmap());
            self.activeCardLabel.setText(self.activeCardLabel.toolTip());
            self.activeCardLabel.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter);
            self.activeCardLabel.show();
            return;

        self.activeCardLabel.setText("");
        self.activeCardLabel.setPixmap(self.activeCardSource.scaled(
            cardSize,
            QtCore.Qt.AspectRatioMode.KeepAspectRatio,
            QtCore.Qt.TransformationMode.SmoothTransformation
        ));
        self.activeCardLabel.show();

    #Setting scene background
    def paintEvent(self, event):
        super().paintEvent(event);
        painter = QtGui.QPainter(self);
        painter.drawPixmap(self.rect(), self.background.scaled(
            self.size(),
            QtCore.Qt.AspectRatioMode.IgnoreAspectRatio,
            QtCore.Qt.TransformationMode.SmoothTransformation
        ));

#Creating play area
class playArea:
    def __init__(self):
        self.playerFrames = [];
        self.playerHandLayouts = {};
        self.handWidgets = {};
        self.scale = 1.0;
        self.energyFrame = None;
        self.energyLabel = None;

    #creates the frame for the play area & resize function
    def createFrame(self, width, height, playerNumber):
        rect = QtWidgets.QFrame();
        rect.setStyleSheet("background-color: #026012; border: 3px solid black;");
        handLayout = QtWidgets.QHBoxLayout(rect);
        handLayout.setContentsMargins(0, 0, 0, 0);
        self.playerHandLayouts[playerNumber] = handLayout;
        self.playerFrames.append((rect, width, height));
        return rect;

    def resize(self, size):
        scale = min(size.width() / 960, size.height() / 540);
        self.scale = scale;
        for rect, width, height in self.playerFrames:
            rect.setFixedSize(
                max(1, round(width * scale)),
                max(1, round(height * scale))
            );

        self.resizeHands();
        self.resizeEnergyAttribute();

    def resizeEnergyAttribute(self):
        if self.energyFrame is not None:
            scale = self.scale;
            self.energyFrame.setFixedSize(
                max(1, round(64 * scale)),
                max(1, round(64 * scale))
            );
            borderWidth = max(1, round(3 * scale));
            self.energyFrame.setStyleSheet(
                f"QFrame {{ background-color: #23408E; border: {borderWidth}px solid black; }}"
            );
            self.energyLabel.setStyleSheet("QLabel { color: white; border: none; }");
            font = self.energyLabel.font();
            font.setPixelSize(max(1, round(32 * scale)));
            self.energyLabel.setFont(font);

    def resizeHands(self):
        for playerNumber, handWidget in self.handWidgets.items():
            baseWidth, baseHeight = (66, 92) if playerNumber in (3, 4) else (70, 98);
            handWidget.setCardSize(QtCore.QSize(
                max(1, round(baseWidth * self.scale)),
                max(1, round(baseHeight * self.scale))
            ));

    #P1 area
    def player1(self):
        player1Area = QtWidgets.QHBoxLayout();
        rect = self.createFrame(600, 100, 1);
        player1Area.setAlignment(QtCore.Qt.AlignmentFlag.AlignBottom);
        player1Area.addWidget(rect, 0, QtCore.Qt.AlignmentFlag.AlignCenter);

        return player1Area;
    #P2 area
    def player2(self):
        player2Area = QtWidgets.QHBoxLayout();
        rect = self.createFrame(600, 100, 2);

        player2Area.setAlignment(QtCore.Qt.AlignmentFlag.AlignTop);
        player2Area.addWidget(rect, 0, QtCore.Qt.AlignmentFlag.AlignHCenter);

        return player2Area;
    #P3 area
    def player3(self):
        player3Area = QtWidgets.QHBoxLayout();
        rect = self.createFrame(100, 300, 3);

        player3Area.setAlignment(QtCore.Qt.AlignmentFlag.AlignLeft);
        player3Area.addWidget(rect, 0, QtCore.Qt.AlignmentFlag.AlignHCenter);

        return player3Area;
    #P4 area
    def player4(self):
        player4Area = QtWidgets.QHBoxLayout();
        rect = self.createFrame(100, 300, 4);

        player4Area.setAlignment(QtCore.Qt.AlignmentFlag.AlignRight);
        player4Area.addWidget(rect, 0, QtCore.Qt.AlignmentFlag.AlignHCenter);

        return player4Area;

    def showHand(self, players=None):
        if players is None:
            players = [None];
        elif hasattr(players, "hand") or hasattr(players, "cards"):
            players = [players];
        else:
            players = list(players);

        for playerNumber, handLayout in self.playerHandLayouts.items():
            handWidget = self.handWidgets.pop(playerNumber, None);
            if handWidget is not None:
                handLayout.removeWidget(handWidget);
                handWidget.deleteLater();

        rotations = {1: 0, 2: 180, 3: 90, 4: 270};
        for playerNumber, player in enumerate(players, start=1):
            handLayout = self.playerHandLayouts.get(playerNumber);
            if handLayout is None:
                break;

            cardHand = getattr(player, "hand", player);
            handWidget = visualHand.visualHand(
                cardHand,
                handLayout.parentWidget(),
                rotation=rotations[playerNumber],
                selectable=playerNumber == 1
            );
            handLayout.addWidget(handWidget);
            self.handWidgets[playerNumber] = handWidget;

        self.resizeHands();

    #Player energy and health display
    def playerEnergyAttribute(self, player):
        playerEnergyAttributeFrame = QtWidgets.QFrame();
        energyLayout = QtWidgets.QHBoxLayout(playerEnergyAttributeFrame);
        energyLayout.setContentsMargins(0, 0, 0, 0);

        self.energyLabel = QtWidgets.QLabel(str(player.getEnergy()));
        self.energyFrame = playerEnergyAttributeFrame;
        self.energyLabel.setAlignment(QtCore.Qt.AlignmentFlag.AlignHCenter | QtCore.Qt.AlignmentFlag.AlignVCenter);
        energyLayout.addWidget(self.energyLabel);
        self.resizeEnergyAttribute();

        return playerEnergyAttributeFrame;

    #card currently used for attack
    def activeAttack(self):
        pass;

    #When card is selected
    def passiveCard(self):
        pass;

#Adding card preview to the gameplay scene, which shows a larger image of the card with its name and 
#type when a card is clicked in the hand
#and actions that can be performed with the card
class cardPreview(QtWidgets.QFrame):
    def __init__(self, parent=None):
        super().__init__(parent);
        self.cardPreviewSource = QtGui.QPixmap();
        self.setStyleSheet(
            "QFrame { background-color: rgba(12, 20, 16, 225); border: 2px solid #d9c98b; }"
            "QLabel { color: white; border: none; }"
            "QPushButton { color: white; background-color: #34533d; border: 1px solid #d9c98b; padding: 3px 8px; }"
        );
        previewLayout = QtWidgets.QVBoxLayout(self);
        previewLayout.setContentsMargins(10, 10, 10, 10);

        header = QtWidgets.QHBoxLayout();
        self.actions = QtWidgets.QHBoxLayout();

        #Header section for the card preview, contains card name, type, and close button
        self.nameLabel = QtWidgets.QLabel();
        self.typeLabel = QtWidgets.QLabel();
        closeButton = QtWidgets.QPushButton("Close");
        closeButton.clicked.connect(self.hide);

        header.addWidget(self.nameLabel, 1);
        header.addWidget(self.typeLabel);
        header.addWidget(closeButton);
        previewLayout.addLayout(header);

        #Image section for the card preview, shows the card image
        self.imageLabel = QtWidgets.QLabel();
        self.imageLabel.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter);
        previewLayout.addWidget(self.imageLabel, 1);
        previewLayout.addLayout(self.actions);

    def setCard(self, card):
        self.nameLabel.setText(card.name);
        self.typeLabel.setText(self.getCardType(card));

        for index in reversed(range(self.actions.count())):
            item = self.actions.takeAt(index);
            widget = item.widget();
            if widget is not None:
                widget.deleteLater();

        #Obtaining card type and setting appropriate action buttons
        match self.getCardType(card):
            case "Attack":
                if not card.isActive:
                    setActiveButton = QtWidgets.QPushButton("Set Active");
                    self.actions.addWidget(setActiveButton, 1);
                    setActiveButton.clicked.connect(
                        lambda checked=False, selectedCard=card: self.setActive(selectedCard)
                    );
                else:
                    attackButton = QtWidgets.QPushButton("Attack");
                    self.actions.addWidget(attackButton, 1);
            case "Support":
                useButton = QtWidgets.QPushButton("Use");
                self.actions.addWidget(useButton, 1);

        self.nameLabel.setStyleSheet("QLabel { color: #d9c98b; border: none; }");
        self.typeLabel.setStyleSheet("QLabel { color: #d9c98b; border: none; }");

        imagePath = Path(card.image);
        if not imagePath.is_absolute():
            imagePath = Path(__file__).resolve().parents[2] / imagePath;
        self.cardPreviewSource = QtGui.QPixmap(str(imagePath));
        self.reposition();

    def getCardType(self, card):
        if isinstance(card, attackCard):
            return "Attack"
        if isinstance(card, prizeCard):
            return "Prize"
        if isinstance(card, supportCard):
            return "Support"
        return "Unknown"

    # Set the given card as the active card for the current player
    def setActive(self, card):
        scene = self.parentWidget();
        if scene is None or scene.game.currentPlayer is not scene.game.players[0]:
            return;

        player = scene.game.currentPlayer;
        if not isinstance(card, attackCard) or card not in player.hand.cards:
            return;

        handWidget = scene.playAreas.handWidgets[1];
        if player.activeCard is not None:
            player.activeCard.isActive = False;
            player.hand.addCard(player.activeCard);
            handWidget.addCard(player.activeCard);
        handWidget.removeCard(card);
        player.setActiveCard(card);
        card.isActive = True;
        scene.showActiveCard(card);
        
        self.hide();

    # Reposition the card preview panel within the parent widget
    def reposition(self):
        parent = self.parentWidget();
        if parent is None:
            return;

        panelWidth = min(280, max(1, parent.width() - 40));
        panelHeight = min(400, max(1, parent.height() - 40));
        self.setGeometry(
            parent.width() - panelWidth - 20,
            (parent.height() - panelHeight) // 2,
            panelWidth,
            panelHeight
        );
        imageSize = QtCore.QSize(max(1, panelWidth - 32), max(1, panelHeight - 120));
        pixmap = self.cardPreviewSource.scaled(
            imageSize,
            QtCore.Qt.AspectRatioMode.KeepAspectRatio,
            QtCore.Qt.TransformationMode.SmoothTransformation
        );
        self.imageLabel.setPixmap(pixmap);