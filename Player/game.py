import sys;
import random;
from pathlib import Path;

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]));

from Player import player;
from Player import bot;
from Deck.deck import deck;
from Deck import card_list;

class game:
    handSizeLimit = 8;

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
        self.prizeCards = tuple(card_list.prizeCardList);
        self.discardPile = [];
        self.winner = None;
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

    def drawCardForPlayer(self, currentPlayer):
        if currentPlayer not in self.players:
            raise ValueError("The player must belong to this game");
        if len(currentPlayer.hand.cards) >= self.handSizeLimit or not self.deck.cards:
            return None;

        card = self.deck.drawCard();
        currentPlayer.hand.addCard(card);
        return card;

    def resolveActiveCardDefeat(self, winningPlayer, defeatedPlayer):
        if winningPlayer not in self.players or defeatedPlayer not in self.players:
            raise ValueError("Both players must belong to this game");
        if winningPlayer is defeatedPlayer:
            raise ValueError("A player cannot defeat their own active card");

        defeatedCard = defeatedPlayer.activeCard;
        if defeatedCard is None or defeatedCard.currentHealth > 0:
            raise ValueError("The defeated player must have a defeated active card");

        defeatedCard.currentHealth = 0;
        defeatedCard.isActive = False;
        self.discardPile.append(defeatedCard);
        defeatedPlayer.setActiveCard(None);

        if not self.prizeCards:
            print("The prize deck is empty; no prize card was awarded.");
            return None;

        prizeChoices = list(self.prizeCards);
        random.shuffle(prizeChoices);
        prize = prizeChoices[0];
        winningPlayer.addPrizeCard(prize);
        print(f"{winningPlayer.name} earned prize card: {prize.name}");
        return prize;

    def checkWinCondition(self):
        if self.winner is None:
            self.winner = next(
                (
                    currentPlayer for currentPlayer in self.players
                    if len(currentPlayer.prizeCards) >= 6
                ),
                None
            );
        return self.winner;

    def nextTurn(self):
        if self.checkWinCondition() is not None:
            return;

        currentPlayerTurn = self.players.index(self.currentPlayer); # Current Turn
        nextPlayerTurn = (currentPlayerTurn + 1) % len(self.players); # Next players turn, repeats after last player

        if self.currentPlayer.attacked: # Adds energy after each turn
            self.currentPlayer.energy += 8;
            self.currentPlayer.attacked = False;
        else:
            self.currentPlayer.energy += 3;

        if currentPlayerTurn == len(self.players) - 1:  # Increases round number after last player
            self.round += 1;

        drawnCard = self.drawCardForPlayer(self.currentPlayer);

        print(self.currentPlayer.name);

        print("Energy:", self.currentPlayer.energy);

        print("Next player turn:", self.players[nextPlayerTurn].name)
        self.checkWinCondition();
        
        self.currentPlayer = self.players[nextPlayerTurn]; # Changes to next player
        return drawnCard;



if __name__ == "__main__":
    myGame = game(4, 2)