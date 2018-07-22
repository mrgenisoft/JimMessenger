# This Python file uses the following encoding: utf-8

import socket
import pytest


from jim_user import *
from jim_message import *
from jim_server import JimServer


DEFAULT_ENCODING = "utf-8"


def test_server_dispatch_message():
    srv_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    server = JimServer()
    server.encoding = DEFAULT_ENCODING
    server.user_list = dict()
    server.socket_list = [srv_socket,]

    # presence-сообщение без авторизации недопустимо
    in_jim_msg = JimMessage(DEFAULT_ENCODING)
    in_jim_msg.action = ACTION_PRESENCE
    in_jim_msg.user = dict()
    in_jim_msg.user["account_name"] = "guest"
    socket_, out_jim_msg = server.dispatch_message(socket.socket(socket.AF_INET, socket.SOCK_STREAM), in_jim_msg)
    assert out_jim_msg.response == RESPONSE_CLIENT_UNAUTHORIZED

    # авторизация нового пользователя = создание нового пользователя
    in_jim_msg = JimMessage(DEFAULT_ENCODING)
    in_jim_msg.action = ACTION_AUTH
    in_jim_msg.user = dict()
    in_jim_msg.user["account_name"] = "guest"
    in_jim_msg.user["password"] = "12345"
    socket_, out_jim_msg = server.dispatch_message(socket.socket(socket.AF_INET, socket.SOCK_STREAM), in_jim_msg)
    assert out_jim_msg.response == RESPONSE_SUCCESS_OK

    # повторная авторизация недопустима
    in_jim_msg = JimMessage(DEFAULT_ENCODING)
    in_jim_msg.action = ACTION_AUTH
    in_jim_msg.user = dict()
    in_jim_msg.user["account_name"] = "guest"
    in_jim_msg.user["password"] = "12345"
    socket_, out_jim_msg = server.dispatch_message(socket.socket(socket.AF_INET, socket.SOCK_STREAM), in_jim_msg)
    assert out_jim_msg.response == RESPONSE_CLIENT_CONFLICT

    # авторизация неактивного пользователя недопустима
    server.user_list["guest"].is_active = False
    in_jim_msg = JimMessage(DEFAULT_ENCODING)
    in_jim_msg.action = ACTION_AUTH
    in_jim_msg.user = dict()
    in_jim_msg.user["account_name"] = "guest"
    in_jim_msg.user["password"] = "12345"
    socket_, out_jim_msg = server.dispatch_message(socket.socket(socket.AF_INET, socket.SOCK_STREAM), in_jim_msg)
    assert out_jim_msg.response == RESPONSE_CLIENT_FORBIDDEN
    server.user_list["guest"].is_active = True

    # presence-сообщение от авторизованного пользователя допустимо
    in_jim_msg = JimMessage(DEFAULT_ENCODING)
    in_jim_msg.action = ACTION_PRESENCE
    in_jim_msg.user = dict()
    in_jim_msg.user["account_name"] = "guest"
    socket_, out_jim_msg = server.dispatch_message(server.user_list["guest"].socket, in_jim_msg)
    assert out_jim_msg.response == RESPONSE_SUCCESS_OK

    # отправка сообщения несуществующему пользователю недопустима
    in_jim_msg = JimMessage(DEFAULT_ENCODING)
    in_jim_msg.action = ACTION_MSG
    in_jim_msg.from_ = "guest"
    in_jim_msg.to_ = "superman"
    in_jim_msg.encoding = DEFAULT_ENCODING
    in_jim_msg.message = "Hello world!"
    socket_, out_jim_msg = server.dispatch_message(server.user_list["guest"].socket, in_jim_msg)
    assert out_jim_msg.response == RESPONSE_CLIENT_NOT_FOUND

    # авторизация нового пользователя = создание нового пользователя
    in_jim_msg = JimMessage(DEFAULT_ENCODING)
    in_jim_msg.action = ACTION_AUTH
    in_jim_msg.user = dict()
    in_jim_msg.user["account_name"] = "superman"
    in_jim_msg.user["password"] = "54321"
    socket_, out_jim_msg = server.dispatch_message(socket.socket(socket.AF_INET, socket.SOCK_STREAM), in_jim_msg)
    assert out_jim_msg.response == RESPONSE_SUCCESS_OK

    # отправка сообщения пользователю не в сети недопустима
    server.user_list["superman"].is_alive = False
    in_jim_msg = JimMessage(DEFAULT_ENCODING)
    in_jim_msg.action = ACTION_MSG
    in_jim_msg.from_ = "guest"
    in_jim_msg.to_ = "superman"
    in_jim_msg.encoding = DEFAULT_ENCODING
    in_jim_msg.message = "Hello world!"
    socket_, out_jim_msg = server.dispatch_message(server.user_list["guest"].socket, in_jim_msg)
    assert out_jim_msg.response == RESPONSE_CLIENT_OFFLINE

    # на quit-сообщение ответ не высылается
    in_jim_msg = JimMessage(DEFAULT_ENCODING)
    in_jim_msg.action = ACTION_QUIT
    socket_, out_jim_msg = server.dispatch_message(socket.socket(socket.AF_INET, socket.SOCK_STREAM), in_jim_msg)
    assert out_jim_msg is None

    # авторизация с неверным паролем недопустима
    in_jim_msg = JimMessage(DEFAULT_ENCODING)
    in_jim_msg.action = ACTION_AUTH
    in_jim_msg.user = dict()
    in_jim_msg.user["account_name"] = "guest"
    in_jim_msg.user["password"] = "54321"
    socket_, out_jim_msg = server.dispatch_message(socket.socket(socket.AF_INET, socket.SOCK_STREAM), in_jim_msg)
    assert out_jim_msg.response == RESPONSE_CLIENT_INVALID_CRED
