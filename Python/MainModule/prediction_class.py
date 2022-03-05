import os
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import tensorflow as tf
from tensorflow import keras
from matplotlib import pyplot as plt
from sklearn.model_selection import train_test_split
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.models import Model
from tensorflow.keras import layers, models
from tensorflow.keras import layers, losses
from keras.models import model_from_json
from tensorflow.keras.layers import Dense
from tensorflow.keras.layers import Dropout
from tensorflow.keras.layers import Flatten
from tensorflow.keras.layers import Conv1D
from tensorflow.keras.layers import MaxPooling1D
from keras.models import load_model
#Start of Class
class Autoencoder(Model):
    def __init__(self, latent_dim, ppg_length):
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
            layers.Dense(ppg_length, activation='sigmoid'),
        ])

    def call(self, x):
        encoded = self.encoder(x)
        decoded = self.decoder(encoded)
        return decoded
#End of Class    
#Start of Class
class prediction_class() :
    def __init__(self):
        print("init")
        self.gpu_ready()
        self.autoencoder = self.autoencoder_load()
        self.cnn_model = self.cnn_model_load()

    #구동하는 컴퓨터가 tensorflow GPU가 가능하면 GPU로 가동하도록 함
    def gpu_ready(self):
        gpus = tf.config.experimental.list_physical_devices('GPU')
        if gpus:
            try:
                tf.config.experimental.set_memory_growth(gpus[0], True)
            except RuntimeError as e:
                print(e)

    #오토인코더 선 학습 시작
    def autoencoder_load(self):
        #학습 데이터 불러오기
        whole_data = np.loadtxt("ppg_bp_filtered.csv",delimiter=',', dtype=np.float32)
        bp_data = whole_data[:,:2]
        ppg_data = whole_data[:,2:]
        ppg_data = (ppg_data-ppg_data.min())/(ppg_data.max()-ppg_data.min())

        #오토인코더 학습 파라미터
        LATENT_DIM = 32
        SPLIT_RATE = 0.2
        EPOCHS = 100 #학습 횟수
        PPG_LENGTH = len(ppg_data[0])

        autoencoder = Autoencoder(LATENT_DIM, PPG_LENGTH)

        autoencoder.compile(optimizer=Adam(lr=1.46e-4), loss=losses.MeanSquaredError())
        autoencoder.fit(ppg_data, ppg_data, epochs=EPOCHS, shuffle=True) #,validation_data=(pv, pv))
        #autoencoder.summary()

        return autoencoder

    #CNN 모델 로드
    def cnn_model_load(self) :
        customObjects = {
            'swish' : tf.nn.swish
        }
        loaded_model = 'ppg_cnn_model.h5'
        model = tf.keras.models.load_model(loaded_model, custom_objects= customObjects)
        model.compile(optimizer = 'adam', loss='mse')

        #model.summary()

        return model

    #필터링 하는 함수
    def filtering_ppg_wave(self, data_list):
        #입력된 리스트는 (2, 200)
        float_data_lists = []
        
        for i in data_list :
            float_data_list = []
            for j in i :
                float_data_list.append(float(j))
            float_data_lists.append(float_data_list)

        data_list = float_data_lists

        ppg_data = np.array(data_list)
        for i in range(len(ppg_data)) :
            ppg_pd = pd.Series(ppg_data[i])
            ppg_data[i] = ppg_pd.rolling(window=10, min_periods=1).mean()

        
        
        """
        whole_data = np.loadtxt("ppg_jeong_filtered.csv",delimiter=',', dtype=np.float32)
        bp_data = whole_data[:,:2]
        ppg_data = whole_data[8:10,2:]
        
        for i in range(len(ppg_data)) :
            ppg_pd = pd.Series(ppg_data[i])
            ppg_data[i] = ppg_pd.rolling(window=10, min_periods=1).mean()
        """
        
        return ppg_data

    def bp_prediction(self, lists):
        """
        #MinMaxScaling을 위한 파라미터
        realtime_data_max = 2818.1
        realtime_data_min = 100.0

        #이동평균 필터링
        ppg_data = self.filtering_ppg_wave(list) #필터링 된 데이터 가져옴

        test_data = np.loadtxt("ppg_jeong_filtered.csv",delimiter=',', dtype=np.float32)
        test_data = (test_data-test_data.min())/(test_data.max()-test_data.min())
        test_ppg_data= test_data[:,2:]
        
        print("test_ppg_data")

        encoded_val_data = self.autoencoder.encoder(ppg_data).numpy() #오토인코더에 입력으로 함

        ppg_data = self.filtering_ppg_wave(lists) #필터링 된 데이터 가져옴
        ppg_data = (ppg_data-realtime_data_min)/(realtime_data_max-realtime_data_min)
        encoded_val_data = self.autoencoder.encoder(ppg_data).numpy() #오토인코더에 입력으로 함

        DATA_LEN = len(encoded_val_data[0])
        xd = encoded_val_data.reshape(-1,DATA_LEN,1)
        print(self.cnn_model.predict(xd))
        """

        #MinMaxScaling을 위한 파라미터
        realtime_data_max = 5000.0
        realtime_data_min = 100.0

        ppg_data = self.filtering_ppg_wave(lists) #필터링 된 데이터 가져옴
        
        ppg_data = (ppg_data-realtime_data_min)/(realtime_data_max-realtime_data_min)
        encoded_val_data = self.autoencoder.encoder(ppg_data).numpy() #오토인코더에 입력으로 함

        DATA_LEN = len(encoded_val_data[0])
        xd = encoded_val_data.reshape(-1,DATA_LEN,1)
        prediction = self.cnn_model.predict(xd)

        
        prediction = prediction.tolist()
        print(prediction)
        
        diavolic = 0
        systolic = 0
        count = 0
        for i in prediction :
            if i[0] > 50 and i[1] > 20: 
                count = count +1
                diavolic = diavolic + i[0]
                systolic = systolic + i[1]
        
        diavolic = diavolic/count
        systolic = systolic/count
        
        returns_str = str(int(diavolic))+","+str(int(systolic+10))
        
        #np.median(prediction
        
        """
        prediction = prediction.tolist()
        print(prediction)
        dias = []
        syss = []

        for i in prediction:
            dias.append(i[0])
            syss.append(i[1])

        dias.sort()
        syss.sort()
        
        returns_str = str(int(dias[2]))+","+str(int(syss[2]))
        """

        return returns_str
#End of Class        

if __name__ == '__main__':
    pc = prediction_class()
    pc.bp_prediction([1,2,3])
