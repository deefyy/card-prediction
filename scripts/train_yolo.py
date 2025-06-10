from ultralytics import YOLO
import os

def train_model():
    data_yaml_path = os.path.join('Playing-Cards-1', 'data.yaml')
    if not os.path.exists(data_yaml_path):
        print(f"Błąd: Plik '{data_yaml_path}' nie został znaleziony.")
        return

    model = YOLO('yolov8n.pt')

    print(">>> Rozpoczynam PRZYSPIESZONY trening modelu YOLOv8...")

    results = model.train(
        data=data_yaml_path,
        epochs=50,
        imgsz=640,
        batch=32,
        workers=8,
        cache=True,
        project='runs/detect',
        name='cards_yolov8_fast_training'
    )

    print(">>> Trening zakończony!")
    print(f"Wytrenowany model zapisano w: {results.save_dir}")

if __name__ == '__main__':
    train_model()