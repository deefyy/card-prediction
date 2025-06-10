import ollama
from src.config import OLLAMA_MODEL

def get_poker_advice(my_cards, community_cards, equity, num_opponents, game_stage):
    card_map = {
        'A': 'As', 'K': 'Król', 'Q': 'Dama', 'J': 'Walet', 'T': '10',
        'H': ' Kier', 'D': ' Karo', 'C': ' Trefl', 'S': ' Pik'
    }
    def translate_card(card):
        return card_map.get(card[0], card[0]) + card_map.get(card[1], card[1])
        
    my_cards_str = ", ".join(translate_card(c) for c in my_cards)
    community_cards_str = ", ".join(translate_card(c) for c in community_cards) if community_cards else "Brak"
    prompt = f"""Jesteś światowej klasy trenerem pokera Texas Hold'em. Analizujesz sytuację i udzielasz porady.
Sytuacja:
- Etap gry: {game_stage}
- Moje karty: {my_cards_str}
- Karty na stole: {community_cards_str}
- Liczba przeciwników: {num_opponents}
- Moja szansa na wygraną (equity): {equity:.1%}
Zadanie:
1. Analiza ręki: Jaka jest siła mojej ręki?
2. Zagrożenia: Jakie układy mogą mnie pokonać?
3. Rekomendacja: Jaką strategię przyjąć (agresywną, pasywną, spasować) i dlaczego?
"""
    try:
        response = ollama.chat(model=OLLAMA_MODEL, messages=[{'role': 'user', 'content': prompt}], options={'temperature': 0.5})
        return response['message']['content']
    except Exception as e:
        return f"Błąd komunikacji z Ollama dla modelu '{OLLAMA_MODEL}': {e}"

def get_blackjack_advice(player_hand, dealer_up_card, recommended_move, player_value):
    card_map = {
        'A': 'As', 'K': 'Król', 'Q': 'Dama', 'J': 'Walet', 'T': '10',
        'H': ' Kier', 'D': ' Karo', 'C': ' Trefl', 'S': ' Pik'
    }
    normalize = lambda c: ('T' + c[2]) if c.startswith('10') else c
    def translate_card(card):
        card = normalize(card)
        return card_map.get(card[0], card[0]) + card_map.get(card[1], card[1])

    player_hand_str = ", ".join(translate_card(c) for c in player_hand)
    dealer_card_str = translate_card(dealer_up_card)

    prompt = f"""Jesteś ekspertem od strategii w blackjacku. Wyjaśniasz graczowi, dlaczego dana decyzja jest poprawna.
Sytuacja:
- Moje karty: {player_hand_str} (wartość: {player_value})
- Odkryta karta krupiera: {dealer_card_str}
- Rekomendowany ruch (zgodnie ze strategią podstawową): {recommended_move}
Zadanie:
Wyjaśnij prostym językiem, dlaczego rekomendowany ruch jest najlepszy. Odnieś się do karty krupiera - czy jest ona dla niego 'słaba' (2-6) czy 'silna' (7-A)? Co to oznacza dla mojej decyzji?
"""
    try:
        response = ollama.chat(model=OLLAMA_MODEL, messages=[{'role': 'user', 'content': prompt}], options={'temperature': 0.5})
        return response['message']['content']
    except Exception as e:
        return f"Błąd komunikacji z Ollama dla modelu '{OLLAMA_MODEL}': {e}"