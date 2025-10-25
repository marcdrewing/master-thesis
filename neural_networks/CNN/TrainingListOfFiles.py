import os
import torch
import pandas as pd
from joblib import dump, load
from model import CNNPeakModel
from data_prep import prepare_data
from dataset import create_dataloaders
from train import train_model

# --------------------------------------------------
# 1. Konfiguration
# --------------------------------------------------
DATA_PATHS = [
    "250820_EC32_Messung1_marked_peaks.csv",
    "250820_EC32_Messung4_marked_peaks.csv",
    #"250826_EC33_Messung1_marked_peaks.csv",
    #"250826_EC33_Messung2_marked_peaks.csv",
    "250826_EC33_Messung3_marked_peaks.csv"
    #"250811_QM1_Messung1_marked_peaks.csv",
    #"250811_QM1_Messung2_marked_peaks.csv",
    #"250812_QM1_Messung3_marked_peaks.csv",
    #"250812_QM1_Messung4_marked_peaks.csv",
    #"250813_QM1_Messung5_marked_peaks.csv",
    #"250818_EC22_Messung1_marked_peaks.csv",
    #"250818_EC22_Messung2_marked_peaks.csv",
    #"250818_EC22_Messung3_marked_peaks.csv",
    #"250819_EC22_Messung4_marked_peaks.csv",
    #"250819_EC22_Messung5_marked_peaks.csv"
]

MODEL_PATH = "model_weights_seqLen_100_betterData.pth"
SCALER_X_PATH = "scaler_x.pkl"
SCALER_Y_PATH = "scaler_y.pkl"
SEQ_LEN = 100
EPOCHS = 50
LR = 1e-4
BATCH_SIZE = 128
USE_GPU = True

features = ["C_CH0", "pressure", "extractionVoltage"]
target = ["currentPeak"]

if USE_GPU:
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print("Verwende" + str(device)+" für die Berechnungen")


######Modell laden####################################

model = CNNPeakModel(
    input_size=len(features),
    output_size=1,
    dropout=0.3
)

if os.path.exists(MODEL_PATH):
    print("Vorhandenes Modell gefunden – lade Gewichte und trainiere weiter.")
    model.load_state_dict(torch.load(MODEL_PATH))
    CONTINUE_TRAINING = True
else:
    print("Kein trainiertes Modell gefunden – neues Modell wird erstellt.")
    CONTINUE_TRAINING = False


####### Scaler laden oder neu erstellen  #############
if os.path.exists(SCALER_X_PATH) and os.path.exists(SCALER_Y_PATH):
    print("Vorhandene Scaler gefunden – lade Skalierer...")
    scaler_x = load(SCALER_X_PATH)
    scaler_y = load(SCALER_Y_PATH)
    USE_EXISTING_SCALERS = True
else:
    print("Keine Scaler gefunden – neue werden beim ersten Datensatz erstellt.")
    scaler_x = None
    scaler_y = None
    USE_EXISTING_SCALERS = False

########## Datensätze antrainieren ########################

for DataSet in DATA_PATHS:
    print(f"Lade Datensatz: {DataSet}")
    df = pd.read_csv(DataSet)

    X_train, X_test, y_train, y_test, scaler_x, scaler_y = prepare_data(
        df,
        features,
        target,
        seq_len=SEQ_LEN,
        existing_scaler_x=scaler_x if USE_EXISTING_SCALERS else None,
        existing_scaler_y=scaler_y if USE_EXISTING_SCALERS else None
    )


    if not USE_EXISTING_SCALERS:
        dump(scaler_x, SCALER_X_PATH)
        dump(scaler_y, SCALER_Y_PATH)
        print("Neue Scaler gespeichert.")
        USE_EXISTING_SCALERS = True


    train_loader, test_loader = create_dataloaders(
        X_train, y_train, X_test, y_test, batch_size=BATCH_SIZE
    )

    train_model(
        model,
        train_loader,
        test_loader,
        epochs=EPOCHS,
        lr=LR,
        save_path=MODEL_PATH,
        continue_training=CONTINUE_TRAINING,
        use_gpu=USE_GPU
    )

    print("Training für aktuellen Datensatz abgeschlossen. Modell und Scaler wurden gespeichert.")

print("\nTraining über alle Datensätze abgeschlossen.")
print("Modell und Scaler wurden gespeichert.")
