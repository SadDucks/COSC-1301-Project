import random
import cards as cards
import card_list


class deck:
    # Creates an empty list when a new deck is created
    def __init__(self):
        self.cards = []

        for card in card_list.attackCardList:
            self.addCard(card)

    # Adds cards to deck
    def addCard(self, card):
        self.cards.append(card)

    def drawCard(self):
        return self.cards.pop(0)

    # Shuffles (Randomizes) deck
    def shuffle(self):
        random.shuffle(self.cards)

class hand:
    def __init__(self):
        self.cards = []

    # Adds cards to hand
    def addCard(self, card):
        self.cards.append(card)

    # Removes cards from hand
    def removeCard(self, card):
        self.cards.remove(card)

    # Clears hands
    def clearHand(self):
        self.cards.clear()