# This Python file uses the following encoding: utf-8

import json
import time


ACTION_AUTH = 1
ACTION_QUIT = 2
ACTION_PROBE = 3
ACTION_PRESENCE = 4
ACTION_MSG = 5


RESPONSE_BASIC_NOTIFICATION = 101
RESPONSE_MAJOR_NOTIFICATION = 101
RESPONSE_SUCCESS_OK = 200
RESPONSE_SUCCESS_CREATED = 201
RESPONSE_SUCCESS_ACCEPTED = 202
RESPONSE_CLIENT_BAD_REQUEST = 400
RESPONSE_CLIENT_UNAUTHORIZED = 401
RESPONSE_CLIENT_INVALID_CRED = 402
RESPONSE_CLIENT_FORBIDDEN = 403
RESPONSE_CLIENT_NOT_FOUND = 404
RESPONSE_CLIENT_CONFLICT = 409
RESPONSE_CLIENT_OFFLINE = 410
RESPONSE_SERVER_ERROR = 500

RESPONSE_MESSAGE_DICT = {
    RESPONSE_BASIC_NOTIFICATION: "Базовое уведомление",
    RESPONSE_MAJOR_NOTIFICATION: "Важное уведомление",
    RESPONSE_SUCCESS_OK: "ОК",
    RESPONSE_SUCCESS_CREATED: "Объект создан",
    RESPONSE_SUCCESS_ACCEPTED: "Подтверждение",
    RESPONSE_CLIENT_BAD_REQUEST: "Некорректный запрос",
    RESPONSE_CLIENT_UNAUTHORIZED: "Пользователь не авторизован",
    RESPONSE_CLIENT_INVALID_CRED: "Неверный логин/пароль",
    RESPONSE_CLIENT_FORBIDDEN: "Пользователь заблокирован",
    RESPONSE_CLIENT_NOT_FOUND: "Пользователь/чат отсутствует на сервере",
    RESPONSE_CLIENT_CONFLICT: "Уже имеется подвключение с указанным логином",
    RESPONSE_CLIENT_OFFLINE: "Адресат не в сети",
    RESPONSE_SERVER_ERROR: "Ошибка сервера"
}


def _decode_message(data, encoding):
    try:
        json_str = data.decode(encoding)
        dict_ = json.loads(json_str, encoding=encoding)
        return dict_

    except Exception as e:
        print(e)
        return None

    
def _encode_message(dict_, encoding):
    try:
        json_str = json.dumps(dict_, ensure_ascii=False)
        data = json_str.encode(encoding)
        return data

    except Exception as e:
        print(e)
        return None
    
    
class JimMessage:

    def __init__(self, encoding):
        self.action = None
        self.response = None
        self.user = None
        self.from_ = None
        self.to_ = None
        self.message = None
        self.time = time.time()
        self.encoding = encoding

        
    def __str__(self):
        if self.time is not None:
            str_time = time.strftime("%d.%m.%Y %H:%M:%S", time.localtime(self.time))
        else:
            str_time = "None"
            
        if self.action is not None:
            return f"JimMessage(action: {self.action}, time: {str_time}, enc: {self.encoding}, user: {self.user}, from: {self.from_}, to: {self.to_}, msg: {self.message})"
        elif self.response is not None:
            return f"JimMessage(response: {self.response}, time: {str_time}, encoding: {self.encoding})"
        else:
            return f"JimMessage(time: {str_time}, encoding: {self.encoding})"
        

    def to_bytes(self):
        dict_ = dict()
        dict_["time"] = self.time

        if self.action is not None:
            if self.action == ACTION_AUTH:
                dict_["action"] = "authenticate"
                dict_["user"] = self.user

            if self.action == ACTION_QUIT:
                dict_["action"] = "quit"

            if self.action == ACTION_PROBE:
                dict_["action"] = "probe"

            if self.action == ACTION_PRESENCE:
                dict_["action"] = "presence"
                dict_["user"] = self.user

            if self.action == ACTION_MSG:
                dict_["action"] = "msg"
                dict_["to"] = self.to_
                dict_["from"] = self.from_
                dict_["encoding"] = self.encoding
                dict_["message"] = self.message

        if self.response is not None:
            dict_["response"] = self.response
        
        data = _encode_message(dict_, self.encoding)
        
        return data


    @staticmethod
    def parse_bytes(data, encoding):
        dict_ = _decode_message(data, encoding)
        
        if dict_ is None:
            return None
    
        if "time" not in dict_:
            return None

        time_ = dict_["time"]

        if "action" in dict_:
            action = dict_["action"]
            if action == "authenticate":
                if "user" not in dict_:
                    return None

                user = dict_["user"]
                if "account_name" not in user or "password" not in user:
                    return None
            
                jim_msg = JimMessage(encoding)
                jim_msg.action = ACTION_AUTH
                jim_msg.time = time_
                jim_msg.user = user
                return jim_msg

            if action == "quit":
                jim_msg = JimMessage(encoding)
                jim_msg.action = ACTION_QUIT
                jim_msg.time = time_
                return jim_msg

            if action == "probe":
                jim_msg = JimMessage(encoding)
                jim_msg.action = ACTION_PROBE
                jim_msg.time = time_
                return jim_msg

            if action == "presence":
                if "user" not in dict_:
                    return None

                user = dict_["user"]
                if "account_name" not in user:
                    return None
            
                jim_msg = JimMessage(encoding)
                jim_msg.action = ACTION_PRESENCE
                jim_msg.time = time_
                jim_msg.user = user
                return jim_msg

            if action == "msg":
                if "to" not in dict_ \
                    or "from" not in dict_ \
                    or "encoding" not in dict_ \
                    or "message" not in dict_:
                    return None
            
                jim_msg = JimMessage(encoding)
                jim_msg.action = ACTION_MSG
                jim_msg.time = time_
                jim_msg.to_ = dict_["to"]
                jim_msg.from_ = dict_["from"]
                jim_msg.encoding = dict_["encoding"]
                jim_msg.message = dict_["message"]
                return jim_msg           

            return None

        elif "response" in dict_:
            jim_msg = JimMessage(encoding)
            jim_msg.response = dict_["response"]
            jim_msg.time = time_
            return jim_msg

        else:
            return None


    @staticmethod
    def response_message(response, encoding):
        jim_msg = JimMessage(encoding)
        jim_msg.response = response
        return jim_msg


