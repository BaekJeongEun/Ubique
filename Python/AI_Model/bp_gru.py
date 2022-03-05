import numpy as np
import tensorflow as tf
from keras.models import Sequential
from matplotlib import pyplot as plt
from keras.layers import Dense, LSTM, GRU
from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score
from tensorflow.keras.optimizers import Adam

gpus = tf.config.experimental.list_physical_devices('GPU')
if gpus:
    try:
        tf.config.experimental.set_memory_growth(gpus[0], True)
    except RuntimeError as e:
        print(e)

#HyperParameter
test_set_size = 0.8 #학습/시험셋 분할 크기(학습셋의 비율)
EPOCH = 400 #학습 횟수
csv_file_path = 'ppg_bp_encoded.csv' #불러올 csv 파일
predict_is_test = True #True일시 예측을 Test 셋으로 함 / False 일시 예측을 전체 데이터로 함

# 데이터 불러오기 및 학습/시험셋 분할
bp_data = np.loadtxt(csv_file_path, delimiter=',') #데이터 읽어옴

y_data = bp_data[:, :2] # ()
x_data = bp_data[:, 2:]

y_test, y_train, x_test, x_train = train_test_split(y_data, x_data, test_size=0.8, shuffle= True)

#print(x_data)
print('-------x reshape-----------')
x_data = x_data.reshape((x_data.shape[0], x_data.shape[1], 1))
x_train = x_train.reshape((x_train.shape[0], x_train.shape[1], 1))  # (4,3,1) reshape 전체 곱 수 같아야 4*3=4*3*1
x_test = x_test.reshape((x_test.shape[0], x_test.shape[1], 1))  # (4,3,1) reshape 전체 곱 수 같아야 4*3=4*3*1

# 2. 모델 구성
model = Sequential()
#model.add(GRU(100, activation=tf.nn.swish, input_shape=(x_data.shape[1], 1)))
model.add(LSTM(1000, activation=tf.nn.swish, input_shape=(x_data.shape[1], 1)))
# DENSE와 사용법 동일하나 input_shape=(열, 몇개씩잘라작업)
#model.add(GRU(100))
model.add(Dense(1024, activation=tf.nn.swish))
model.add(Dense(512, activation=tf.nn.swish))
model.add(Dense(256, activation=tf.nn.swish))
model.add(Dense(2))
model.summary()

# 3. 실행 epoch 반복 횟수
#opimizer = rmsprop, adam  / batch_size는 데이터를 자르는 크기
model.compile(optimizer=Adam(lr=1.46e-3), loss='mse')
model.fit(x_train, y_train, epochs= EPOCH) #validation_split은 학습 도중 학습할 부분과 아닌 부분을 분할하는 비율

if predict_is_test :
    x_predict = x_test
    y_predict = y_test
else :
    x_predict = x_data
    y_predict = y_data

yhat = model.predict(x_predict) #예측 결과
print(yhat)
print(r2_score(y_predict, yhat))

sys_list = []
dia_list = []
for i in range(len(y_predict)) :
    sys_list.append(yhat[i][0]-y_predict[i][0])
    dia_list.append(yhat[i][1]-y_predict[i][1])

plt.rcParams["figure.figsize"] = (7,5)
plt.subplot(211)
plt.title('systolic')
plt.hist(sys_list, bins=100, density=True, histtype='step')

plt.subplot(212)
plt.title('diastolic')
plt.hist(dia_list, bins=100, density=True, histtype='stepfilled')
plt.show()

model.save('ppg_gru_model.h5') #모델 저장 <- 옵티마이저 저장안됨 로드 후 컴파일 다시 필요