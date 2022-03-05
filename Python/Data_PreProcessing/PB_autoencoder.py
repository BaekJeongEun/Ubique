import os
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import tensorflow as tf
from matplotlib import pyplot as plt
from sklearn.model_selection import train_test_split
from tensorflow.keras.optimizers import Adam
from tensorflow.keras import layers, losses
from tensorflow.keras.models import Model
from tensorflow.keras import layers, models
from tensorflow import keras
from keras.models import model_from_json

whole_data = np.loadtxt("ppg_bp_filtered.csv",delimiter=',', dtype=np.float32)
bp_data = whole_data[:,:2]
ppg_data = whole_data[:,2:]
ppg_data = (ppg_data-ppg_data.min())/(ppg_data.max()-ppg_data.min())
test_data = np.loadtxt("ppg_jeong_filtered.csv",delimiter=',', dtype=np.float32)
#ppg_data = (ppg_data-ppg_data.min())/(ppg_data.max()-ppg_data.min())
test_data = (test_data-test_data.min())/(test_data.max()-test_data.min())
test_ppg_data= test_data[:,2:]

LATENT_DIM = 32
SPLIT_RATE = 0.2
EPOCHS = 10
PPG_LENGTH = len(ppg_data[0])

ppg_file = open('ppg_bp_encoded_'+ str(LATENT_DIM) +'.csv','a')
test_file = open('ppg_jeong_encoded_'+ str(LATENT_DIM) +'.csv','a')

checkpoint_path = "ppg_bp_aae/pba.ckpt"
checkpoint_dir = os.path.dirname(checkpoint_path)
cp_callback = tf.keras.callbacks.ModelCheckpoint(filepath=checkpoint_path, save_weights_only=True, verbose=1)

#pt, pv = train_test_split(ppg_data, test_size = SPLIT_RATE, random_state = 123)

class Autoencoder(Model):
    def __init__(self, latent_dim):
        super(Autoencoder, self).__init__()
        self.latent_dim = latent_dim   
        self.encoder = tf.keras.Sequential([
            layers.Dense(1024, activation=tf.nn.swish),
            layers.Dense(512, activation=tf.nn.swish),
            layers.Dense(latent_dim),
        ])
        self.decoder = tf.keras.Sequential([
            layers.Dense(512, activation=tf.nn.swish),
            layers.Dense(1024, activation=tf.nn.swish),
            layers.Dense(PPG_LENGTH, activation='sigmoid'),
        ])

    def call(self, x):
        encoded = self.encoder(x)
        decoded = self.decoder(encoded)
        return decoded

autoencoder = Autoencoder(LATENT_DIM)

autoencoder.compile(optimizer=Adam(lr=1.46e-4), loss=losses.MeanSquaredError())
autoencoder.fit(ppg_data, ppg_data, epochs=EPOCHS, shuffle=True) #,validation_data=(pv, pv))
autoencoder.summary()

encoded_val_data = autoencoder.encoder(ppg_data).numpy()
decoded_val_data = autoencoder.decoder(encoded_val_data).numpy()

x_axis = range(len(ppg_data[0]))
plt.plot(x_axis, decoded_val_data[5])
plt.plot(x_axis, ppg_data[5])
plt.show()

encoded_data = autoencoder.encoder(ppg_data).numpy()
test_encoded_data = autoencoder.encoder(test_ppg_data).numpy()

for i in range(len(encoded_data)):
    tmp_list = []
    tmp_list.append(bp_data[i].tolist()[0])
    tmp_list.append(bp_data[i].tolist()[1])

    for d in encoded_data[i] :
        tmp_list.append(d)

    rtn = str(tmp_list)[1:-1]
    ppg_file.write(str.format(rtn) + "\n")
"""
for i in range(len(test_encoded_data)):
    tmp_list = []

    for d in test_encoded_data[i] :
        tmp_list.append(d)

    rtn = str(tmp_list)[1:-1]
    test_file.write(str.format(rtn) + "\n")
"""