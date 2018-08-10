# This Python file uses the following encoding: utf-8

import socket
import select
import time

from jim_user import *
from jim_message import *
from server_log import *


@func_log
def parse_server_args(argv):
    host = None
    port = None
    
    for idx, arg in enumerate(argv):
        if arg == "-a":
            if (idx + 1) < len(argv):
                host = argv[idx+1]
            
        elif arg == "-p":
            print(idx + 1, len(argv))
            if (idx + 1) < len(argv):
                try:
                    port = int(argv[idx+1])
                except:
                    continue
            
    return host, port
    
    
class JimServer:

    def __init__(self):
        self.socket = None
        self.host = None
        self.port = None
        self.user_list = None
        self.socket_list = None
        self.encoding = None
        self.max_buf_size = None
        self.probe_interval = None

    
    @staticmethod
    @func_log
    def start_server(host, port, max_users):
        try:
            srv_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            
        except Exception as e:
            srv_socket = None
            raise e
            
        try:
            print(f"Инициализация сервера по адресу {host}:{port}...")
            srv_socket.bind((host, port))
            srv_socket.listen(max_users)
            print("Сервер запущен успешно")

        except Exception as e:
            srv_socket.close()
            srv_socket = None
            raise e

        jim_server = JimServer()
        jim_server.socket = srv_socket
        jim_server.socket_list = [srv_socket,]
        jim_server.host = host
        jim_server.port = port
        return jim_server

        
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
                self._close_user_socket(out_socket)
                return False
                    
        else:
            print("Ошибка при отправке сообщения")
            return False
    
    @func_log
    def _close_user_socket(self, socket):
        if socket in self.socket_list:
            self.socket_list.remove(socket)

        for user in self.user_list.values():
            if socket is user.socket:
                user.socket = None
                user.is_auth = False
                user.is_alive = False
                break

        socket.close()


    def run_server(self):
        while True:
            next_probe_time = time.time() + self.probe_interval

            try:
                rlist, wlist, xlist = select.select(self.socket_list, [], [], 0)

                for in_socket in rlist:
                    if in_socket is self.socket:
                        new_socket, addr = self.socket.accept()
                        self.socket_list.append(new_socket)
                        print(f"Получен запрос на соединение от {str(addr)}")

                    else:
                        try:
                            data = in_socket.recv(self.max_buf_size)

                            if data is not None:
                                in_jim_msg = JimMessage.parse_bytes(data, self.encoding)
                                print("Входящее сообщение:", in_jim_msg)
                    
                                if in_jim_msg is not None:
                                    try:
                                        out_socket, out_jim_msg = self.dispatch_message(in_socket, in_jim_msg)
                        
                                    except Exception as e:
                                        print(e)
                                        out_socket = in_socket
                                        out_jim_msg = JimMessage.response_message(RESPONSE_SERVER_ERROR, self.encoding)
                        
                                else:
                                    out_socket = in_socket
                                    out_jim_msg = JimMessage.response_message(RESPONSE_CLIENT_BAD_REQUEST, self.encoding)

                                if out_socket is not None:
                                    self._send_message(out_socket, out_jim_msg)
                                    
                                elif out_jim_msg is not None:
                                    for username in self.user_list:
                                        user = self.user_list[username]
                                        if user.socket is not None and user.is_alive:
                                            if not self._send_message(user.socket, out_jim_msg):
                                                self._close_user_socket(user.socket)

                            else:
                                self._close_user_socket(in_socket)

                        except Exception as e:
                            self._close_user_socket(in_socket)
                            print(e)
                
            except Exception as e:
                print(e)
            
        self.socket.close()
        self.socket = None

        
    @func_log
    def dispatch_message(self, socket, jim_msg):
        action = jim_msg.action

        if action == ACTION_AUTH:
            return self._msg_auth_handler(socket, jim_msg)

        if action == ACTION_QUIT:
            return self._msg_quit_handler(socket, jim_msg)

        if action == ACTION_PRESENCE:
            return self._msg_presence_handler(socket, jim_msg)

        if action == ACTION_MSG:
            return self._msg_message_handler(socket, jim_msg)

        return socket, JimMessage.response_message(RESPONSE_CLIENT_BAD_REQUEST, self.encoding)
 
    
    @func_log
    def _msg_auth_handler(self, socket, jim_msg):
        username = jim_msg.user["account_name"]
        password = jim_msg.user["password"]
        
        if username in self.user_list:
            user = self.user_list[username]
            
            if user.password == password:
                if not user.is_active:
                    return socket, JimMessage.response_message(RESPONSE_CLIENT_FORBIDDEN, self.encoding)
                
                elif user.is_auth:
                    return socket, JimMessage.response_message(RESPONSE_CLIENT_CONFLICT, self.encoding)
                
                else:
                    if user.socket is not None:
                        user.socket.close()
                        
                    user.socket = socket
                    user.is_auth = True
                    user.is_alive = True
                    user.last_login = time.time()
                    return socket, JimMessage.response_message(RESPONSE_SUCCESS_OK, self.encoding)
                
            else:
                return socket, JimMessage.response_message(RESPONSE_CLIENT_INVALID_CRED, self.encoding)
            
        else:
            user = JimUser()
            user.socket = socket
            user.username = username
            user.password = password
            user.is_active = True
            user.is_auth = True
            user.is_alive = True
            user.date_joined = time.time()
            user.last_login = time.time()

            self.user_list[username] = user
            
            return socket, JimMessage.response_message(RESPONSE_SUCCESS_OK, self.encoding)
    
    
    @func_log
    def _msg_quit_handler(self, socket, jim_msg):
        self._close_user_socket(socket)
        return None, None
        
        
    @func_log
    def _msg_presence_handler(self, socket, jim_msg):
        username = jim_msg.user["account_name"]
        
        if username in self.user_list:
            user = self.user_list[username]

            if not user.is_active:
                return socket, JimMessage.response_message(RESPONSE_CLIENT_FORBIDDEN, self.encoding)
            
            elif not user.is_auth or user.socket is None or socket is not user.socket:
                return socket, JimMessage.response_message(RESPONSE_CLIENT_UNAUTHORIZED, self.encoding)
            
            else:
                user.is_alive = True
                return socket, JimMessage.response_message(RESPONSE_SUCCESS_OK, self.encoding)
            
        else:
            return socket, JimMessage.response_message(RESPONSE_CLIENT_UNAUTHORIZED, self.encoding)      
        
        
    @func_log
    def _msg_message_handler(self, socket, jim_msg):
        username_from = jim_msg.from_
        username_to = jim_msg.to_
        
        if username_from in self.user_list:
            user = self.user_list[username_from]

            if not user.is_active:
                return socket, JimMessage.response_message(RESPONSE_CLIENT_FORBIDDEN, self.encoding)
            
            elif not user.is_auth or user.socket is None or socket is not user.socket:
                return socket, JimMessage.response_message(RESPONSE_CLIENT_UNAUTHORIZED, self.encoding)
            
            else:
                if username_to == "EVERYONE":
                    return None, jim_msg
                    
                elif username_to in self.user_list:
                    user_to = self.user_list[username_to]

                    if not user_to.is_auth or not user_to.is_active or not user_to.is_alive or user_to.socket is None:
                        return socket, JimMessage.response_message(RESPONSE_CLIENT_OFFLINE, self.encoding)

                    else:
                        return user_to.socket, jim_msg

                else:
                    return socket, JimMessage.response_message(RESPONSE_CLIENT_NOT_FOUND, self.encoding)               
            
        else:
            return socket, JimMessage.response_message(RESPONSE_CLIENT_UNAUTHORIZED, self.encoding)

