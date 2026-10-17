# Creates the basic information for every card

class card:
    def __init__(self, id, name, image):
        self.id = id;
        self.name = name;
        self.image = image;

    def __str__(self):
        return self.name;

# Creates Attack Cards

class attackCard(card):
    def __init__(self, id, name, image, attack, energyCost, health):
        super().__init__(id, name, image);
        self.attack = attack;
        self.energy = energyCost;
        self.health = health;
        self.currentHealth = health;
        self.isActive = False;

# Creates Support Cards

class supportCard(card):
    def __init__(self, id, name, image, healing, energy):
        super().__init__(id, name, image);
        self.healing = healing;
        self.energy = energy;

    def applyEffect(self, player):
        player.energy += self.energy;

        activeCard = player.activeCard;
        if isinstance(activeCard, attackCard):
            activeCard.currentHealth = min(
                activeCard.currentHealth + self.healing,
                activeCard.health
            );

        print(f"Applied support card {self.name} to player {player}");
        print(f"Player {player} now has {player.energy} energy and active card health \
              {player.activeCard.currentHealth if player.activeCard else 'N/A'}");

# Creates Prize Cards

class prizeCard(card):
    def __init__(self, id, name, image):
        super().__init__(id, name, image);