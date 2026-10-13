import sys;
from pathlib import Path;

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]));

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

    def chooseTarget(self, attacker):
        opponents = self.getOpponents()

        bestTarget = None;
        bestScore = -1;

        for opponent in opponents:
            target = opponent.activeCard;

            if target is not None:
                score = self.evaluateTarget(attacker, target, opponent);

                if score > bestScore:
                    bestScore = score;
                    bestTarget = target;

        return bestTarget;

    def evaluateTarget(self, attacker, target, opponent):
        score = 0;

        if attacker.attack >= target.currentHealth:
            score += 100;

        wastedDamage = max(0, attacker.attack - target.currentHealth);
        score -= wastedDamage // 2;

        points = len(opponent.prizeCards)

        if points >= 7:
            score += 50;
        elif points >= 5:
            score += 25;
        elif points >= 3:
            score += 10;

        return score;

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

        target = self.chooseTarget(attacker);

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
            target.currentHealth = 0;

        Combat.reportAttack(self.player, attacker, target, damage);
        if target.currentHealth == 0:
            defeatedPlayer = next(
                (
                    opponent for opponent in self.game.players
                    if opponent.activeCard is target
                ),
                None
            );
            if defeatedPlayer is None:
                raise RuntimeError("The defeated card has no owning player");
            self.game.resolveActiveCardDefeat(self.player, defeatedPlayer);