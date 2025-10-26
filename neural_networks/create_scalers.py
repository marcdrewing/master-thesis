import os
import pandas as pd
from joblib import dump
from sklearn.preprocessing import MinMaxScaler

DATA_PATHS = [
    "250820_EC32_Messung1_marked_peaks.csv",
    "250820_EC32_Messung4_marked_peaks.csv",
    "250826_EC33_Messung1_marked_peaks.csv",
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

FEATURES = ["C_CH0", "pressure", "extractionVoltage"]
TARGET = ["currentPeak"]

SCALER_X_PATH = "scaler_x.pkl"
SCALER_Y_PATH = "scaler_y.pkl"


def main():

    global_feature_min = pd.Series(float("inf"), index=FEATURES)
    global_feature_max = pd.Series(float("-inf"), index=FEATURES)
    global_target_min = pd.Series(float("inf"), index=TARGET)
    global_target_max = pd.Series(float("-inf"), index=TARGET)

    for path in DATA_PATHS:
        if not os.path.exists(path):
            print(f"Datei nicht gefunden, übersprungen: {path}")
            continue

        df = pd.read_csv(path)
        missing = [c for c in FEATURES + TARGET if c not in df.columns]
        if missing:
            print(f"Fehlende Spalten in {path}: {missing} – übersprungen.")
            continue

        feature_min = df[FEATURES].min()
        feature_max = df[FEATURES].max()
        target_min = df[TARGET].min()
        target_max = df[TARGET].max()

        global_feature_min = pd.concat([global_feature_min, feature_min], axis=1).min(axis=1)
        global_feature_max = pd.concat([global_feature_max, feature_max], axis=1).max(axis=1)
        global_target_min = pd.concat([global_target_min, target_min], axis=1).min(axis=1)
        global_target_max = pd.concat([global_target_max, target_max], axis=1).max(axis=1)

    print("Globale Wertebereiche gefunden.\n")

    fit_features = pd.DataFrame([global_feature_min, global_feature_max])
    fit_targets = pd.DataFrame([global_target_min, global_target_max])

    scaler_x = MinMaxScaler().fit(fit_features)
    scaler_y = MinMaxScaler().fit(fit_targets)

    dump(scaler_x, SCALER_X_PATH)
    dump(scaler_y, SCALER_Y_PATH)

    print("Scaler erfolgreich erstellt und gespeichert.")
    print(f"  Eingabebereich: {SCALER_X_PATH}")
    print(f"  Zielbereich:   {SCALER_Y_PATH}\n")

    print("Wertebereiche (globales Min → globales Max):")
    for f in FEATURES:
        print(f"  {f:25s}: {global_feature_min[f]:.4e} → {global_feature_max[f]:.4e}")
    for t in TARGET:
        print(f"  {t:25s}: {global_target_min[t]:.4e} → {global_target_max[t]:.4e}")



if __name__ == "__main__":
    main()
