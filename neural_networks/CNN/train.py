import torch
import torch.nn as nn
import os

def train_model(model, train_loader, test_loader, epochs=30, lr=1e-3,
                save_path="model_weights.pth", continue_training=False,
                use_gpu=True):
    
    # Gerät wählen
    if use_gpu and torch.cuda.is_available():
        device = torch.device("cuda")
        print("Verwende GPU (CUDA) für das Training.")
    else:
        device = torch.device("cpu")
        if use_gpu and not torch.cuda.is_available():
            print("WARNUNG: USE_GPU=True, aber keine CUDA-GPU verfügbar. Verwende CPU.")
        else:
            print("Verwende CPU für das Training.")

    model = model.to(device)
    criterion = nn.MSELoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=lr)

    if continue_training and os.path.exists(save_path):
        print(f"Lade bestehende Modellgewichte aus '{save_path}' ...")
        model.load_state_dict(torch.load(save_path, map_location=device))
        print("Modell erfolgreich geladen – Training wird fortgesetzt.")
    elif continue_training:
        print(f"Warnung: continue_training=True, aber '{save_path}' wurde nicht gefunden.")
        print("Training startet neu.")
    else:
        print("Starte neues Training.")

    for epoch in range(epochs):
        model.train()
        running_loss = 0.0

        for X_batch, y_batch in train_loader:
            X_batch, y_batch = X_batch.to(device), y_batch.to(device)

            optimizer.zero_grad()
            output = model(X_batch)
            loss = criterion(output, y_batch)
            loss.backward()
            optimizer.step()
            running_loss += loss.item()

        model.eval()
        val_loss = 0.0
        with torch.no_grad():
            for X_val, y_val in test_loader:
                X_val, y_val = X_val.to(device), y_val.to(device)
                preds = model(X_val)
                loss = criterion(preds, y_val)
                val_loss += loss.item()

        print(f"Epoch [{epoch+1}/{epochs}] "
              f"Train Loss: {running_loss/len(train_loader):.4f} "
              f"Val Loss: {val_loss/len(test_loader):.4f}")

    torch.save(model.state_dict(), save_path)
    print(f"Modell gespeichert unter: {save_path}")
