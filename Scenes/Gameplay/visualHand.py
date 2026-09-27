from pathlib import Path;

from PySide6 import QtCore, QtGui, QtWidgets;

from Deck.deck import deck;


class visualHand(QtWidgets.QWidget):
	def __init__(self, card_deck=None, parent=None, rotation=0):
		super().__init__(parent);
		self.rotation = rotation;

		self.card_deck = card_deck or deck();
		self.card_widgets = [];
		self.layout = QtWidgets.QHBoxLayout(self);
		self.layout.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter);

		self.showCards();

	def showCards(self):
		for card in self.card_deck.cards:
			self.addCard(card);

	#Adding visual aspect of the vard
	def addCard(self, card):
		card_size = QtCore.QSize(80,112);

		card_image = QtWidgets.QLabel();
		card_image.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter);
		card_image.setToolTip(card.name);

		image_path = Path(card.image);
		if not image_path.is_absolute():
			image_path = Path(__file__).resolve().parents[2] / image_path;

		pixmap = QtGui.QPixmap(str(image_path));
		if not pixmap.isNull():
			pixmap = pixmap.scaled(
				card_size,
				QtCore.Qt.AspectRatioMode.KeepAspectRatio,
				QtCore.Qt.TransformationMode.SmoothTransformation
			);
			if self.rotation:
				pixmap = pixmap.transformed(
				QtGui.QTransform().rotate(self.rotation),
					QtCore.Qt.TransformationMode.SmoothTransformation
				);
			card_image.setFixedSize(pixmap.size());
			card_image.setPixmap(pixmap);
		else:
			card_image.setFixedSize(card_size);
			card_image.setText(card.name);

		self.layout.addWidget(card_image);
		self.card_widgets.append(card_image);
