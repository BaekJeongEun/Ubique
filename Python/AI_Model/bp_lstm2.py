from numpy import array
from keras.models import Sequential
from keras.layers import Dense, LSTM
from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score
import numpy as np

# Open, High, Low, Volume, Close
bp_data = np.loadtxt('ppg_bp_encoded.csv', delimiter=',') #데이터 읽어옴

y_data = bp_data[:, :2]
x_data = bp_data[:, 2:]

y_test, y_train, x_test, x_train = train_test_split(y_data, x_data, test_size=0.8, shuffle= True)
"""
sc = MinMaxScaler(feature_range=(0,1))
x_data = sc.fit_transform(x_data)
"""
print('x shape : ', x_data.shape)  # (4,3)
print('y shape : ', y_data.shape)  # (4,)

#print(x_data)
print('-------x reshape-----------')
x_train = x_train.reshape((x_train.shape[0], x_train.shape[1], 1))  # (4,3,1) reshape 전체 곱 수 같아야 4*3=4*3*1
x_test = x_test.reshape((x_test.shape[0], x_test.shape[1], 1))  # (4,3,1) reshape 전체 곱 수 같아야 4*3=4*3*1
print('x shape : ', x_train.shape)

#  x        y
# [1][2][3] 4
# .....

# 2. 모델 구성
model = Sequential()
model.add(LSTM(100, activation='relu', input_shape=(x_data.shape[1], 1)))
# DENSE와 사용법 동일하나 input_shape=(열, 몇개씩잘라작업)
model.add(Dense(64))
model.add(Dense(512))
model.add(Dense(64))
model.add(Dense(2))
model.summary()

# 3. 실행 epoch 반복 횟수
#opimizer = rmsprop, adam  / batch_size는 데이터를 자르는 크기
model.compile(optimizer='adam', loss='mse')
model.fit(x_train, y_train, validation_split=0.2, epochs= 500)

"""
x_input = array(x)
x_input = x_input.reshape((1, 2000, 1))
"""

yhat = model.predict(x_test)
print(r2_score(y_test, yhat))


