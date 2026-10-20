def attack(attacker, defender):
    damage = attacker.attack + getattr(attacker, "damageBoost", 0);

    shield = getattr(defender, "shield", 0);
    absorbed = min(damage, shield);
    damage -= absorbed;
    defender.shield = shield - absorbed;

    defender.currentHealth = max(0, defender.currentHealth - damage);
    attacker.damageBoost = 0;

    return damage;

def reportAttack(player, attacker, defender, damage):
    if defender.currentHealth <= 0:
        print("target defeated");

    print("Attacker: ", attacker.name, " dealt ", damage, " damage to ", defender.name);
    print("Target health: ", defender.currentHealth, "/", defender.health);
    print("Attacker health: ", attacker.currentHealth, "/", attacker.health);
    print("Player energy: ", player.energy);

def heal(card, amount):
    card.currentHealth = min(card.currentHealth + amount, card.health);

def applySupport(supportCard, player):
    effect = supportCard.effectType;
    amount = supportCard.amount;
    activeCard = player.activeCard;

    if effect == "healing":
        if activeCard is not None:
            heal(activeCard, amount);

    elif effect == "energy":
        player.energy += amount;

    elif effect == "damage_boost":
        if activeCard is not None:
            activeCard.damageBoost = (getattr(activeCard, "damageBoost", 0) + amount);

    elif effect == "shield":
        if activeCard is not None:
            activeCard.shield = (getattr(activeCard, "shield", 0) + amount);

    else:
        raise ValueError(f"Unknown support effect: {effect}");