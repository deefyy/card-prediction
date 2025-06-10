# src/vision/card_recognizer.py
from ultralytics import YOLO
import src.config as config  # Importujemy cały moduł config

class CardRecognizer:
    def __init__(self, model_path):
        try:
            self.model = YOLO(model_path)
        except Exception as e:
            raise IOError(f"Nie można załadować modelu z '{model_path}'. Upewnij się, że ścieżka jest poprawna. Błąd: {e}")

    def recognize(self, image):
        """
        Rozpoznaje karty, przekazując parametry z pliku konfiguracyjnego
        bezpośrednio do metody model.predict().
        """
        # --- GŁÓWNA ZMIANA JEST TUTAJ ---
        # Wywołujemy predict z parametrami załadowanymi z naszego pliku config.py
        results = self.model.predict(
            source=image,
            imgsz=config.IMG_SIZE,
            conf=config.CONFIDENCE_THRESHOLD,
            iou=config.IOU_THRESHOLD,
            device=config.DEVICE,
            augment=config.AUGMENT,
            save=config.SAVE_PREDICT,
            show=config.SHOW_PREDICT,
            verbose=False # Pozostawiamy wyłączone, aby uniknąć bałaganu w konsoli
        )
        
        detections = []
        for result in results:
            boxes = result.boxes
            # Używamy progu z configu, chociaż predict już go zastosował,
            # to dobra praktyka dla pewności.
            for box in boxes:
                if box.conf[0] > config.CONFIDENCE_THRESHOLD:
                    class_id = int(box.cls[0])
                    class_name = self.model.names[class_id]
                    detection_info = {
                        'box': box.xyxy[0].tolist(),
                        'label': class_name,
                        'conf': box.conf[0].item()
                    }
                    detections.append(detection_info)
                    
        return detections, results