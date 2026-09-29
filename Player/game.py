import sys;
from pathlib import Path;

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]));

from Player import player;
from Deck.deck import deck;

class game:
    def __init__(self, numberOfPlayers):
        self.players = [] # List of Players
        self.deck = deck()
        self.round = 1 # Round Number

        for i in range(numberOfPlayers):
            newPlayer = player.player(f"Player {i + 1}");
            self.players.append(newPlayer);
        self.currentPlayer = self.players[0];

    def drawStartingHands(self):
        for player in self.players:
            self.deck.shuffle();

            for i in range(1): # Cards per Player
                card = self.deck.drawCard()
                player.hand.addCard(card)

    def nextTurn(self):
        currentPlayerTurn = self.players.index(self.currentPlayer) # Current Turn

        nextPlayerTurn = (currentPlayerTurn + 1) % len(self.players) # Next players turn, repeats after last player

        if self.currentPlayer.attacked: # Adds energy after each turn
            self.currentPlayer.energy += 8
            self.currentPlayer.attacked = False
        else:
            self.currentPlayer.energy += 3

        if currentPlayerTurn == len(self.players) - 1:  # Increases round number after last player
            self.round += 1

        print(self.currentPlayer.name)
        print(self.currentPlayer.energy)
        
        self.currentPlayer = self.players[nextPlayerTurn] # Changes to next player


myGame = game(4)

print("Number of players:", len(myGame.players))

print("Deck before: ", [str(card) for card in myGame.deck.cards])

myGame.drawStartingHands()

for player in myGame.players:
    print(player.name)
    print("Hand: ", [str(card) for card in player.hand.cards])
print("Deck after: ", [str(card) for card in myGame.deck.cards])


myGame.currentPlayer.attacked = True
myGame.nextTurn()
myGame.currentPlayer.attacked = True
myGame.nextTurn()
myGame.nextTurn()
myGame.nextTurn()
