# This Python file uses the following encoding: utf-8

import sys


from server_argv import parse_server_args
from jim_server import JimServer
from jim_user import JimUser


SERVER_HOST = ""
SERVER_PORT = 7777
MAX_USERS = 1
MAX_BUF_SIZE = 1024
PROBE_INTERVAL_SEC = 60
DEFAULT_ENCODING = "utf-8"


host, port = parse_server_args(sys.argv)

if host is None:
    host = SERVER_HOST

if port is None:
    port = SERVER_PORT

try:
    user_list = dict() # load_user_list()
    
except Exception as e:
    print(e)
    sys.exit(1)
    
try:
    jim_server = JimServer.start_server(host, port, MAX_USERS)
    jim_server.encoding = DEFAULT_ENCODING
    jim_server.max_buf_size = MAX_BUF_SIZE
    jim_server.probe_interval = PROBE_INTERVAL_SEC
    
except Exception as e:
    print(e)
    sys.exit(1)

jim_server.user_list = user_list
jim_server.run_server()
    

