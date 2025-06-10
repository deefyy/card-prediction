import cv2
import os
import argparse

from src.vision.card_recognizer import CardRecognizer
from src.logic.poker_logic import calculate_equity as calculate_poker_equity
from src.logic.blackjack_logic import get_basic_strategy_move, calculate_win_probability as calculate_blackjack_win_prob
from src.llm.llm_coach import get_poker_advice, get_blackjack_advice
import src.config as config

def assign_poker_cards(detections):
    if len(detections) < 2:
        return [], [d['label'] for d in detections]
    detections.sort(key=lambda d: (d['box'][1] + d['box'][3]) / 2, reverse=True)
    player_detections = detections[:2]
    table_detections = detections[2:]
    table_detections.sort(key=lambda d: d['box'][0])
    return [d['label'] for d in player_detections], [d['label'] for d in table_detections]

def assign_blackjack_cards(detections):
    if not detections:
        return [], []
    detections.sort(key=lambda d: (d['box'][1] + d['box'][3]) / 2, reverse=True)
    
    player_cards = []
    dealer_cards = []
    
    if len(detections) < 2:
        return [d['label'] for d in detections], []
        
    hand_threshold_y = (detections[0]['box'][1] + detections[0]['box'][3]) / 2
    hand_threshold_y -= 50

    for det in detections:
        if (det['box'][1] + det['box'][3]) / 2 > hand_threshold_y:
            player_cards.append(det['label'])
        else:
            dealer_cards.append(det['label'])
            
    return player_cards, dealer_cards

def draw_analysis_on_image(image, detections, player_cards):
    output_image = image.copy()
    for det in detections:
        box = list(map(int, det['box']))
        label = det['label']
        color = (255, 200, 0)
        if label in player_cards:
            color = (0, 255, 0)
        cv2.rectangle(output_image, (box[0], box[1]), (box[2], box[3]), color, 2)
        cv2.putText(output_image, f"{label}", (box[0], box[1] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
    return output_image

def filter_unique_detections(detections):
    unique_detections = []
    seen_labels = set()
    for det in sorted(detections, key=lambda x: x['conf'], reverse=True):
        if det['label'] not in seen_labels:
            unique_detections.append(det)
            seen_labels.add(det['label'])
    return unique_detections

def analyze_poker_frame(frame, recognizer):
    detections, _ = recognizer.recognize(frame)
    unique_detections = filter_unique_detections(detections)
    if not unique_detections: return None
    my_cards, community_cards = assign_poker_cards(unique_detections)
    
    print("\n--- ANALIZA POKERA ---")
    print(f"Ręka: {my_cards}, Stół: {community_cards}")
    
    equity = calculate_poker_equity(my_cards, community_cards, config.POKER_NUM_OPPONENTS, config.POKER_SIMULATIONS_COUNT)
    game_stage = "Pre-flop" if not community_cards else "Flop" if len(community_cards) <= 3 else "Turn" if len(community_cards) == 4 else "River"
    print(f"Szansa na wygraną: {equity:.2%}")

    print("\nPytam trenera AI o poradę dla POKERA...")
    advice = get_poker_advice(my_cards, community_cards, equity, config.POKER_NUM_OPPONENTS, game_stage)
    print("\n--- PORADA TRENERA AI ---\n" + advice)
    
    return draw_analysis_on_image(frame, unique_detections, my_cards)

def analyze_blackjack_frame(frame, recognizer):
    detections, _ = recognizer.recognize(frame)
    unique_detections = filter_unique_detections(detections)
    if not unique_detections: return None
    player_cards, dealer_cards = assign_blackjack_cards(unique_detections)

    if not player_cards or not dealer_cards:
        print("Nie można rozpoznać ręki gracza i krupiera.")
        return None
        
    dealer_up_card = dealer_cards[0]
    
    print("\n--- ANALIZA BLACKJACKA ---")
    print(f"Twoja ręka: {player_cards}, Krupier pokazuje: {dealer_up_card}")
    
    move_str, move_code, player_value = get_basic_strategy_move(player_cards, dealer_up_card)
    win_prob = calculate_blackjack_win_prob(player_cards, dealer_up_card, move_code)
    
    print(f"Twoja wartość: {player_value}, Rekomendowany ruch: {move_str}")
    print(f"Szansa na wygraną przy tym ruchu: {win_prob:.2%}")

    print("\nPytam trenera AI o poradę dla BLACKJACKA...")
    advice = get_blackjack_advice(player_cards, dealer_up_card, move_str, player_value)
    print("\n--- PORADA TRENERA AI ---\n" + advice)

    return draw_analysis_on_image(frame, unique_detections, player_cards)

def main():
    parser = argparse.ArgumentParser(description="Analizator gier karcianych AI.")
    parser.add_argument('game', type=str, choices=['poker', 'blackjack'], help="Wybierz grę do analizy.")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--image', type=str, help="Ścieżka do obrazu do analizy.")
    group.add_argument('--camera', action='store_true', help="Użyj kamery na żywo.")
    parser.add_argument('--no-preview', action='store_true', help="Nie wyświetlaj okna z podglądem wyniku.")
    args = parser.parse_args()

    model_path = os.path.join('models', config.MODEL_PATH)
    try:
        recognizer = CardRecognizer(model_path)
    except IOError as e:
        print(f"!!! Błąd krytyczny: {e}")
        return
    
    analysis_func = analyze_poker_frame if args.game == 'poker' else analyze_blackjack_frame

    if args.image:
        if not os.path.exists(args.image):
            print(f"Błąd: Plik obrazu '{args.image}' nie został znaleziony.")
            return
        frame = cv2.imread(args.image)
        result_image = analysis_func(frame, recognizer)
        if result_image is not None:
            cv2.imwrite(config.OUTPUT_IMAGE_NAME, result_image)
            if not args.no_preview:
                cv2.imshow('Analysis Result', result_image)
                cv2.waitKey(0)
    elif args.camera:
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            print("Błąd: Nie można otworzyć kamery.")
            return
        
        while True:
            ret, frame = cap.read()
            if not ret: break
            cv2.imshow('Live Analyzer', frame)
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'): break
            if key == ord(' '):
                result_image = analysis_func(frame, recognizer)
                if result_image is not None and not args.no_preview:
                    cv2.imshow('Analysis Result', result_image)
        cap.release()
    cv2.destroyAllWindows()

if __name__ == '__main__':
    main()