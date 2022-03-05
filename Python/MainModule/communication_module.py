from socket import *
import threading
import enum
import json
import time

import requests

class order_enum(enum.Enum):
    NO_REQUEST = 0
    JUST_MESSAGE = 1
    WAVES = 2
    BP_REQUEST = 3

# end of class

class client_handler:
    def __init__(self, clientSock, addr, lock):
        self.request = order_enum.NO_REQUEST
        self.sock = clientSock
        self.addr = addr
        self.lock = lock
        self.recv_msg = None
        self.server_msg = None
        self.th = threading.Thread(target=self.run, args=())
        self.th.start()
        self.destroy = False
        self.error_msg = ""

    def run(self):
        data_list = []
        print(str(self.addr) + " 에서 접속하였습니다.")
        while True:
            self.recv_msg = self.sock.recv(1024).decode("utf-8")
            self.recv_msg = json.loads(self.recv_msg)

            #print(self.recv_msg)
            if self.error_msg != "":
                self.send_msg("msg", self.error_msg)
                self.error_msg = ""
            if self.recv_msg != None and type(self.recv_msg) != type(1):
                try:
                    if self.recv_msg.get('msg_type') == "just_message":
                        self.recieve_order(order_enum.JUST_MESSAGE)
                    elif self.recv_msg.get('msg_type') == "waves":
                        #print(self.recv_msg)
                        self.recieve_order(order_enum.WAVES)
                    elif self.recv_msg.get('msg_type') == "bp_request":
                        self.recieve_order(order_enum.BP_REQUEST)
                    else:
                        print("unknown msg_type : " + self.recv_msg.get('msg_type'))
                except AttributeError as e:
                    print(e)
                    self.sock.close()
                except Exception as e:
                    print(e, "ee")

###################### 여기서 데이터리스트 만들어줌 ######################
            else :
                """
                if len(data_list) < 10 :
                    data_list.append(self.recv_msg)
                elif len(data_list) == 10 :
                    print(data_list)
                    data_list.clear()
                """
                if len(data_list) < 10 :
                    data_list.append(self.recv_msg)

                if len(data_list)%10 == 0:
                    print(data_list)
                    data_list.clear()

###################### 여기서 데이터리스트 만들어줌 ######################

            if self.destroy:
                break


            time.sleep(0.1)
        # end of while loop
    """  you should define function here
        all of funtion must acquire and release lock
    """
    def send_msg(self, type, msg):
        tmp_dict = {'msg_type': str(type), 'msg_content': str(msg)}
        tmp_json = json.dumps(tmp_dict)
        self.sock.sendall(tmp_json.encode())

    def recieve_order(self, order):
        self.lock.acquire()
        self.request = order

        # 요청한 작업이 완료되면 request를 NO_REQUEST로 바꾸어주어 바쁜대기를 종료합니다.
        while self.request != order.NO_REQUEST:
            time.sleep(0.1)

        self.recv_msg = None
        self.lock.release()

    # end of function

# end of class


class server_class:
    def __init__(self):
        self.lock1 = threading.Lock()
        self.server_ip = "220.69.203.88"
        self.server_port = 5000
        self.serverSock = None
        self.waiting_th = threading.Thread(target=self.connetion_thread)
        self.client_handler_list = []
        self.server_init()
        self.waiting_start()
        self.destroy = False

    def server_init(self):  # 서버를 열어주는 스레드
        print("initiating server...")
        self.serverSock = socket(AF_INET, SOCK_STREAM)  # IPV4 형식의 IP 형식이며, SOCK_STREAM 형식을 채택
        self.serverSock.settimeout(1) #소켓 통신에 시간 제한을 둠
        self.serverSock.bind((self.server_ip, self.server_port))  # 서버 소켓으로 사용할 IP와 포트 번호를 지정합니다.
        self.serverSock.listen(5)  # 최대 두개의 클라이언트가 접속할 수 있습니다.

    def waiting_start(self) :
        th = threading.Thread(target=self.connetion_thread, args=())
        th.start()

    def connetion_thread(self):
        print("waiting client...")
        while True:
            try:
                connectionSock, addr = self.serverSock.accept()
                ch = client_handler(connectionSock, addr, self.lock1)
                self.client_handler_list.append(ch)
            except Exception as e:
                pass
            except socket.timeout:
                pass

            if self.destroy:
                break

    def clear(self):
        print("clearing server")
        for c in self.client_handler_list:
            c.sock.close()
            c.destory = True
        self.serverSock.close()
        self.destroy = True
        print("done")


if __name__ == "__main__" :
    server_class = server_class()
    print("클라이언트 접속을 기다립니다.")

