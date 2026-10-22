from pathlib import Path;

from PySide6 import QtCore;
from PySide6 import QtGui;
from PySide6 import QtMultimedia;
from PySide6 import QtWidgets;

from Deck import Combat;
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
        self.scoreOverlay = None;

        self.activeStatus = False

        #Audio
        self.audioOutput = QtMultimedia.QAudioOutput(self);
        self.audioOutput.setVolume(self.config.getVolume() / 100);

        self.soundEffectsOutput = QtMultimedia.QAudioOutput(self);
        self.soundEffectsOutput.setVolume(self.audioOutput.volume());
        self.audioOutput.volumeChanged.connect(self.soundEffectsOutput.setVolume);

        #Background Music
        self.backgroundMusic = QtMultimedia.QMediaPlayer(self);
        self.backgroundMusic.setAudioOutput(self.audioOutput);
        self.backgroundMusic.setSource(QtCore.QUrl.fromLocalFile("Assets/Sound/Music/wondersOfTheEarth.mp3"));
        self.backgroundMusic.setLoops(QtMultimedia.QMediaPlayer.Loops.Infinite);
        self.backgroundMusic.play();

        #Card Draw Sound & card back

        self.cardBack = QtGui.QPixmap("Assets/gamePlayScene/cardBack.png");

        self.cardDrawSound = QtMultimedia.QMediaPlayer(self);
        self.cardDrawSound.setAudioOutput(self.soundEffectsOutput);
        self.cardDrawSound.setSource(QtCore.QUrl.fromLocalFile("Assets/Sound/SFX/cardDealt.mp3"));

        #Creating player layout and logic variables
        self.background = QtGui.QPixmap("Assets/gamePlayScene/background.jpeg");
        self.playAreas = playArea();
        self.game = game(1, 3);
        self.game.drawStartingHands();

        self.botTurnHandler = handleBotTurn(self.game, self);
        self.playerActions = playerActions(self.game, self);

        self.playerLayout = QtWidgets.QGridLayout();
        self.activeCardSource = QtGui.QPixmap();

        self.activeCard = None;
        self.activeCardLabel = visualHand.cardImageLabel(None, self);
        self.activeCardLabel.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter);
        self.activeCardLabel.setCursor(QtCore.Qt.CursorShape.PointingHandCursor);
        self.activeCardLabel.clicked.connect(self.showPassiveCard);
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

        self.scoreButton = QtWidgets.QPushButton("Score");
        self.scoreButton.setObjectName("scoreButton");
        self.scoreButton.clicked.connect(self.showScores);
        self.scoreButton.setStyleSheet(
            "QPushButton { "
            "background-color: rgba(35, 105, 170, 210); "
            "color: black; "
            "padding: 5px 10px; "
            "border-radius: 5px; "
            "} "
            "QPushButton:hover { "
            "background-color: rgba(48, 130, 200, 230); "
            "}");

        self.playerLayout.addWidget(
            self.scoreButton, 2, 0,
            QtCore.Qt.AlignmentFlag.AlignBottom | QtCore.Qt.AlignmentFlag.AlignLeft
        );
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

        self.playAreas.showHand(self.game.players, self.cardBack);
        self.playAreas.handWidgets[1].cardSelected.connect(self.showPassiveCard);
        self.playAreas.showActiveCards(self.game.players, self);
        self.passiveCardPreview = None;


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
        self.playerLayout.activate();
        self.playAreas.showActiveCards(self.game.players, self);

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key.Key_Escape:
            if self.scoreOverlay is not None and self.scoreOverlay.isVisible():
                self.scoreOverlay.close();
            elif self.settingsStatus:
                self.settingsOverlay.close();
            else:
                self.openSettings();
        else:
            super().keyPressEvent(event);

    def resizeEvent(self, event):
        super().resizeEvent(event);
        self.playAreas.resize(self.size());
        self.resizeActiveCard();
        self.playerLayout.activate();
        self.playAreas.showActiveCards(self.game.players, self);

        if hasattr(self, "settingsOverlay"):
            self.settingsOverlay.setGeometry(self.rect());
        if self.scoreOverlay is not None:
            self.scoreOverlay.setGeometry(self.rect());
        if self.passiveCardPreview is not None:
            self.passiveCardPreview.reposition();

    #Card Preview -- On call action upon clicking a card in the hand, shows a larger image of the card with its name and type
    def showPassiveCard(self, card):
        if (
            self.game.currentPlayer is not self.game.players[0]
            and not isinstance(card, prizeCard)
        ):
            if self.passiveCardPreview is not None:
                self.passiveCardPreview.hide();
            return;

        if self.passiveCardPreview is None:
            self.passiveCardPreview = showPassiveCard(self);
        self.passiveCardPreview.setCard(card);
        self.passiveCardPreview.show();
        self.passiveCardPreview.raise_();

    #End Turn button handling
    def endTurn(self):
        if self.game.currentPlayer is not self.game.players[0]:
            return;

        self.playerActions.cancelAttackSelection();
        if self.passiveCardPreview is not None:
            self.passiveCardPreview.hide();

        drawnCard = self.game.nextTurn();
        self.playDrawSound(drawnCard);

        if self.showWinnerIfAny():
            return;
        self.botTurnHandler.handleBotTurn();

    def playDrawSound(self, drawnCard):
        if drawnCard is None:
            return;

        self.cardDrawSound.stop();
        self.cardDrawSound.setPosition(0);
        self.cardDrawSound.play();
        self.playAreas.showHand(self.game.players, self.cardBack);
        self.playAreas.handWidgets[1].cardSelected.connect(self.showPassiveCard);

    def showWinnerIfAny(self):
        winner = self.game.checkWinCondition();
        if winner is None:
            return False;

        self.playerActions.cancelAttackSelection();
        self.endTurnButton.setEnabled(False);
        QtWidgets.QMessageBox.information(
            self,
            "Game Over",
            f"{winner.name} wins with {len(winner.prizeCards)} prize cards!"
        );
        return True;

    def showScores(self):
        if self.scoreOverlay is not None:
            self.scoreOverlay.close();
            self.scoreOverlay.deleteLater();

        self.scoreOverlay = scoreOverlayMenu(self, self.game.players);
        self.scoreOverlay.setGeometry(self.rect());
        self.scoreOverlay.raise_();
        self.scoreOverlay.show();

    def updateEndTurnButton(self):
        self.endTurnButton.setVisible(self.game.currentPlayer is self.game.players[0]);
        self.endTurnButton.setEnabled(
            self.game.currentPlayer is self.game.players[0]
            and not self.botTurnHandler.botTurnInProgress
            and self.game.winner is None
        );

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
        self.playAreas.showActiveCards(self.game.players, self);

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

