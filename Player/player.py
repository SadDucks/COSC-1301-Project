from Deck.deck import hand;



class player:
    def __init__(self, name):
        self.name = name
        self.hand = hand()
        self.activeCard = None
        self.bench = []
        self.prizeCards = []
        self.energy = 0

    def setActiveCard(self, card):
        self.activeCard = card

    def addToBench(self, card):
        self.bench.append(card)

    def addPrizeCard(self, card):
        self.prizeCards.append(card)