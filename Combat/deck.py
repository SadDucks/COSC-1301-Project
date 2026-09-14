import random
import cards as cards
import card_list


class deck:
    # Creates an empty list when a new deck is created
    def __init__(self):
        self.cards = []

        self.addCard(card_list.Link)
        self.addCard(card_list.Gannondorf)
        self.addCard(card_list.Zelda)
        self.addCard(card_list.Calamo)

        self.addCard(card_list.healing_potion)
        self.addCard(card_list.energy_potion)


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