from pathlib import Path;

from PySide6 import QtCore, QtGui, QtWidgets;

from Deck.deck import deck;


class visualHand(QtWidgets.QWidget):
	def __init__(self, card_deck=None, parent=None, rotation=0):
		super().__init__(parent);
		self.rotation = rotation;

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
		card_image = QtWidgets.QLabel();

		card_image.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter);
		card_image.setToolTip(card.name);
		self.updateCardSize(card_image, source);
		self.card_sources.append((card_image, source));
		self.layout.addWidget(card_image);
		self.card_widgets.append(card_image);

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
