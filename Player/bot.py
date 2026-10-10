import sys;
from pathlib import Path;

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from Deck import Combat;

class bot:
    def __init__(self, player, game):
        self.player = player;
        self.game = game;

    def getHand(self):
        return self.player.hand.cards;

    def getActiveCard(self):
        return self.player.activeCard;

    def getBench(self):
        return self.player.bench;

    def getEnergy(self):
        return self.player.energy;

    def getOpponents(self):
        opponents = [];

        for player in self.game.players:
            if player != self.player:
                opponents.append(player);

        return opponents;

    def hasAttacked(self):
        return self.player.attacked;

    def chooseActiveCard(self):
        if self.player.activeCard is None and len(self.player.bench) > 0:
            self.player.activeCard = self.player.bench.pop(0);
            self.player.activeCard.isActive = True;

    def chooseTarget(self):
        
        opponents = self.getOpponents()

        for opponent in opponents:
            if opponent.activeCard is not None:
                return opponent.activeCard

        return None

    def takeTurn(self):

        print("TEST\n\n\n")#TEST

        self.chooseActiveCard();
        attacker = self.player.activeCard;

        if attacker is None:
            for card in self.player.hand.cards:
                if hasattr(card, "attack"):
                    self.player.activeCard = card;
                    self.player.hand.removeCard(card);
                    card.isActive = True;
                    print("Active card chosen:", self.player.activeCard.name);#TEST
                    attacker = card;
                    break;

        if attacker is None:
            print("No active card available, moving on.");
            return;

        target = self.chooseTarget();
        if target is None:
            print("No target"); #TEST
            return;

        if self.player.energy < attacker.energy:
            print("Not enough energy!");#TEST
            return;

        self.player.energy -= attacker.energy;

        damage = Combat.attack(attacker, target);

        self.player.attacked = True;

        if target.currentHealth <= 0:
            print("target defeated");#TEST
            target.currentHealth = 0;

        print("Attacker: ", attacker.name, " dealt ", damage, " damage to ", target.name);#TEST
        print("Target health: ", target.currentHealth, "/", target.health);#TEST
        print("Attacker health: ", attacker.currentHealth, "/", attacker.health);#TEST
        print("Player energy: ", self.player.energy);#TEST