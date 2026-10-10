from pathlib import Path;

from PySide6 import QtCore, QtGui, QtWidgets;

from Deck.deck import deck;


class cardImageLabel(QtWidgets.QLabel):
	clicked = QtCore.Signal(object);

	def __init__(self, card, parent=None):
		super().__init__(parent);
		self.card = card;

	def mousePressEvent(self, event):
		if event.button() == QtCore.Qt.MouseButton.LeftButton:
			self.clicked.emit(self.card);
		super().mousePressEvent(event);


class visualHand(QtWidgets.QWidget):
	cardSelected = QtCore.Signal(object);

	def __init__(self, card_deck=None, parent=None, rotation=0, selectable=False):
		super().__init__(parent);
		self.rotation = rotation;
		self.selectable = selectable;

		self.card_deck = card_deck or deck();
		self.card_widgets = [];
		self.card_sources = [];
		self.card_size = QtCore.QSize(70, 98);
		self.layout = QtWidgets.QHBoxLayout(self);
		self.layout.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter);
		self.layout.setContentsMargins(0, 0, 0, 0);
		self.layout.setSpacing(0);

		self.showCards();

	def showCards(self):
		for card in self.card_deck.cards:
			self.addCard(card);

	def setCardSize(self, card_size):
		self.card_size = card_size;
		for card_image, source in self.card_sources:
			self.updateCardSize(card_image, source);

	#Adding visual aspect of the vard
	def addCard(self, card):
		image_path = Path(card.image);
		if not image_path.is_absolute():
			image_path = Path(__file__).resolve().parents[2] / image_path;

		source = QtGui.QPixmap(str(image_path));
		card_image = cardImageLabel(card) if self.selectable else QtWidgets.QLabel();
		if self.selectable:
			card_image.clicked.connect(self.cardSelected.emit);

		card_image.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter);
		card_image.setToolTip(card.name);
		self.updateCardSize(card_image, source);
		self.card_sources.append((card_image, source));
		self.layout.addWidget(card_image);
		self.card_widgets.append(card_image);

	def removeCard(self, card):
		for index, card_image in enumerate(self.card_widgets):
			if card_image.card is not card:
				continue;

			self.card_deck.cards.pop(index);
			self.layout.removeWidget(card_image);
			card_image.deleteLater();
			self.card_widgets.pop(index);
			self.card_sources.pop(index);
			return True;

		return False;

	def updateCardSize(self, card_image, source):
		pixmap = source.scaled(
			self.card_size,
			QtCore.Qt.AspectRatioMode.KeepAspectRatio,
			QtCore.Qt.TransformationMode.SmoothTransformation
		);
		if not pixmap.isNull():
			if self.rotation:
				pixmap = pixmap.transformed(
					QtGui.QTransform().rotate(self.rotation),
					QtCore.Qt.TransformationMode.SmoothTransformation
				);
			card_image.setFixedSize(pixmap.size());
			card_image.setPixmap(pixmap);
		else:
			card_image.setFixedSize(self.card_size);
			card_image.setPixmap(QtGui.QPixmap());
			card_image.setText(card_image.toolTip());
