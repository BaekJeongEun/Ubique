import communication_module as cm
import prediction_class as pc
#import database_module as dm
import threading
import time
import json

class module_communicator:

    def __init__(self, server, predict_class):
        self.split_list_all= []
        self.lists_list = []
        self.count = 0
        self.list_count = 0
        self.bp_requested = False

        self.predict_class = predict_class
        self.server = server
        self.handler = threading.Thread(target=self.run, args=())
        self.handler.start()

    def run(self):
        # 무한 루프로 돌려버립니다.
        while True:
            # 클라이언트 목록을 향상된 for문으로 참조합니다.
            for c in self.server.client_handler_list:
                # 만일 해당 클라이언트의 리퀘스트가 NO REQUEST가 아니라면
                if c.request != cm.order_enum.NO_REQUEST:
                    try:
                        if c.request == cm.order_enum.JUST_MESSAGE:
                            content = c.recv_msg.get('msg_content')
                            self.just_message(content)
                        elif c.request == cm.order_enum.WAVES:
                            content = c.recv_msg.get('msg_content')
                            self.go_android(c.recv_msg, content)
                        elif c.request == cm.order_enum.BP_REQUEST:
                            if self.bp_requested == False :
                                self.bp_requested = True
                        else:
                            print("unknown request :" + c.request)
                    except Exception as e:
                        c.error_msg = str(e)
                        print(c.error_msg)
                    finally:
                        c.request = cm.order_enum.NO_REQUEST
            time.sleep(0.01)
        # end of while loop
        #clear_all(self.db, self.server)

    #ppg에서 받은 bp를 여기를 거쳐서 인공지능 모듈로
    def go_android2(self, content, content_get):
        for client in self.server.client_handler_list:
            dictionaries2={'msg_type':'bp','msg_content':'120,80'}

            try:
                message2=json.dumps(dictionaries2)
            except:
                raise ("dddddddd")

            client.sock.sendall(message2.encode("utf-8"))

    #waves를 안드로이드로 보냄
    def go_android(self, content, content_get):
        for client in self.server.client_handler_list:
            dictionaries={'msg_type':'waves','msg_content':content_get}
            try:
                message=json.dumps(dictionaries)
            except:
                raise ("dddddddd")

            client.sock.sendall(message.encode("utf-8"))

        if self.bp_requested :
            #200개 넘으면 인공지능 모듈에 보낼거기때문에 함수 실행
            #여기서 split해서 10개씩 끊어진 str를 하나의 리스트로 만들었음
            #,로 시작하기 때문에 [0]는 무조건 빈 값이 들어가므로 삭제해줬음!
            #200개를 세기 위해 count 추가해서 확인하도록 했음
            content_get_split = content_get.split(',')
            del content_get_split[0]
            self.count = self.count + 1

            #self.count가 1개당 list 안에 데이터는 10개! 그러므로 200의 데이터 리스트를 모으려면 count가 20가 될때까지 계속 더해줘서
            #200개의 데이터가 모여있는 1개의 리스트: self.split_list_all
            #count가 20개일때 인공지능 모듈로 보내주고, 함수 실행하라고 했지만.. 다연이는 말 안드러ㅓㅓㅓ
            if self.count<=4:
                self.split_list_all = self.split_list_all + content_get_split

            if self.count == 4:
                print("list_count :",self.list_count)
                counting_thread = threading.Thread(target=self.send_message, args=("progress", "hello",))
                counting_thread.start()

                self.list_count = self.list_count + 1
                self.lists_list.append(self.split_list_all)
                if self.list_count == 5 :
                    self.bp_requested = False
                    bp_thread = threading.Thread(target=self.send_blood_pressure, args=(self.lists_list, ))
                    bp_thread.start()

                    self.list_count = 0
                    self.lists_list = []

                self.count = 0
                self.split_list_all = []
    
    def send_blood_pressure(self, lists):
        #인공지능 모듈로 예측
        blood_pressure = self.predict_class.bp_prediction(lists)

        bp_dict = {'msg_type' : 'bp', 'msg_content' : blood_pressure}
        
        try :
            for c in self.server.client_handler_list:
                print(bp_dict)
                c.sock.sendall(json.dumps(bp_dict).encode("utf-8"))
        except Exception as e :
            print('혈압 송신에서 예외 발생', e)
    
    def send_message(self, msg_type, content):
        message_dict = {'msg_type' : msg_type, 'msg_content' : content}

        try :
            for c in self.server.client_handler_list:
                print(message_dict)
                c.sock.sendall(json.dumps(message_dict).encode("utf-8"))
        except Exception as e :
            print('메세지 보내기에서 예외 발생', e)

    def just_message(self, content):
        print(content)
    # end of funtion
# end of class
def clear_all(server, db):  # video stream will be terminated automatically
    server.clear()
    db.clear()

def main():
    predict_class = pc.prediction_class()
    server = cm.server_class()
    module_communicator( server = server, predict_class = predict_class)

if __name__ == "__main__":
    main()
