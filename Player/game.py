import sys;
from pathlib import Path;

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]));

from Player import player;
from Player import bot;
from Deck.deck import deck;

class game:
    def __init__(self, numberOfPlayers, numberOfBots=None): # Total Players and how many are Bots
        numberOfPlayers = max(1, int(numberOfPlayers));

        if numberOfBots is None:
            numberOfBots = max(0, 4 - numberOfPlayers);
        else:
            numberOfBots = max(0, int(numberOfBots));

        totalPlayers = min(4, numberOfPlayers + numberOfBots);

        if totalPlayers < 4:
            numberOfBots += 4 - totalPlayers;
            totalPlayers = 4;

        self.players = []; # List of Players
        self.deck = deck();
        self.round = 1 # Round Number

        for i in range(totalPlayers):
            isBot = i >= totalPlayers - numberOfBots;
            newPlayer = player.player(f"Player {i + 1}", isBot);

            if isBot:
                newPlayer.bot = bot.bot(newPlayer, self);
        
            self.players.append(newPlayer);
        self.currentPlayer = self.players[0];

    def drawStartingHands(self):
        for player in self.players:
            self.deck.shuffle();

            for i in range(1): # Cards per Player
                card = self.deck.drawCard();
                player.hand.addCard(card);

    def nextTurn(self):
        currentPlayerTurn = self.players.index(self.currentPlayer); # Current Turn
        nextPlayerTurn = (currentPlayerTurn + 1) % len(self.players); # Next players turn, repeats after last player

        if self.currentPlayer.attacked: # Adds energy after each turn
            self.currentPlayer.energy += 8;
            self.currentPlayer.attacked = False;
        else:
            self.currentPlayer.energy += 3;

        if currentPlayerTurn == len(self.players) - 1:  # Increases round number after last player
            self.round += 1;

        print(self.currentPlayer.name);
        print("Energy:", self.currentPlayer.energy);

        print("Next player turn:", self.players[nextPlayerTurn].name)
        
        self.currentPlayer = self.players[nextPlayerTurn]; # Changes to next player


if __name__ == "__main__":
    myGame = game(4, 2)

    print("Number of players:", len(myGame.players));

    print("Deck before: ", [str(card) for card in myGame.deck.cards]);

    myGame.drawStartingHands();

    for player in myGame.players:
        print(player.name);
        print("Hand: ", [str(card) for card in player.hand.cards]);
        print("Energy: ", player.energy);
        print("isBot: ", player.isBot);
    print("Deck after: ", [str(card) for card in myGame.deck.cards]);

    myGame.currentPlayer.attacked = True;
    myGame.nextTurn();
    myGame.currentPlayer.attacked = True;
    myGame.nextTurn();


# Bot test code, prints out the bot's hand, active card, bench, energy, opponents, target, and attack status

# Everything after this is just for testing
"""
for player in myGame.players:
    if player.isBot:
        print("This is test code")

        print("Bot hand:", [card.name for card in player.bot.getHand()])

        active = player.bot.getActiveCard()

        if active is not None:
            print("Bot active:", active.name)
            print("Bot health:", active.currentHealth, "/", active.health)
        else:
            print("Bot active: None")

        print("Bot bench:", [card.name for card in player.bot.getBench()])

        print("Bot energy:", player.bot.getEnergy())

        opponents = player.bot.getOpponents()
        print("Bot opponents:", [opponent.name for opponent in opponents])

        target = player.bot.chooseTarget()

        if target is not None:
            print("Bot target:", target.name)
            print("Target health:", target.currentHealth, "/", target.health)
        else:
            print("Bot target: None")

        print("Bot has attacked:", player.attacked)
"""