class scoreOverlayMenu(QtWidgets.QWidget):
    def __init__(self, parent, players):
        super().__init__(parent);
        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_StyledBackground, True);
        self.setStyleSheet("background-color: rgba(0, 0, 0, 150);");

        panel = QtWidgets.QWidget();
        panelWidth = max(280, min(900, parent.width() - 80));
        panelHeight = max(260, min(560, parent.height() - 80));
        panel.setFixedSize(panelWidth, panelHeight);
        panel.setStyleSheet(
            "QWidget#scorePanel { "
            "background-color: rgba(20, 38, 29, 245); "
            "border: 2px solid #d9c98b; "
            "border-radius: 8px; "
            "color: white; "
            "} "
            "QLabel { background: transparent; border: none; color: white; }"
        );
        panel.setObjectName("scorePanel");

        panelLayout = QtWidgets.QVBoxLayout(panel);
        panelLayout.setContentsMargins(16, 12, 16, 12);
        panelLayout.setSpacing(8);

        title = QtWidgets.QLabel("Scoreboard");
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: #f1d985;");
        title.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter);
        panelLayout.addWidget(title);

        subtitle = QtWidgets.QLabel("Prize cards collected (6 to win)");
        subtitle.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter);
        subtitle.setStyleSheet("color: #d5dfd4;");
        panelLayout.addWidget(subtitle);

        scoreList = QtWidgets.QWidget();
        scoreListLayout = QtWidgets.QVBoxLayout(scoreList);
        scoreListLayout.setContentsMargins(0, 0, 0, 0);
        scoreListLayout.setSpacing(8);

        for player in players:
            playerPanel = QtWidgets.QFrame();
            playerPanel.setStyleSheet(
                "QFrame { "
                "background-color: rgba(44, 68, 52, 230); "
                "border: 1px solid #71896e; "
                "border-radius: 5px; "
                "} "
                "QLabel { color: white; border: none; background: transparent; }"
            );
            playerPanelLayout = QtWidgets.QVBoxLayout(playerPanel);
            playerPanelLayout.setContentsMargins(10, 7, 10, 7);
            playerPanelLayout.setSpacing(5);

            playerType = "You" if not player.isBot else "Bot";
            scoreLabel = QtWidgets.QLabel(
                f"{player.name} ({playerType})    "
                f"Score: {len(player.prizeCards)} / 6"
            );
            scoreLabel.setStyleSheet(
                "font-size: 15px; font-weight: bold; color: #f1d985;"
            );
            playerPanelLayout.addWidget(scoreLabel);

            if player.prizeCards:
                cardRow = QtWidgets.QHBoxLayout();
                cardRow.setAlignment(QtCore.Qt.AlignmentFlag.AlignLeft);
                cardRow.setSpacing(8);
                for card in player.prizeCards:
                    cardLabel = visualHand.cardImageLabel(card);
                    cardLabel.setFixedSize(82, 115);
                    cardLabel.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter);
                    cardLabel.setCursor(QtCore.Qt.CursorShape.PointingHandCursor);
                    cardLabel.setToolTip(f"{card.name} - click to view");
                    cardLabel.setStyleSheet(
                        "QLabel { border: 1px solid #d9c98b; border-radius: 3px; }"
                    );
                    imagePath = Path(card.image);
                    if not imagePath.is_absolute():
                        imagePath = Path(__file__).resolve().parents[2] / imagePath;
                    pixmap = QtGui.QPixmap(str(imagePath));
                    if pixmap.isNull():
                        cardLabel.setText(card.name);
                    else:
                        cardLabel.setPixmap(pixmap.scaled(
                            cardLabel.size(),
                            QtCore.Qt.AspectRatioMode.KeepAspectRatio,
                            QtCore.Qt.TransformationMode.SmoothTransformation
                        ));
                    cardLabel.clicked.connect(parent.showPassiveCard);
                    cardRow.addWidget(cardLabel);
                playerPanelLayout.addLayout(cardRow);
            else:
                noCardsLabel = QtWidgets.QLabel("No prize cards yet");
                noCardsLabel.setStyleSheet("color: #c8d2c7; font-style: italic;");
                playerPanelLayout.addWidget(noCardsLabel);

            scoreListLayout.addWidget(playerPanel);

        scoreListLayout.addStretch();
        scrollArea = QtWidgets.QScrollArea();
        scrollArea.setWidgetResizable(True);
        scrollArea.setFrameShape(QtWidgets.QFrame.Shape.NoFrame);
        scrollArea.setStyleSheet(
            "QScrollArea { background: transparent; border: none; }"
            "QScrollBar:vertical { background: #20372a; width: 10px; }"
            "QScrollBar::handle:vertical { background: #71896e; border-radius: 4px; }"
        );
        scrollArea.setWidget(scoreList);
        panelLayout.addWidget(scrollArea, 1);

        closeButton = QtWidgets.QPushButton("Close");
        closeButton.setStyleSheet(
            "QPushButton { "
            "background-color: #34533d; color: white; "
            "border: 1px solid #d9c98b; border-radius: 4px; padding: 6px 18px; "
            "} "
            "QPushButton:hover { background-color: #456b50; }"
        );
        closeButton.clicked.connect(self.close);
        panelLayout.addWidget(closeButton, 0, QtCore.Qt.AlignmentFlag.AlignRight);

        overlayLayout = QtWidgets.QVBoxLayout(self);
        overlayLayout.addWidget(panel, 0, QtCore.Qt.AlignmentFlag.AlignCenter);

