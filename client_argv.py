# This Python file uses the following encoding: utf-8

def parse_client_args(argv):
    try:
        host = argv[1]
    except:
        host = None
        
    try:
        port = int(argv[2])
    except:
        port = None
            
    return host, port
    