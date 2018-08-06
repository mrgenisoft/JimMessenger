# This Python file uses the following encoding: utf-8

import sys

from jim_client import JimClient, parse_client_args


SERVER_HOST = "localhost"
SERVER_PORT = 7777
DEFAULT_ENCODING = "utf-8"
MAX_BUF_SIZE = 1024
MESSAGE_PROMPT = ">>>"


host, port, read_only = parse_client_args(sys.argv)

if host is None:
    host = SERVER_HOST

if port is None:
    port = SERVER_PORT
    
if read_only is None:
    read_only = True
    
username = input("Введите логин: ")
password = input("Введите пароль: ")

try:
    jim_client = JimClient.start_client(host, port)
    jim_client.encoding = DEFAULT_ENCODING
    jim_client.max_buf_size = MAX_BUF_SIZE
    jim_client.message_prompt = MESSAGE_PROMPT
    jim_client.username = username
    jim_client.password = password
    jim_client.read_only = read_only
    
except Exception as e:
    print(e)
    sys.exit(1)

if jim_client.authorize():
    jim_client.run_client()
    jim_client.disconnect()

else:
    jim_client.close()
