# This Python file uses the following encoding: utf-8

import sys
import logging
from functools import wraps
from datetime import date


def func_log(func):
    @wraps(func)
    def log_wrap(*args, **kwargs):
        res = func(*args, **kwargs)
        logger = logging.getLogger(logger_name)
        logger.debug(f"{func.__module__} {func.__name__}(args={args},kwargs={kwargs})={res}")
        return res
    return log_wrap
    

logger_name = f"jim_server_{date.today().isoformat()}"
logger = logging.getLogger(logger_name)
formatter = logging.Formatter("%(asctime)s %(levelname)s %(message)s")

fh = logging.FileHandler(f"{logger_name}.log", encoding="utf-8", delay=True)
fh.setLevel(logging.DEBUG)
fh.setFormatter(formatter)
logger.addHandler(fh)

sh = logging.StreamHandler(sys.stderr)
sh.setLevel(logging.DEBUG)
sh.setFormatter(formatter)
logger.addHandler(sh)

logger.setLevel(logging.DEBUG)

