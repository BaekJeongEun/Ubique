import os
import numpy as np
import tensorflow as tf
from tensorflow.keras.optimizers import Adam
from tensorflow.keras import layers, models
from tensorflow.keras.layers import Dense
from tensorflow.keras.layers import Dropout
from tensorflow.keras.layers import Flatten
from tensorflow.keras.layers import Conv1D
from tensorflow.keras.layers import MaxPooling1D
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error
from sklearn.metrics import r2_score
import matplotlib.pyplot as plt
import pandas as pd

gpus = tf.config.experimental.list_physical_devices('GPU')
if gpus:
    try:
        tf.config.experimental.set_memory_growth(gpus[0], True)
    except RuntimeError as e:
        print(e)

xy_data = np.loadtxt("ppg_bp_encoded_32.csv",delimiter=',', dtype=np.float32)
xd = xy_data[:,2:]
yd = xy_data[:,:2]
test_data = np.loadtxt("ppg_jeong_encoded_32.csv",delimiter=',', dtype=np.float32)
#xd = (xd-xd.min())/(xd.max()-xd.min())

DATA_LEN = len(xd[0])
EPOCH = 500
SPLIT_RATE = 0.2
DROPOUT_RATE = 0.2
LOAD_MODEL = False

xd = xd.reshape(-1,DATA_LEN,1)
test_data = test_data.reshape(-1,DATA_LEN,1)

xt, xv, yt, yv = train_test_split(xd, yd, test_size = SPLIT_RATE, random_state = 123)

checkpoint_path = "training/cnn_{epoch:04d}.ckpt"
checkpoint_dir = os.path.dirname(checkpoint_path)

cp_callback = tf.keras.callbacks.ModelCheckpoint(
    filepath=checkpoint_path, 
    verbose=1, 
    save_weights_only=True,
    period=100)

model = models.Sequential()
if LOAD_MODEL:
    model.load_weights(checkpoint_path)
model.add(Conv1D(filters=128, kernel_size=4, activation=tf.nn.swish, input_shape=(DATA_LEN,1)))
model.add(MaxPooling1D(pool_size=2))
model.add(Conv1D(filters=256, kernel_size=2, activation=tf.nn.swish))
model.add(MaxPooling1D(pool_size=2))
model.add(Dropout(DROPOUT_RATE))
model.add(Flatten())
model.add(Dense(500, activation=tf.nn.swish))
model.add(Dense(500, activation=tf.nn.swish))
model.add(Dense(500, activation=tf.nn.swish))
model.add(Dense(2, activation=tf.nn.swish))
model.compile(optimizer = 'adam', loss='mse')
model.save_weights(checkpoint_path.format(epoch=0))
model.summary()
model.fit(xt, yt, epochs=EPOCH, verbose=2, callbacks=[cp_callback])

pd = model.predict(xv)

model.save('ppg_cnn_model.h5')

#for d in pd:
    #print(d)

for i in range(len(xv)):
    #fmt = '실제값: {1}, 예측값: {2:.5f} {3:.5f}, 정제된값: {4:.0f} {5:.0f}'
    #print(fmt.format(yv[i], pd[i][0], pd[i][1], pd[i][0], pd[i][1]))
    #print("실제값 : ", yv[i],"\t", "예측값 :", pd[i])
    pass

print(r2_score(yv, pd))

sys_list = []
dia_list = []
for i in range(len(yv)) :
    sys_list.append(pd[i][0]-yv[i][0])
    dia_list.append(pd[i][1]-yv[i][1])

print("SBP MAE:",mean_absolute_error(pd[:,0:1], yv[:,0:1]))
print("DBP MAE:",mean_absolute_error(pd[:,1:2], yv[:,1:2]))

plt.rcParams["figure.figsize"] = (7,5)
plt.subplot(211)
plt.title('systolic')
plt.hist(sys_list, histtype='step', bins=200)

plt.subplot(212)
plt.title('diastolic')
plt.hist(dia_list, histtype='stepfilled',  bins=200)
plt.show()