#Creating play area
class playArea:
    def __init__(self):
        self.playerFrames = [];
        self.playerAreaFrames = {};
        self.playerHandLayouts = {};
        self.handWidgets = {};
        self.activeCardLabels = {};
        self.activeCardHealthLabels = {};
        self.activeCardStaminaLabels = self.activeCardHealthLabels;
        self.scale = 1.0;
        self.energyFrame = None;
        self.energyLabel = None;
        self.staminaBlinkTimer = QtCore.QTimer();
        self.staminaBlinkTimer.setInterval(150);
        self.staminaBlinkTimer.timeout.connect(self._updateStaminaBlink);
        self.staminaBlinkLabel = None;
        self.staminaBlinkCount = 0;

    #creates the frame for the play area & resize function
    def createFrame(self, width, height, playerNumber):
        rect = QtWidgets.QFrame();
        rect.setStyleSheet("background-color: #026012; border: 3px solid black;");
        frameLayout = QtWidgets.QHBoxLayout(rect);
        frameLayout.setContentsMargins(0, 0, 0, 0);
        frameLayout.setSpacing(2);

        activeCardLabel = visualHand.cardImageLabel(None, rect);
        activeCardLabel.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter);
        activeCardLabel.setStyleSheet("QLabel { background: transparent; border: 2px solid black; }");
        activeCardLabel.hide();
        self.activeCardLabels[playerNumber] = activeCardLabel;

        healthLabel = QtWidgets.QLabel(rect);
        healthLabel.setAlignment(
            QtCore.Qt.AlignmentFlag.AlignCenter
        );
        healthLabel.setStyleSheet(
            "QLabel { "
            "color: #77dd77; "
            "background-color: rgba(0, 0, 0, 190); "
            "border: 1px solid #77dd77; "
            "border-radius: 4px; "
            "padding: 2px; "
            "}"
        );
        healthLabel.hide();

        self.activeCardHealthLabels[playerNumber] = healthLabel;

        self.playerAreaFrames[playerNumber] = rect;
        self.playerHandLayouts[playerNumber] = frameLayout;
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
            backgroundColor = (
                "#c00000"
                if self.staminaBlinkTimer.isActive()
                and self.staminaBlinkCount % 2 == 0
                else "#23408E"
            );
            self.energyFrame.setStyleSheet(
                f"QFrame {{ background-color: {backgroundColor}; "
                f"border: {borderWidth}px solid black; }}"
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

    def showActiveCards(self, players, parent):
        for playerNumber, player in enumerate(players, start=1):
            activeCardLabel = self.activeCardLabels.get(playerNumber);
            if activeCardLabel is None:
                continue;

            frame = self.playerAreaFrames[playerNumber];
            card = player.activeCard;
            healthLabel = self.activeCardHealthLabels[playerNumber];
            if card is None:
                activeCardLabel.clear();
                activeCardLabel.hide();
                healthLabel.hide();
                if self.staminaBlinkLabel is healthLabel:
                    self.staminaBlinkTimer.stop();
                    self.staminaBlinkLabel = None;
                if playerNumber == 1:
                    parent.activeCard = None;
                    parent.activeCardSource = QtGui.QPixmap();
                    parent.activeCardLabel.card = None;
                    parent.activeCardLabel.clear();
                    parent.activeCardLabel.hide();
                continue;

            if playerNumber == 1:
                activeCardLabel.hide();
                cardPosition = parent.activeCardLabel.mapTo(
                    parent, QtCore.QPoint(0, 0)
                );
                self.showActiveCardHealth(
                    healthLabel,
                    card,
                    cardPosition,
                    parent.activeCardLabel.size(),
                    playerNumber,
                    player.energy,
                    parent
                );
                continue;

            activeCardLabel.card = card;
            if not getattr(activeCardLabel, "targetSelectionConnected", False):
                activeCardLabel.clicked.connect(parent.playerActions.selectTarget);
                activeCardLabel.targetSelectionConnected = True;

            if activeCardLabel.parentWidget() is not parent:
                activeCardLabel.setParent(parent);
            framePosition = frame.mapTo(parent, QtCore.QPoint(0, 0));
            cardSize = QtCore.QSize(
                max(1, round(70 * self.scale)),
                max(1, round(98 * self.scale))
            );
            activeCardLabel.setToolTip(card.name);

            imagePath = Path(card.image);
            if not imagePath.is_absolute():
                imagePath = Path(__file__).resolve().parents[2] / imagePath;
            pixmap = QtGui.QPixmap(str(imagePath));
            if pixmap.isNull():
                activeCardLabel.setFixedSize(cardSize);
                activeCardLabel.setPixmap(QtGui.QPixmap());
                activeCardLabel.setText(card.name);
            else:
                pixmap = pixmap.scaled(
                    cardSize,
                    QtCore.Qt.AspectRatioMode.KeepAspectRatio,
                    QtCore.Qt.TransformationMode.SmoothTransformation
                );
                rotation = {2: 180, 3: 90, 4: 270}[playerNumber];
                if rotation:
                    pixmap = pixmap.transformed(
                        QtGui.QTransform().rotate(rotation),
                        QtCore.Qt.TransformationMode.SmoothTransformation
                    );
                activeCardLabel.setFixedSize(pixmap.size());
                activeCardLabel.setText("");
                activeCardLabel.setPixmap(pixmap);

            labelWidth = activeCardLabel.width();
            labelHeight = activeCardLabel.height();
            frameCenterX = framePosition.x() + frame.width() // 2;
            frameCenterY = framePosition.y() + frame.height() // 2;
            if playerNumber == 2:
                position = QtCore.QPoint(
                    frameCenterX - labelWidth // 2,
                    framePosition.y() + frame.height() + 8
                );
            elif playerNumber == 3:
                position = QtCore.QPoint(
                    framePosition.x() + frame.width() + 8,
                    frameCenterY - labelHeight // 2
                );
            else:
                position = QtCore.QPoint(
                    framePosition.x() - labelWidth - 8,
                    frameCenterY - labelHeight // 2
                );
            activeCardLabel.move(position);
            activeCardLabel.show();
            activeCardLabel.raise_();

            self.showActiveCardHealth(
                healthLabel,
                card,
                position,
                activeCardLabel.size(),
                playerNumber,
                player.energy,
                parent
            );

    def showActiveCardHealth(self, healthLabel, card, cardPosition, cardSize, playerNumber, currentEnergy, parent):

        currentHealth = getattr(card, "currentHealth", None);
        maximumHealth = getattr(card, "health", None);
        if currentHealth is None or maximumHealth is None:
            healthLabel.hide();
            return;

        if healthLabel.parentWidget() is not parent:
            healthLabel.setParent(parent);
        healthLabel.healthText = f"HP {currentHealth}/{maximumHealth}";
        healthLabel.energyCost = card.energy;
        healthLabel.energyUsable = currentEnergy >= card.energy;
        healthLabel.setFixedSize(
            max(70, round(88 * self.scale)),
            max(34, round(40 * self.scale))
        );
        font = healthLabel.font();
        font.setPixelSize(max(8, round(12 * self.scale)));
        healthLabel.setFont(font);
        self._setStaminaStyle(
            healthLabel,
            self.staminaBlinkLabel is healthLabel
            and self.staminaBlinkCount % 2 == 0
        );

        if playerNumber in (1, 2):
            position = QtCore.QPoint(
                cardPosition.x() + cardSize.width() + 4,
                cardPosition.y() + (cardSize.height() - healthLabel.height()) // 2
            );
        else:
            position = QtCore.QPoint(
                cardPosition.x() + (cardSize.width() - healthLabel.width()) // 2,
                cardPosition.y() + cardSize.height() + 4
            );
        healthLabel.move(position);
        healthLabel.show();
        healthLabel.raise_();

    def _setStaminaStyle(self, label, alert):
        if alert:
            energyColor = "#ff3030";
        elif label.energyUsable:
            energyColor = "#42e66c";
        else:
            energyColor = "#ffe066";
        statusColor = "#42e66c" if label.energyUsable else "#ffe066";
        label.setStyleSheet(
            f"QLabel {{ color: {statusColor}; "
            "background-color: rgba(0, 0, 0, 190); "
            f"border: 1px solid {statusColor}; border-radius: 4px; padding: 2px; "
            "font-weight: bold; }"
        );
        label.setText(
            f'{label.healthText}<br>Energy: '
            f'<span style="color: {energyColor};">{label.energyCost}</span>'
        );
        label.setToolTip(
            f'{label.healthText} | Energy cost: {label.energyCost}'
        );

    def flashInsufficientStamina(self, playerNumber=1):
        label = self.activeCardStaminaLabels.get(playerNumber);
        if label is None or label.isHidden():
            return;
        self.staminaBlinkTimer.stop();
        self.staminaBlinkLabel = label;
        self.staminaBlinkCount = 8;
        self._setStaminaStyle(label, True);
        self._setEnergyBlink(True);
        self.staminaBlinkTimer.start();

    def _updateStaminaBlink(self):
        label = self.staminaBlinkLabel;
        if label is None and self.energyFrame is None:
            self.staminaBlinkTimer.stop();
            return;
        self.staminaBlinkCount -= 1;
        done = self.staminaBlinkCount <= 0 or (
            label is not None and label.isHidden()
        );
        alert = not done and self.staminaBlinkCount % 2 == 0;
        if label is not None:
            self._setStaminaStyle(label, alert);
        self._setEnergyBlink(alert);
        if done:
            self.staminaBlinkLabel = None;
            self.staminaBlinkTimer.stop();

    def _setEnergyBlink(self, alert):
        if self.energyFrame is None:
            return;
        borderWidth = max(1, round(3 * self.scale));
        backgroundColor = "#c00000" if alert else "#23408E";
        borderColor = "#ff4d4d" if alert else "black";
        self.energyFrame.setStyleSheet(
            f"QFrame {{ background-color: {backgroundColor}; "
            f"border: {borderWidth}px solid {borderColor}; }}"
        );
        self.energyLabel.setStyleSheet("QLabel { color: white; border: none; }");

    def setAttackTargets(self, players, enabled):
            for playerNumber, player in enumerate(players, start=1):
                activeCardLabel = self.activeCardLabels.get(playerNumber);
                if activeCardLabel is None or activeCardLabel.isHidden():
                    continue;

                isAttackTarget = (
                    enabled
                    and playerNumber != 1
                    and player.activeCard is not None
                    and player.activeCard.currentHealth > 0
                );
                if isAttackTarget:
                    glow = QtWidgets.QGraphicsDropShadowEffect(activeCardLabel);
                    glow.setBlurRadius(24);
                    glow.setColor(QtGui.QColor(255, 255, 255, 255));
                    glow.setOffset(0, 0);
                    activeCardLabel.setGraphicsEffect(glow);
                    activeCardLabel.setCursor(QtCore.Qt.CursorShape.PointingHandCursor);
                else:
                    activeCardLabel.setGraphicsEffect(None);
                    activeCardLabel.setCursor(QtCore.Qt.CursorShape.ArrowCursor);

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

    def showHand(self, players=None, cardBack=None):
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
                selectable=playerNumber == 1,
                reveal_cards=playerNumber == 1,
                card_back=cardBack
            );
            handLayout.addWidget(handWidget);
            self.handWidgets[playerNumber] = handWidget;

        self.resizeHands();

    #Player energy display
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

