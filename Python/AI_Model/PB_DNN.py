import numpy as np
import random
import tensorflow as tf
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.layers import Dropout
from tensorflow.keras import layers, models
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix
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

#xd = (xd-xd.min())/(xd.max()-xd.min())
#yd = yd

#hyper params
SPLIT_RATE = 0.2
EPOCH = 500
INPUT_SIZE = len(xd[0])

xt, xv, yt, yv = train_test_split(xd, yd, test_size = SPLIT_RATE, random_state = 123)
xt = np.array(xt)
xv = np.array(xv)
yt = np.array(yt)
yv = np.array(yv)

with tf.device('GPU:0'):
    tf.keras.initializers.RandomNormal(mean=0.0, stddev=0.05, seed=0)
    model = models.Sequential()
    model.add(layers.Dense(1000, activation=tf.nn.swish, input_shape=[INPUT_SIZE]))
    model.add(layers.Dense(1000, activation=tf.nn.swish))
    model.add(layers.Dense(1000, activation=tf.nn.swish))
    model.add(layers.Dense(1000, activation=tf.nn.swish))
    model.add(layers.Dense(1000, activation=tf.nn.swish))
    model.add(layers.Dense(2, activation=tf.nn.swish))

    model.compile(optimizer=Adam(lr=1.46e-3), loss='mse')
    hist = model.fit(xt, yt, shuffle=True, epochs=EPOCH)
    print(hist)
    model.summary()

    pd = model.predict(xv)

    for i in range(len(xv)):
        #fmt = '실제값: {1}, 예측값: {2:.5f} {3:.5f}, 정제된값: {4:.0f} {5:.0f}'
        #print(fmt.format(yv[i], pd[i][0], pd[i][1], pd[i][0], pd[i][1]))
        print("실제값 : ", yv[i],"\t", "예측값 :", pd[i])

    print(r2_score(yv, pd))
    model.save('ppg_dnn_model.h5')

    sys_list = []
    dia_list = []
    for i in range(len(yv)) :
        sys_list.append(pd[i][0]-yv[i][0])
        dia_list.append(pd[i][1]-yv[i][1])

    plt.rcParams["figure.figsize"] = (7,5)
    plt.subplot(211)
    plt.title('systolic')
    plt.hist(sys_list, histtype='step', bins=100)

    plt.subplot(212)
    plt.title('diastolic')
    plt.hist(dia_list, histtype='stepfilled', bins=100)
    plt.show()

    