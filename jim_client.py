# This Python file uses the following encoding: utf-8

import sys
import socket
import select
import time

from jim_message import *
from client_log import *


@func_log
def parse_client_args(argv):
    host = None
    port = None
    read_only = None
    
    for idx, arg in enumerate(argv):
        if arg == "-r":
            read_only = True
            
        elif arg == "-w":
            read_only = False
            
        elif arg == "-a":
            if (idx + 1) < len(argv):
                host = argv[idx+1]
            
        elif arg == "-p":
            print(idx + 1, len(argv))
            if (idx + 1) < len(argv):
                try:
                    port = int(argv[idx+1])
                except:
                    continue
            
    return host, port, read_only
    
        
class JimClient:

    def __init__(self):
        self.socket = None
        self.host = None
        self.port = None
        self.username = None
        self.password = None
        self.encoding = None
        self.max_buf_size = None
        self.message_prompt = None
        self.read_only = None


    @staticmethod
    @func_log
    def start_client(host, port):
        try:
            clnt_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            
        except Exception as e:
            clnt_socket = None
            raise e
            
        try:
            print(f"Подключение к серверу {host}:{port}...")
            clnt_socket.connect((host, port))
            print("Подключение успешно установлено")

        except Exception as e:
            clnt_socket.close()
            clnt_socket = None
            raise e

        jim_client = JimClient()
        jim_client.socket = clnt_socket
        jim_client.host = host
        jim_client.port = port
        return jim_client

        
    @func_log
    def close(self):
        self.socket.close()
        self.socket = None


    def show_message_prompt(self):
        print(self.message_prompt)

        
    @func_log
    def authorize(self):
        auth_jim_msg = JimMessage(self.encoding)
        auth_jim_msg.action = ACTION_AUTH
        auth_jim_msg.user = { "account_name": self.username, "password": self.password }

        if not self._send_message(self.socket, auth_jim_msg):
            return False

        try:
            data = self.socket.recv(self.max_buf_size)
            in_jim_msg = JimMessage.parse_bytes(data, self.encoding)
            print("Ответ сервера:", in_jim_msg)

            if in_jim_msg is not None:
                if in_jim_msg.response == RESPONSE_SUCCESS_OK:
                    print("Авторизация прошла успешно")
                    return True

                else:
                    print("Ошибка авторизации:", RESPONSE_MESSAGE_DICT[in_jim_msg.response])
                    return False
            
            else:
                print("Ошибка при получении ответа сервера")
                return False

        except Exception as e:
            print(e)
            print("Ошибка при получении ответа сервера")
            return False

            
    @func_log
    def run_client(self):
        if self.read_only:
            while True:
                try:
                    data = self.socket.recv(self.max_buf_size)
                    in_jim_msg = JimMessage.parse_bytes(data, self.encoding)

                    if in_jim_msg is not None:
                        print("Ответ сервера:", in_jim_msg)
                    
                    else:
                        print("Ошибка при получении ответа сервера")
                        break

                except Exception as e:
                    print(e)
                    print("Ошибка при получении ответа сервера")
                    break
            
        else:
            while True:
                message = "Съешь еще этих мягких французских булочек." # input("Введите сообщение: ")
                
                jim_msg = JimMessage(self.encoding)
                jim_msg.action = ACTION_MSG
                jim_msg.to_ = "EVERYONE"
                jim_msg.from_ = self.username
                jim_msg.message = message
                
                if not self._send_message(self.socket, jim_msg):
                    break
                    
                time.sleep(10)

                
    @func_log
    def disconnect(self):
        quit_jim_msg = JimMessage(self.encoding)
        quit_jim_msg.action = ACTION_QUIT

        self._send_message(self.socket, quit_jim_msg)

        self.close()

        
    @func_log
    def _send_message(self, out_socket, out_jim_msg):
        data = out_jim_msg.to_bytes()

        if data is not None:
            try:
                out_socket.send(data)
                print("Исходящее сообщение:", out_jim_msg)
                return True

            except Exception as e:
                print(e)
                print("Ошибка при отправке сообщения")
                return False
                    
        else:
            print("Ошибка при отправке сообщения")
            return False

