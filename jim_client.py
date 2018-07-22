# This Python file uses the following encoding: utf-8

import sys
import socket
import select
import time

from jim_message import *

        
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


    @staticmethod
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


    def close(self):
        self.socket.close()
        self.socket = None


    def show_message_prompt(self):
        print(self.message_prompt)


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


    def run_client(self):
        pass


    def disconnect(self):
        quit_jim_msg = JimMessage(self.encoding)
        quit_jim_msg.action = ACTION_QUIT

        self._send_message(self.socket, quit_jim_msg)

        self.close()


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

