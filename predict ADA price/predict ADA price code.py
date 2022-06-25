# -*- coding: utf-8 -*-
"""

@author: HueMinh
"""
#%%
import pandas as pd 
import yfinance as yf
import matplotlib.pyplot as plt 
from matplotlib.pyplot import rcParams
rcParams['figure.figsize'] = 15,6
import seaborn; seaborn.set()

#%%
# Lấy dữ liệu ADA từ yahoo finance
df= yf.download('ADA-USD', 
                       start='2017-01-01', 
                       end='2022-01-21',
                       progress=False)
#%% Kiểm tra bộ dữ liệu lấy từ Yahoo Finance 
#Kiểm tra thông tin cột và dữ liệu bị thiếu 
df.info()

# Xóa các cột ngoại trừ cột "Adj Close"
df.drop(df.columns.difference(['Adj Close']), 1, inplace=True)

#%% Phân tích dữ liệu thô 
rolmean = df.rolling(window= 30,center=False).mean()
rolstd = df.rolling(window=30 ,center=False).std()    

orig = plt.plot(df, color='blue',label='Orignal')
mean = plt.plot(rolmean, color='red', label='Rolling Mean')
std = plt.plot(rolstd, color='black', label = 'Rolling Standard Deviation')
plt.legend(loc='best')
plt.title('Raw Data: Rolling Mean & Standard Deviation')
plt.ylabel("Cardano's Daily Price")
plt.show(block=False)
plt.show()
#%% Kiểm tra tính mùa vụ của dữ liệu
from statsmodels.tsa.seasonal import seasonal_decompose
df_weekly= df.resample('w').last() 

decompose_res = seasonal_decompose(df_weekly['Adj Close'], model='multiplicative')
 
decompose_res.plot()

plt.tight_layout()
# plt.savefig('images/ch3_im2.png')
plt.show()
#%%
from pandas.plotting import autocorrelation_plot
autocorrelation_plot(df)
plt.show()

#%% Kiểm tra tính dừng của dữ liệu
from statsmodels.tsa.stattools import adfuller

def ad_test(dataset):
    dftest = adfuller(dataset, autolag ='AIC')
    print('1. ADF: ', dftest[0])
    print('2. P-value: ', dftest[1])
    print('3. Số các độ lệch : ', dftest[2])
    print('4. Số lượng quan sát được sử dụng để tính toán hồi quy ADF và các giá trị tới hạn: ', dftest[3])
    print('5. Giá trị tới hạn: ' )
    for key,val in dftest[4].items():
        print('\t',key,':',val)
    for key,val in dftest[4].items():
         if dftest[0]>val: 
            print('Dữ liệu không có tính dừng') 
            break
         else:
            print('Dữ liệu có tính dừng')
            break;

ad_test(df['Adj Close'])
#%% Khắc phục chuỗi dữ liệu không dừng
# Lấy sai phân của dữ liệu    
df_stationary_diff = df.diff().dropna()

df_stationary_diff.head() 

# Kiểm định tính dừng của dữ liệu sau khi lấy sai phân
ad_test(df_stationary_diff)

#%% Vẽ biểu đồ của dữ liệu sau khi lấy sai phân 
#Thống kê luân phiên với 30 kỳ 
rolmean = df_stationary_diff.rolling(window=30,center=False).mean()
rolstd = df_stationary_diff.rolling(window=30,center=False).std()

orig = plt.plot(df_stationary_diff, color='blue',label='Original')
mean = plt.plot(rolmean, color='red', label='Rolling Mean')
std = plt.plot(rolstd, color='black', label = 'Rolling Standard Deviation')
plt.legend(loc='best')
plt.title('Diff of price: Rolling mean and standard deviation')
plt.ylabel("Diff of Cardano's Daily price ")
plt.show(block=False)
plt.show()

#%% Kiểm định tự tương quan
from statsmodels.tsa.stattools import acf, pacf

