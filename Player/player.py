from Deck.deck import hand;

# Creates players
class player:
    def __init__(self, name):
        self.name = name
        self.hand = hand()
        self.activeCard = None
        self.bench = []
        self.prizeCards = []
        self.energy = 10 # Max 100 Energy
        self.attacked = False

    def setActiveCard(self, card):
        self.activeCard = card

    def addToBench(self, card):
        self.bench.append(card)

    def addPrizeCard(self, card):
        self.prizeCards.append(card)