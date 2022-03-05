import numpy as np
import matplotlib.pyplot as plt
import csv

class MakeCsv():
    def __init__(self):


        self.opend_txt = open("uq_vsd_case06_fulldata_07.csv", 'r')
        self.maked_file = open('read_ppg_case_1122_2.csv', 'a') # a = 새로운 내용 추가, w = 새로운 파일 쓰기, r = 파일 내용 읽기 (끝나고 close 해주어야 함)
        self.all_of_data = None

    def csv_to_list(self):
        readed_file = csv.reader(self.opend_txt)
        outer_list = []

        for now_line in readed_file :
            inner_list = []
            for now_value in now_line :
                inner_list.append(now_value)

            outer_list.append(inner_list)

        print(outer_list[4][3])

        self.all_of_data = outer_list

    def search_csv(self):
        print("탐색을 시작할 열 : ")
        start_row = input()

        now_row = int(start_row)
        # 1 = 쓰고 다음으로 / 2 = 안 쓰고 다음으로 / 3 = 저장 종료
        while True :
            dbp, sdp, time, now_data = self.get_data(now_row)
            self.data_plotting(now_data)

            print("order : ")
            a = int(input())
            if a == 1:
                print("saving")
                self.saving_data(dbp, sdp, time, now_data)
            elif a == 2 :
                print("cancel")    
            else :
                print("프로그램 종료")
                break


            now_row = now_row + 200

        self.opend_txt.close()
        self.maked_file.close()

    def get_data(self, row):
        datas = []

        for i in range(0,200) :
                datas.append(float(self.all_of_data[row+i][3]))

        print(datas)

        
        return float(self.all_of_data[row][1]), float(self.all_of_data[row][2]), self.all_of_data[row][0], datas


    def data_plotting(self, datas):
        print(np.array(datas))
        print(type(datas[3]))
        plt.plot( np.array(datas))
        plt.show()

    def saving_data(self, dbp, sbp, start_time, data):
        writing_data = str(dbp) + ',' + str(sbp) + ',' + start_time
        for i in data :
            writing_data = writing_data + ',' + str(i)
        self.maked_file.write(str.format(writing_data) + "\n")
        print("saving...")
        

if __name__ == '__main__':
    mcs = MakeCsv()
    mcs.csv_to_list()
    mcs.search_csv()