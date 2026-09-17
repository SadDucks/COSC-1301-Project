def attack(attacker, defender):
    damage = attacker.attack
    defender.currentHealth -= damage

    return damage

def heal(card, amount):
    card.currentHealth += amount

    if card.currentHealth > card.health:
        card.currentHealth = card.health