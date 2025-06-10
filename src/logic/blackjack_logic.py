import random
import src.config as config

CARD_VALUES = {
    '2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9, 
    'T': 10, 'J': 10, 'Q': 10, 'K': 10, 'A': 11
}

STRATEGY_HARD = {
    17: 'S', 16: 'S', 15: 'S', 14: 'S', 13: 'S',
    12: {2: 'H', 3: 'H', 4: 'S', 5: 'S', 6: 'S', 7: 'H'},
    11: 'D', 10: 'D', 9: {2: 'H', 3: 'D', 4: 'D', 5: 'D', 6: 'D', 7: 'H'},
    8: 'H',
}

STRATEGY_SOFT = {
    20: 'S', 19: 'S',
    18: {2: 'DS', 3: 'DS', 4: 'DS', 5: 'DS', 6: 'DS', 7: 'S', 8: 'S', 9: 'H'},
    17: 'H', 16: 'H', 15: 'H', 14: 'H', 13: 'H',
}

STRATEGY_PAIRS = {
    'A': 'P', 'T': 'S',
    '9': {2: 'P', 3: 'P', 4: 'P', 5: 'P', 6: 'P', 7: 'S', 8: 'P', 9: 'P', 10: 'S'},
    '8': 'P', '7': 'P', '6': 'P', '5': 'D', '4': 'H',
    '3': {2: 'P', 3: 'P', 4: 'P', 5: 'P', 6: 'P', 7: 'P', 8: 'H'},
    '2': {2: 'P', 3: 'P', 4: 'P', 5: 'P', 6: 'P', 7: 'P', 8: 'H'},
}

MOVE_MAP = {
    'S': 'Stand (Nie dobieraj)', 'H': 'Hit (Dobierz)', 'D': 'Double Down (Podwój)',
    'P': 'Split (Rozdziel)', 'DS': 'Double Down, jeśli można, inaczej Stand'
}

def _create_deck():
    ranks = '23456789TJQKA'
    suits = 'HDCS'
    return [r + s for r in ranks for s in suits] * 4

def normalize_card(card):
    if card.startswith('10'): return 'T' + card[2:]
    return card

def calculate_hand_value(hand):
    hand = [normalize_card(c) for c in hand]
    value = 0
    num_aces = 0
    for card in hand:
        rank = card[0]
        value += CARD_VALUES.get(rank, 0)
        if rank == 'A': num_aces += 1
    while value > 21 and num_aces > 0:
        value -= 10
        num_aces -= 1
    return value

def get_basic_strategy_move(player_hand, dealer_up_card):
    player_hand = [normalize_card(c) for c in player_hand]
    dealer_up_card = normalize_card(dealer_up_card)
    player_value = calculate_hand_value(player_hand)
    dealer_value = CARD_VALUES.get(dealer_up_card[0], 0)
    is_pair = len(player_hand) == 2 and player_hand[0][0] == player_hand[1][0]
    is_soft = 'A' in [c[0] for c in player_hand] and player_value - 11 <= 10

    move_code = 'H'
    if is_pair: move_code = STRATEGY_PAIRS.get(player_hand[0][0], 'H')
    elif is_soft and player_value > 12: move_code = STRATEGY_SOFT.get(player_value, 'H')
    else: move_code = STRATEGY_HARD.get(player_value, 'S')

    if isinstance(move_code, dict): move_code = move_code.get(dealer_value, 'H')
    if player_value >= 17 and not is_soft: move_code = 'S'
    if player_value > 21: move_code = 'S'

    return MOVE_MAP.get(move_code), move_code, player_value

def _play_dealer_hand(dealer_hand, deck):
    hand = list(dealer_hand)
    while True:
        score = calculate_hand_value(hand)
        is_soft = 'A' in [c[0] for c in hand] and score - 11 <= 10
        if score > 17 or (score == 17 and not (is_soft and config.DEALER_HITS_ON_SOFT_17)):
            break
        hand.append(deck.pop())
    return calculate_hand_value(hand)

def _play_player_hand(player_hand, deck, move_code):
    hand = list(player_hand)
    if move_code in ['H', 'D', 'DS']:
        hand.append(deck.pop())
    return calculate_hand_value(hand)

def _compare_hands(player_score, dealer_score):
    if player_score > 21: return 'loss'
    if dealer_score > 21 or player_score > dealer_score: return 'win'
    if player_score == dealer_score: return 'push'
    return 'loss'

def calculate_win_probability(player_hand, dealer_up_card, move_code):
    player_hand = [normalize_card(c) for c in player_hand]
    dealer_up_card = normalize_card(dealer_up_card)
    
    wins, pushes, losses = 0.0, 0.0, 0.0
    simulations = 100000

    for _ in range(simulations):
        deck = _create_deck()
        visible_cards = player_hand + [dealer_up_card]
        for card in visible_cards:
            if card in deck: deck.remove(card)
        random.shuffle(deck)

        if move_code == 'P':
            hand1_deck = deck[::2]
            hand2_deck = deck[1::2]
            
            player_score1 = _play_player_hand([player_hand[0]], hand1_deck, 'H')
            player_score2 = _play_player_hand([player_hand[1]], hand2_deck, 'H')
            
            dealer_hand = [dealer_up_card]
            dealer_score = _play_dealer_hand(dealer_hand, hand1_deck + hand2_deck)

            result1 = _compare_hands(player_score1, dealer_score)
            result2 = _compare_hands(player_score2, dealer_score)

            for result in [result1, result2]:
                if result == 'win': wins += 0.5
                elif result == 'push': pushes += 0.5
                else: losses += 0.5
        else:
            player_final_score = _play_player_hand(player_hand, deck, move_code)
            dealer_hand = [dealer_up_card]
            dealer_score = _play_dealer_hand(dealer_hand, deck)
            
            result = _compare_hands(player_final_score, dealer_score)
            if result == 'win': wins += 1
            elif result == 'push': pushes += 1
            else: losses += 1
            
    return wins / simulations