#Adding card preview to the gameplay scene, which shows a larger image of the card with its name and 
#type when a card is clicked in the hand
#and actions that can be performed with the card
class showPassiveCard(QtWidgets.QFrame):
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

        #Header section for the card preview, contains card name, type, and health
        self.nameLabel = QtWidgets.QLabel();
        self.typeLabel = QtWidgets.QLabel();
        self.healthLabel = QtWidgets.QLabel();

        header.addWidget(self.nameLabel, 1);
        header.addWidget(self.typeLabel);
        header.addWidget(self.healthLabel);
        previewLayout.addLayout(header);

        #Image section for the card preview, shows the card image
        self.imageLabel = QtWidgets.QLabel();
        self.imageLabel.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter);
        previewLayout.addWidget(self.imageLabel, 1);
        previewLayout.addLayout(self.actions);

    def setCard(self, card):
        self.nameLabel.setText(card.name);
        self.typeLabel.setText("Type: " + self.getCardType(card));

        if hasattr(card, "health"):
            currentHealth = getattr(card, "currentHealth", card.health);
            self.healthLabel.setText(
                f"Health: {currentHealth}"
            );
        else:
            self.healthLabel.hide();

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
                        lambda checked=False, selectedCard=card: (
                            self.parentWidget().playerActions.setActive(selectedCard)
                        )
                    );
                else:
                    attackButton = QtWidgets.QPushButton("Attack");
                    self.actions.addWidget(attackButton, 1);
                    attackButton.clicked.connect(self.parentWidget().playerActions.attack);
            case "Support":
                useButton = QtWidgets.QPushButton("Use");
                self.actions.addWidget(useButton, 1);
                useButton.clicked.connect(lambda: (self.parentWidget().playerActions.useSupportCard(card)));

        closeButton = QtWidgets.QPushButton("Close");
        closeButton.clicked.connect(self.hide);
        self.actions.addWidget(closeButton);

        self.healthLabel.setStyleSheet(
            "QLabel { "
            "color: #77dd77; "
            "background-color: rgba(30, 55, 38, 220); "
            "border: 2px solid #d9c98b; "
            "border-radius: 5px; "
            "padding: 3px 6px; "
            "font-weight: bold; "
            "}"
        );

        imagePath = Path(card.image);
        if not imagePath.is_absolute():
            imagePath = Path(__file__).resolve().parents[2] / imagePath;
        self.cardPreviewSource = QtGui.QPixmap(str(imagePath));
        self.reposition();

    def getCardType(self, card):
        if isinstance(card, attackCard):
            color = "#c3214b";
            self.nameLabel.setStyleSheet(self.headerLabelStyle(color));
            self.typeLabel.setStyleSheet(self.headerLabelStyle(color));
            return "Attack"
        if isinstance(card, prizeCard):
            color = "#ffd700";
            self.nameLabel.setStyleSheet(self.headerLabelStyle(color));
            self.typeLabel.setStyleSheet(self.headerLabelStyle(color));
            return "Prize"
        if isinstance(card, supportCard):
            color = "#1e90ff";
            self.nameLabel.setStyleSheet(self.headerLabelStyle(color));
            self.typeLabel.setStyleSheet(self.headerLabelStyle(color));
            return "Support"
        return "Unknown"

    def headerLabelStyle(self, color):
        return (
            "QLabel { "
            f"color: {color}; "
            "background-color: rgba(30, 55, 38, 220); "
            "border: 2px solid #d9c98b; "
            "border-radius: 5px; "
            "padding: 3px 6px; }"
        )

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

