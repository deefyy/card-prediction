import random

RANKS = '23456789TJQKA'
SUITS = 'HDCS'
RANK_VALUES = {rank: i for i, rank in enumerate(RANKS)}

def _create_deck():
    return [rank + suit for rank in RANKS for suit in SUITS]

def _evaluate_hand(hand_7_cards):
    ranks = sorted([RANK_VALUES[card[0]] for card in hand_7_cards], reverse=True)
    suits = [card[1] for card in hand_7_cards]
    
    is_flush = None
    for suit in SUITS:
        if suits.count(suit) >= 5:
            is_flush = suit
            break

    flush_ranks = sorted([RANK_VALUES[card[0]] for card in hand_7_cards if is_flush and card[1] == is_flush], reverse=True)
    is_straight, straight_top_rank = _is_straight(flush_ranks if is_flush else ranks)

    if is_flush and is_straight:
        return (8, straight_top_rank)

    rank_counts = {rank: ranks.count(rank) for rank in set(ranks)}
    counts = sorted(rank_counts.items(), key=lambda item: (item[1], item[0]), reverse=True)
    
    if counts[0][1] == 4:
        return (7, [counts[0][0]] + [r for r in ranks if r != counts[0][0]][:1])

    if counts[0][1] == 3 and counts[1][1] >= 2:
        return (6, [counts[0][0], counts[1][0]])

    if is_flush:
        return (5, flush_ranks[:5])

    if is_straight:
        return (4, straight_top_rank)

    if counts[0][1] == 3:
        return (3, [counts[0][0]] + [r for r in ranks if r != counts[0][0]][:2])

    if counts[0][1] == 2 and counts[1][1] == 2:
        return (2, [counts[0][0], counts[1][0]] + [r for r in ranks if r not in [counts[0][0], counts[1][0]]][:1])

    if counts[0][1] == 2:
        return (1, [counts[0][0]] + [r for r in ranks if r != counts[0][0]][:3])
        
    return (0, ranks[:5])

def _is_straight(ranks):
    unique_ranks = sorted(list(set(ranks)), reverse=True)
    if len(unique_ranks) < 5:
        return False, None
    
    if set(unique_ranks) >= {12, 0, 1, 2, 3}:
        return True, 3

    for i in range(len(unique_ranks) - 4):
        if unique_ranks[i] - unique_ranks[i+4] == 4:
            return True, unique_ranks[i]
            
    return False, None

def calculate_equity(my_cards, community_cards, num_opponents=1, simulations=10000):
    
    normalize = lambda c: ('T' + c[2]) if c.startswith('10') else c
    my_cards = [normalize(c) for c in my_cards]
    community_cards = [normalize(c) for c in community_cards]
    
    deck = _create_deck()
    
    for card in my_cards + community_cards:
        if card in deck:
            deck.remove(card)
            
    wins = 0
    ties = 0
    for _ in range(simulations):
        sim_deck = deck[:]
        random.shuffle(sim_deck)
        
        opponents_hands = [sim_deck[i*2:i*2+2] for i in range(num_opponents)]
        
        cards_to_draw = 5 - len(community_cards)
        remaining_community = sim_deck[num_opponents*2 : num_opponents*2 + cards_to_draw]
        
        my_hand_7 = my_cards + community_cards + remaining_community
        my_score = _evaluate_hand(my_hand_7)
        
        is_winner = True
        is_tie = False
        
        for opp_hand in opponents_hands:
            opp_hand_7 = opp_hand + community_cards + remaining_community
            opp_score = _evaluate_hand(opp_hand_7)
            if opp_score > my_score:
                is_winner = False
                break
            if opp_score == my_score:
                is_tie = True

        if is_winner:
            if is_tie:
                ties += 1
            else:
                wins += 1
            
    return wins / simulations + (ties / simulations) / (num_opponents + 1)