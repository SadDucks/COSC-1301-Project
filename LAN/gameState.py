from Deck.cards import attackCard, prizeCard, supportCard


def _serializeCard(card):
    if isinstance(card, attackCard):
        return {
            "type": "attack",
            "id": card.id,
            "name": card.name,
            "image": card.image,
            "attack": card.attack,
            "energy": card.energy,
            "health": card.health,
            "currentHealth": card.currentHealth,
            "isActive": card.isActive,
        }
    if isinstance(card, supportCard):
        return {
            "type": "support",
            "id": card.id,
            "name": card.name,
            "image": card.image,
            "effects": card.effects,
        }
    if isinstance(card, prizeCard):
        return {
            "type": "prize",
            "id": card.id,
            "name": card.name,
            "image": card.image,
        }
    raise TypeError(f"Unsupported card type: {type(card).__name__}")


def _deserializeCard(data):
    cardType = data.get("type")
    if cardType == "attack":
        card = attackCard(
            data["id"],
            data["name"],
            data["image"],
            data["attack"],
            data["energy"],
            data["health"],
        )
        card.currentHealth = data["currentHealth"]
        card.isActive = data["isActive"]
        return card
    if cardType == "support":
        return supportCard(data["id"], data["name"], data["image"], data["effects"])
    if cardType == "prize":
        return prizeCard(data["id"], data["name"], data["image"])
    raise ValueError(f"Unsupported card type: {cardType!r}")


def serializeGame(game):
    return {
        "round": game.round,
        "currentPlayer": game.players.index(game.currentPlayer),
        "winner": game.players.index(game.winner) if game.winner in game.players else None,
        "players": [
            {
                "name": player.name,
                "isBot": player.isBot,
                "hand": [_serializeCard(card) for card in player.hand.cards],
                "activeCard": _serializeCard(player.activeCard) if player.activeCard else None,
                "bench": [_serializeCard(card) for card in player.bench],
                "prizeCards": [_serializeCard(card) for card in player.prizeCards],
                "energy": player.energy,
                "damageBoost": player.damageBoost,
                "shield": player.shield,
                "attacked": player.attacked,
            }
            for player in game.players
        ],
        "deck": [_serializeCard(card) for card in game.deck.cards],
        "discardPile": [_serializeCard(card) for card in game.discardPile],
        "prizeDeck": [_serializeCard(card) for card in game.prizeCards],
    }


def restoreGame(game, state):
    players = state["players"]
    if len(players) != len(game.players):
        raise ValueError("The synchronized game must contain four players")

    for player, data in zip(game.players, players):
        player.name = data["name"]
        player.isBot = data["isBot"]
        player.hand.cards = [_deserializeCard(card) for card in data["hand"]]
        player.activeCard = (
            _deserializeCard(data["activeCard"]) if data["activeCard"] else None
        )
        player.bench = [_deserializeCard(card) for card in data["bench"]]
        player.prizeCards = [_deserializeCard(card) for card in data["prizeCards"]]
        player.energy = data["energy"]
        player.damageBoost = data["damageBoost"]
        player.shield = data["shield"]
        player.attacked = data["attacked"]
        if player.bot is not None:
            player.bot.player = player
            player.bot.game = game

    game.deck.cards = [_deserializeCard(card) for card in state["deck"]]
    game.discardPile = [_deserializeCard(card) for card in state["discardPile"]]
    game.prizeCards = tuple(
        _deserializeCard(card) for card in state["prizeDeck"]
    )
    game.round = state["round"]
    game.currentPlayer = game.players[state["currentPlayer"]]
    winner = state["winner"]
    game.winner = game.players[winner] if winner is not None else None
