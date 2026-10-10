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

    def chooseTarget(self):
        opponents = self.getOpponents()

        for opponent in opponents:
            if opponent.activeCard is not None:
                return opponent.activeCard

        return None

    def takeTurn(self):

        self.chooseActiveCard();
        attacker = self.player.activeCard;

        if attacker is None:
            return;

        if self.player.energy < attacker.energy:
            return;

        target = self.chooseTarget();

        if target is None:
            return;

        damage = Combat.calculateDamage(attacker, target);

        self.player.attacked = True;

        if target.currentHealth <= 0:
            target.currentHealth = 0;