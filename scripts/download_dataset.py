from roboflow import Roboflow

ROBOFLOW_API_KEY = "ROBOFLOW_API_KEY"

if ROBOFLOW_API_KEY == "TWOJ_KLUCZ_API_TUTAJ":
    print("!!! BŁĄD: Musisz wkleić swój klucz API z Roboflow w pliku download_dataset.py")
else:
    try:
        rf = Roboflow(api_key=ROBOFLOW_API_KEY)
        project = rf.workspace("augmented-startups").project("playing-cards-ow27d")

        dataset = project.version(1).download("yolov8")
        
        print(f"Dataset pobrany i zapisany w folderze: {dataset.location}")
        print("Plik konfiguracyjny 'data.yaml' znajduje się w tym folderze.")
        print("Teraz możesz uruchomić skrypt 'train_yolo.py'.")

    except Exception as e:
        print(f"Wystąpił błąd podczas pobierania danych: {e}")
        print("Upewnij się, że Twój klucz API jest poprawny i masz połączenie z internetem.")