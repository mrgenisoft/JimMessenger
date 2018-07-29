# This Python file uses the following encoding: utf-8

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
    