lag_acf = acf(df_stationary_diff, nlags=40)
lag_pacf = pacf(df_stationary_diff, nlags=40, method='ols')

from statsmodels.graphics.tsaplots import plot_acf
from statsmodels.graphics.tsaplots import plot_pacf
 
fig, ax = plt.subplots(2, sharex= True)
plot_acf(df_stationary_diff, ax=ax[0],lags=40, alpha=0.05)
plot_pacf(df_stationary_diff, ax=ax[1], lags=40, alpha=0.05)

#%% Figure out order for ARIMA model
from pmdarima import auto_arima
# Ignore harmless warnings
import warnings
warnings.filterwarnings('ignore')
#%% Tìm bộ tham số (p, d, q) phù hợp với autoarima 

stepwise_fit = auto_arima(df, trace = True, suppress_warnings=True, seasonal =False)

stepwise_fit.summary()
#%% Chia dữ liệu thành tập dữ liệu đào tạo và thử nghiệm
n = int(0.9*df.shape[0])
train = df.iloc[:n]
test = df.iloc[n:]
print('\n', 'Kích thước của tập dữ liệu đào tạo là: ', train.shape, 
      '\n', 'Kích thước của tập dữ liệu thử nghiệm là: ', test.shape)
#%% Đồ thị biểu diễn tập dữ liệu đào tạo và thử nghiệm
plt.figure(figsize=(12,5))
plt.xlabel('Dates')
plt.ylabel('Price')
plt.plot(train, 'b', label = 'Train data')
plt.plot(test, 'g', label = 'Test data')
plt.title('Train & Test Data')
plt.show()

#%% Đào tạo mô hình 

from statsmodels.tsa.arima_model import ARIMA
model = ARIMA(train, order=(1,1,1))
model = model.fit()
model.summary()

#%% Thực hiện dự báo trên tập kiểm định 
start = len(train)
end= len(train) + len(test) -1 
pred = model.predict(start=start,end=end, typ='levels')
 
print(pred)

#%% Biểu đồ giá trị dự đoán 
plt.figure(figsize=(12,5))
plt.xlabel('Dates')
plt.ylabel('Price')
plt.plot(train, 'b', label = 'Train data')
plt.plot(test, 'g', label = 'Test data')
plt.plot(pred, 'r', label ='Predict')
plt.title('Prediction')
plt.legend(loc = 'best') 
plt.show()
#%% Biểu đồ dự đoán giá với tập kiểm định, khoảng tin cậy 95%
fig, ax = plt.subplots()
ax = test.plot(ax=ax)
model.plot_predict(start=start,
                   end=end, 
                   dynamic =True,
                   ax=ax, 
                   plot_insample=False)
#%% 
from sklearn.metrics import mean_squared_error, mean_absolute_error, mean_absolute_percentage_error
from math import sqrt

mse = mean_squared_error(test,pred)
rmse = sqrt(mse)
mae = mean_absolute_error(test, pred)
mape = mean_absolute_percentage_error(test, pred)

print('Mean Square Error (MSE): ' '%.4f' % mse )
print('Root Mean Square Error (RMSE): ' '%.4f' % rmse )
print('Mean Absolute Error (MAE): ' '%.4f' % mae )
print('Mean Absolute Percentage Error (MAPE): ' '%.4f' % mape )

#%% Dự đoán giá Cardano trong 30 ngày tiếp theo trong tương lai 
model2 = ARIMA(df, order=(1,1,1)).fit()
predict = model2.predict(start = len(df),end=len(df)+30,typ='levels').rename('ARIMA prediction')

print(predict)

#%%Biểu đồ dự đoán giá trong 30 ngày ở tương lai 
fig, ax = plt.subplots()
ax = df.loc['2022':].plot(ax=ax)
model2.plot_predict(start=len(df),end=len(df)+30, dynamic =True,ax=ax, plot_insample=False)
