import torch
import matplotlib.pyplot as plt

def evaluate_model(model, X_test, y_test, scaler_y):
    model.eval()
    with torch.no_grad():
        y_pred_scaled = model(torch.tensor(X_test, dtype=torch.float32)).numpy()

    y_pred = scaler_y.inverse_transform(y_pred_scaled)
    y_true = scaler_y.inverse_transform(y_test)

    plt.figure(figsize=(9, 5))
    plt.plot(y_true, label="Echter currentPeak")
    plt.plot(y_pred, label="Erkannter currentPeak")
    plt.title("Verschleißerkennung mit LSTM")
    plt.legend()
    plt.tight_layout()
    plt.show()
