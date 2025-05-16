# Info:

# Author:
# Date

# Purpose:

# inputs:

# outputs:

# Version control:

#-- Import Libraries  -------------------------------
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import copy
#import math 
#from math import sqrt

# Creat signals -----------------------------------------------------------
freq = 1
ampl = 1
phi = 0

# datapoints
x = np.linspace(0, 50, 300)
#x = np.linspace(-np.pi, np.pi, 201)
y = ampl * np.sin(freq * x - phi)

# creat noise
np.random.seed(10)
noise = np.random.uniform(-0.3, 0.3, size = x.shape[0])
y_noisy = y + noise

# plot the clean and noisy signal
fig, ax = plt.subplots()
plt.plot(x, y)
plt.plot(x, y_noisy, 'r')




# creat n_sample by sample_len, both clean and noisy
n_samples = 100
sample_len = 400

clean_sig = np.zeros((n_samples, sample_len))
noisy_sig = np.zeros((n_samples, sample_len))

for i in range (n_samples):  # i=0
    
    rand = np.random.uniform (0, 1)
    freq = 1+rand
    ampl = 1 + np.random.uniform (0, 1)
    #phi = 0 + np.random.uniform (0, 5)
    
    x = np.linspace(0, 50, sample_len)
    x = x + np.random.uniform (-10, 10)
    
    clean_sig [i, :] = ampl * np.sin(freq * x)
    noisy_sig [i, :] = clean_sig [i, :] + np.random.uniform (-0.4, 0.4, size=len(x))
    


# plot the clean and noisy signal
sample = 77
fig, ax = plt.subplots()
plt.plot(x, clean_sig[sample, :])
plt.plot(x, noisy_sig[sample, :], 'r')


'''
# Feature Scaling--------------------------------------------------------------
#-- Normalize data manually
for i in range(noisy_sig.shape[0]):
    max_value = max(noisy_sig[i,:])
    noisy_sig[i,:] = noisy_sig[i,:]/max_value

    max_value = max(clean_sig[i,:])
    clean_sig[i,:] = clean_sig[i,:]/max_value

#-- use abs function
noisy_signals = np.abs(noisy_sig)
clean_signals = np.abs(clean_sig)
'''

noisy_signals = noisy_sig.copy()
clean_signals = clean_sig.copy()

#-- reshape (sample, length, featuers)
noisy_signals = noisy_signals.reshape(noisy_signals.shape[0],noisy_signals.shape[1],1)
clean_signals = clean_signals.reshape(clean_signals.shape[0],clean_signals.shape[1],1)

#-- Plot a sample signal
sample=0 # 0, 1, 2, 100
fig, ax = plt.subplots()
plt.plot (noisy_signals[sample,:,0], label="Noisy")
plt.plot (clean_signals[sample,:,0], label="Clean")
plt.ylabel("signal")
plt.xlabel("Data points (deg)")
plt.legend()
plt.show()



#-- Splitting the dataset into the Training set and Test set-------------------
from sklearn.model_selection import train_test_split

#-- randomly assign the train and test set, useing sklearn
x_train, x_test, y_train, y_test = train_test_split(
    noisy_signals, clean_signals, test_size=0.15)

#-- Plot a sample signal
ind=2
fig, ax = plt.subplots()
plt.plot (x_test[ind,:], label="Noisy")
plt.plot (y_test[ind,:], label="Clean")
plt.title('Training data noisy&clean')
plt.legend()
plt.show()



#==============================================================================
#-- Function 2 using Keras ====================================================
#==============================================================================
# Importing the Keras libraries and packages
from keras.models import Sequential
from keras.layers import Dense, LSTM, Dropout, GRU
from keras.layers import RepeatVector, TimeDistributed, Bidirectional


timesteps = x_train.shape[1]
No_of_features = x_train.shape[2]
hidden_nodes = 50
#num_layers = 1
No_epoch=10 
dropout = 0.0 # dropout rate, to simply forget some Neurons to avoid overfitting
learning_rate = 0.01
batch_size = 5
unit_type = "GRU" # "GRU" # "LSTM" #This to select the tyoe of units "LSTM" or "GRU"


# define model
rnn_model = Sequential()
rnn_model.add(Bidirectional(GRU(units = 100, return_sequences = True,
                    activation='relu', input_shape = (timesteps, No_of_features))))

rnn_model.add(GRU(10, activation='relu', return_sequences=True))

#rnn_model.add(RepeatVector(timesteps))

rnn_model.add(GRU(10, activation='relu', return_sequences=True))
rnn_model.add(GRU(100, activation='relu', return_sequences=True))
rnn_model.add(TimeDistributed(Dense(1)))
#rnn_model.add(Dense(units = 1, activation='relu'))

rnn_model.compile(optimizer='adam', loss='mean_absolute_error')
#rnn_model.summary()

rnn_model.fit(x_train, y_train, epochs = No_epoch, 
              batch_size = batch_size, verbose=2)

#-- Predict the output for test set
x_test_pred = rnn_model.predict(x_test, verbose=1)

#-- save the RNN model to be used later----------------------------------------
from keras.models import load_model
model_name = "LSTM_Auto_sine.h5"
rnn_model.save(model_name)

#-- Load the model
rnn_model2 = load_model(model_name)

x_test_pred = rnn_model2.predict(x_test, verbose=1)


#-- plot the test results--------------
ind = 0
fig, ax = plt.subplots()

plt.plot (x_test[ind,:,0], label="Noisy")
plt.plot (x_test_pred[ind,:,0], color='g', linewidth=2,  label="Pred")
plt.plot (y_test[ind,], color = "orange", linestyle=':', linewidth=1.5,\
          label="True Ind.")

plt.legend()
plt.xlabel ("Circumferential Locations (Degrees)")
plt.ylabel ("Distance (mm)")
plt.show()

#plt.savefig("x_test"+str(ind)+".tif", dpi=200, format='tif')






