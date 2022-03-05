import numpy as np
import pandas as pd
import glob
import pandas as pd
from scipy.stats import norm, kurtosis
from sklearn.preprocessing import MinMaxScaler
from collections import Counter

def text_to_csv():
    ppg_data_list = glob.glob('0_subject/*.txt')
    bp_data = np.loadtxt("bp_data.csv",delimiter=',', dtype=np.float32)

    file = open('ppg_bp.csv','a')
    
    ppg_bp_list = []

    print("loading text...")
    for p in ppg_data_list:

        label = p[p.index('t')+2:p.index('_',2)]
        subject = None
        for d in bp_data:
            if d[0] == float(label) :
                subject = d
        
        ppg = np.genfromtxt(p, dtype=None)
        if len(ppg) >2100:
            tmp = ppg[:2100]
            rtn_str = []
            rtn_str.append(subject[1])
            rtn_str.append(subject[2])
            for d in tmp:
                rtn_str.append(d)
            rtn = str(rtn_str)[1:-1]
            ppg = ppg[2100:]

        rtn_str = []
        rtn_str.append(subject[1])
        rtn_str.append(subject[2])
        for d in ppg:
            rtn_str.append(d)
        rtn = str(rtn_str)[1:-1]
        file.write(str.format(rtn) + "\n")
    print("done")

def ma_filter():
    #file = open('ppg_bp_filtered.csv','a')
    #filtered_data = np.loadtxt("ppg_bp_filtered.csv",delimiter=',', dtype=np.float32)
    #filtered_ppg = filtered_data[:, 2:]
    #scaler = MinMaxScaler(feature_range=(np.min(filtered_ppg),np.max(filtered_ppg)))

    file = open('ppg_bp_filtered.csv','a')
    whole_data = np.loadtxt("ppg_bp.csv",delimiter=',', dtype=np.float32)
    bp_data = whole_data[:,:2]
    ppg_data = whole_data[:,2:]
    
    for i in ppg_data :
        print(i)


    for i in range(len(ppg_data)) :
        ppg_pd = pd.Series(ppg_data[i])
        ppg_data[i] = ppg_pd.rolling(window=10, min_periods=1).mean()

        tmp_list = []
        tmp_list.append(bp_data[i].tolist()[0])
        tmp_list.append(bp_data[i].tolist()[1])
        for d in ppg_data[i]:
            tmp_list.append(d)
        rtn = str(tmp_list)[1:-1]
        file.write(str.format(rtn) + "\n")

def pre_processing():
    file = open('ppg_bp_ap.csv','a')
    whole_data = np.loadtxt("ppg_bp_filtered.csv",delimiter=',', dtype=np.float32)
    bp_data = whole_data[:,:2]
    ppg_data = whole_data[:,2:]
    ppg_data = (ppg_data-ppg_data.min())/(ppg_data.max()-ppg_data.min())

    for i in range(len(ppg_data)) :
        ppg_pd = pd.Series(ppg_data[i])
        
        ppg_min = np.min(ppg_data[i])
        ppg_max = np.max(ppg_data[i])
        ppg_ptp = ppg_max - ppg_min
        ppg_med = np.median(ppg_data[i])
        ppg_mean = np.mean(ppg_data[i])
        ppg_std = np.std(ppg_data[i])
        ppg_auc = ppg_pd.autocorr(lag=1)
        ppg_skew = ppg_pd.skew(skipna=True)
        ppg_mode = Counter(ppg_data[i]).most_common(1)[0][0]
        ppg_kur = kurtosis(ppg_data[i])

        tmp_list = []
        tmp_list.append(bp_data[i].tolist()[0])
        tmp_list.append(bp_data[i].tolist()[1])
        tmp_list.append(ppg_min)
        tmp_list.append(ppg_max)
        tmp_list.append(ppg_ptp)
        tmp_list.append(ppg_mean)
        tmp_list.append(ppg_med)
        tmp_list.append(ppg_std)
        tmp_list.append(ppg_auc)
        tmp_list.append(ppg_skew)
        tmp_list.append(ppg_mode)
        tmp_list.append(ppg_kur)
        rtn = str(tmp_list)[1:-1]
        file.write(str.format(rtn) + "\n")

def merge_ap_ae():
    file = open('ppg_bp_ap_ae.csv','a')
    whole_data = np.loadtxt("ppg_bp_ap.csv",delimiter=',', dtype=np.float32)
    bp_data = whole_data[:,:2]
    ppg_data = whole_data[:,2:]
    
    whole_data = np.loadtxt("ppg_bp_encoded.csv",delimiter=',', dtype=np.float32)
    ppg_data2 = whole_data[:,2:]

    
    for i in range(638):
        tmp_list = []
        tmp_list.append(bp_data[i].tolist()[0])
        tmp_list.append(bp_data[i].tolist()[1])
        for d in ppg_data[i]:
            tmp_list.append(d)
        for d in ppg_data2[i]:
            tmp_list.append(d)
        rtn = str(tmp_list)[1:-1]
        file.write(str.format(rtn) + "\n")

if __name__ == '__main__':
    #merge_ap_ae()
    ma_filter()