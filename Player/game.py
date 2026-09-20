import sys
from pathlib import Path

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from Player import player
from Deck.deck import deck

class game:
    def __init__(self, numberOfPlayers):
        self.players = []
        self.deck = deck()

        for i in range(numberOfPlayers):
            newPlayer = player.player(f"Player {i + 1}")
            self.players.append(newPlayer)
        self.currentPlayer = self.players[0]

    def drawStartingHands(self):
        for player in self.players:
            self.deck.shuffle()

            for i in range(1): # Cards per Player
                card = self.deck.drawCard()
                player.hand.addCard(card)

myGame = game(3)

print("Number of players:", len(myGame.players))

print("Deck before: ", [str(card) for card in myGame.deck.cards])

myGame.drawStartingHands()

for player in myGame.players:
    print(player.name)
    print("Hand: ", [str(card) for card in player.hand.cards])
print("Deck after: ", [str(card) for card in myGame.deck.cards])