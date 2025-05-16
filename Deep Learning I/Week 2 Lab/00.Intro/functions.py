import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
import matplotlib.pyplot as plt

def load_and_preprocess_data(file_path, seq_length=3):
    # Load the data
    df = pd.read_csv(file_path, parse_dates=['Month'], index_col='Month')

    # Normalize the data
    scaler = MinMaxScaler()
    scaled_data = scaler.fit_transform(df)

    # Create sequences
    X, y = [], []
    for i in range(len(scaled_data) - seq_length):
        X.append(scaled_data[i:(i + seq_length), 0])
        y.append(scaled_data[i + seq_length, 0])
    X, y = np.array(X), np.array(y)

    # Split the data
    train_size = int(len(X) * 0.7)
    X_train, X_test = X[:train_size], X[train_size:]
    y_train, y_test = y[:train_size], y[train_size:]

    # Reshape input to be [samples, time steps, features]
    X_train = np.reshape(X_train, (X_train.shape[0], X_train.shape[1], 1))
    X_test = np.reshape(X_test, (X_test.shape[0], X_test.shape[1], 1))

    return X_train, X_test, y_train, y_test, scaler

def plot_results(history, y_train_inv, train_predict, y_test_inv, test_predict):
    # Plot training and validation loss
    plt.figure(figsize=(12, 6))
    plt.plot(history.history['loss'], label='Train Loss', color='blue')
    plt.plot(history.history['val_loss'], label='Validation Loss', color='orange')
    plt.title('Training and Validation Loss Over Epochs')
    plt.xlabel('Epochs')
    plt.ylabel('Loss')
    plt.legend()
    plt.grid(True)
    plt.show()

    # Plot actual vs predicted values
    plt.figure(figsize=(12, 6))
    plt.plot(y_train_inv, label='Actual Train', marker='o', color='blue')
    plt.plot(train_predict, label='Predicted Train', marker='x', color='orange')
    plt.plot(np.arange(len(y_train_inv), len(y_train_inv) + len(y_test_inv)), y_test_inv, label='Actual Test', marker='o', color='green')
    plt.plot(np.arange(len(y_train_inv), len(y_train_inv) + len(y_test_inv)), test_predict, label='Predicted Test', marker='x', color='red')
    plt.title('Actual vs Predicted Values')
    plt.xlabel('Time Step')
    plt.ylabel('Number of Passengers')
    plt.legend()
    plt.grid(True)
    plt.show()


def calculate_rmse(train_predict, y_train_inv, test_predict, y_test_inv):
    train_rmse = np.sqrt(np.mean((train_predict - y_train_inv)**2))
    test_rmse = np.sqrt(np.mean((test_predict - y_test_inv)**2))
    print(f'Train RMSE: {train_rmse:.3f}')
    print(f'Test RMSE: {test_rmse:.3f}')
    return train_rmse, test_rmse