class playerActions(QtCore.QObject):
    def __init__(self, game, scene):
        super().__init__();
        self.game = game;
        self.scene = scene;
        self.selectingTarget = False;

        # Set the given card as the active card for the current player
    def setActive(self, card):
        scene = self.scene;
        if scene is None or scene.game.currentPlayer is not scene.game.players[0]:
            return;
        self.cancelAttackSelection();

        player = scene.game.currentPlayer;
        if not isinstance(card, attackCard) or card not in player.hand.cards:
            return;

        handWidget = scene.playAreas.handWidgets.get(1);
        if handWidget is None:
            raise RuntimeError("The human player's hand is not displayed");

        if player.activeCard is not None:
            player.activeCard.isActive = False;
            player.hand.addCard(player.activeCard);
            handWidget.addCard(player.activeCard);
        if not handWidget.removeCard(card):
            raise RuntimeError(f"Could not remove {card.name} from the displayed hand");
        player.setActiveCard(card);
        card.isActive = True;
        scene.showActiveCard(card);
        if scene.passiveCardPreview is not None:
            scene.passiveCardPreview.hide();

    #Attack related functions
    def attack(self):
        if self.selectingTarget:
            self.cancelAttackSelection();
            return;

        if self.game.currentPlayer is not self.game.players[0]:
            return;

        attacker = self.game.currentPlayer.activeCard;
        if not isinstance(attacker, attackCard) or self.game.currentPlayer.attacked:
            return;
        if self.game.currentPlayer.energy < attacker.energy:
            self.scene.playAreas.flashInsufficientStamina();
            return;

        targets = [
            player for player in self.game.players
            if (
                player is not self.game.currentPlayer
                and player.activeCard is not None
                and player.activeCard.currentHealth > 0
            )
        ];
        if not targets:
            return;

        self.scene.playAreas.setAttackTargets(self.game.players, True);
        self.selectingTarget = True;
        if self.scene.passiveCardPreview is not None:
            self.scene.passiveCardPreview.hide();

    def cancelAttackSelection(self):
        self.selectingTarget = False;
        self.scene.playAreas.setAttackTargets(self.game.players, False);

    def selectTarget(self, targetCard):
        if not self.selectingTarget:
            return;

        attackerPlayer = self.game.currentPlayer;
        attacker = attackerPlayer.activeCard;
        targetPlayer = next(
            (
                player for player in self.game.players
                if player is not attackerPlayer and player.activeCard is targetCard
            ),
            None
        );
        if (
            attackerPlayer is not self.game.players[0]
            or not isinstance(attacker, attackCard)
            or attackerPlayer.attacked
            or targetPlayer is None
            or targetCard.currentHealth <= 0
            or attackerPlayer.energy < attacker.energy
        ):
            return;

        attackerPlayer.energy -= attacker.energy;
        damage = Combat.attack(attacker, targetCard);
        attackerPlayer.attacked = True;
        if targetCard.currentHealth <= 0:
            targetCard.currentHealth = 0;
        Combat.reportAttack(attackerPlayer, attacker, targetCard, damage);
        if targetCard.currentHealth == 0:
            self.game.resolveActiveCardDefeat(attackerPlayer, targetPlayer);

        self.cancelAttackSelection();
        self.scene.playAreas.energyLabel.setText(str(attackerPlayer.getEnergy()));
        self.scene.playAreas.showActiveCards(self.game.players, self.scene);
        if self.scene.passiveCardPreview is not None:
            self.scene.passiveCardPreview.hide();

    # Support card related use
    def useSupportCard(self, selectedCard):
        currentPlayer = self.game.currentPlayer;
        if currentPlayer is not self.game.players[0]:
            return;

        if not isinstance(selectedCard, supportCard):
            return;

        if selectedCard not in currentPlayer.hand.cards:
            return;

        handWidget = self.scene.playAreas.handWidgets.get(1);
        if handWidget is None:
            raise RuntimeError("The human player's hand is not displayed");
        if not handWidget.removeCard(selectedCard):
            raise RuntimeError(
                f"Could not remove {selectedCard.name} from the displayed hand"
            );

        currentPlayer.applySupportCard(selectedCard);
        self.scene.playAreas.energyLabel.setText(str(currentPlayer.getEnergy()));
        self.scene.playAreas.showActiveCards(self.game.players, self.scene);
        if self.scene.passiveCardPreview is not None:
            self.scene.passiveCardPreview.hide();

