def attack(attacker, defender):
    damage = attacker.attack;
    defender.currentHealth -= damage;

    return damage;

def reportAttack(player, attacker, defender, damage):
    if defender.currentHealth <= 0:
        print("target defeated");

    print("Attacker: ", attacker.name, " dealt ", damage, " damage to ", defender.name);
    print("Target health: ", defender.currentHealth, "/", defender.health);
    print("Attacker health: ", attacker.currentHealth, "/", attacker.health);
    print("Player energy: ", player.energy);

def heal(card, amount):
    card.currentHealth += amount;

    if card.currentHealth > card.health:
        card.currentHealth = card.health;