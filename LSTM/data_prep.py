import numpy as np
from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import train_test_split


def create_sequences(X, y, seq_length=50):
    Xs, ys = [], []
    for i in range(len(X) - seq_length):
        Xs.append(X[i:(i + seq_length)])
        ys.append(y[i + seq_length-1])
    return np.array(Xs), np.array(ys)


def prepare_data(df, features, target, seq_len=50,
                 existing_scaler_x=None, existing_scaler_y=None,
                 test_size=0.2, shuffle=False):

    if existing_scaler_x is not None and existing_scaler_y is not None:
        print("Verwende vorhandene Scaler.")
        scaler_x = existing_scaler_x
        scaler_y = existing_scaler_y
        X_scaled = scaler_x.transform(df[features])
        y_scaled = scaler_y.transform(df[target])
    else:
        print("Erstelle neue Scaler.")
        scaler_x = MinMaxScaler()
        scaler_y = MinMaxScaler()
        X_scaled = scaler_x.fit_transform(df[features])
        y_scaled = scaler_y.fit_transform(df[target])


    X_seq, y_seq = create_sequences(X_scaled, y_scaled, seq_len)


    X_train, X_test, y_train, y_test = train_test_split(
        X_seq, y_seq, test_size=test_size, shuffle=shuffle
    )

    return X_train, X_test, y_train, y_test, scaler_x, scaler_y