# Handle the bot's turn in the game. Takes logic from bot.py
class handleBotTurn(QtCore.QObject):
    def __init__(self, game, scene):
        super().__init__();
        self.game = game;
        self.scene = scene;
        self.botTurnInProgress = False;

    def handleBotTurn(self, runBotAction=False):
        currentPlayer = self.game.currentPlayer;
        if not currentPlayer.isBot:
            self.botTurnInProgress = False;
            self.scene.updateEndTurnButton();
            self.scene.playAreas.energyLabel.setText(
                str(self.game.players[0].getEnergy())
            );
            return;

        self.botTurnInProgress = True;
        self.scene.updateEndTurnButton();
        if not runBotAction:
            QtCore.QTimer.singleShot(
                800,
                lambda: self.handleBotTurn(runBotAction=True)
            );
            return;

        if currentPlayer.bot is None:
            raise RuntimeError(
                f"{currentPlayer.name} is marked as a bot but has no bot controller"
            );

        currentPlayer.bot.takeTurn();
        self.scene.playAreas.showHand(self.game.players, self.scene.cardBack);
        self.scene.playAreas.handWidgets[1].cardSelected.connect(
            self.scene.showPassiveCard
        );

        self.scene.playAreas.showActiveCards(self.game.players, self.scene);
        drawnCard = self.game.nextTurn();
        self.scene.playDrawSound(drawnCard);
        if self.scene.showWinnerIfAny():
            return;
        self.handleBotTurn();