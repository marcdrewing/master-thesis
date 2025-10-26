import torch
import pandas as pd
import numpy as np
from joblib import load
from model import CNNPeakModel
from evaluate import evaluate_model


DATA_PATH = "250826_EC33_Messung2_marked_peaks.csv"  # Pfad zur CSV-Datei
MODEL_PATH = "model_weights_seqLen_5_betterData.pth"                     # trainiertes Modell
SCALER_X_PATH = "scaler_x.pkl"
SCALER_Y_PATH = "scaler_y.pkl"
SEQ_LEN = 5                                        # gleiche Länge wie beim Training

# Spaltennamen (müssen exakt mit Training übereinstimmen)
FEATURES = ["C_CH0", "pressure", "extractionVoltage"]
TARGET = ["currentPeak"]


print(f"Lade Datensatz: {DATA_PATH}")
df = pd.read_csv(DATA_PATH)

print("Lade Skalierer...")
scaler_x = load(SCALER_X_PATH)
scaler_y = load(SCALER_Y_PATH)

print("Skaliere Daten...")
X_scaled = scaler_x.transform(df[FEATURES])
y_scaled = scaler_y.transform(df[TARGET])


def create_sequences(X, y, seq_length=SEQ_LEN):
    Xs, ys = [], []
    for i in range(len(X) - seq_length):
        Xs.append(X[i:(i + seq_length)])
        ys.append(y[i + seq_length-1])
    return np.array(Xs), np.array(ys)

X_seq, y_seq = create_sequences(X_scaled, y_scaled)

print(f"Erstellte Sequenzen: {X_seq.shape[0]} Samples mit je {SEQ_LEN} Zeitschritten")


print("Initialisiere Modell...")
model = CNNPeakModel(
    input_size=len(FEATURES),
    output_size=1,
    dropout=0.3
)

print("Lade trainierte Gewichte...")
model.load_state_dict(torch.load(MODEL_PATH))
model.eval()

print("Modell erfolgreich geladen.")

print("Starte Evaluation...")
evaluate_model(model, X_seq, y_seq, scaler_y)

print("Fertig.")

