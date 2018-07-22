# This Python file uses the following encoding: utf-8

import pytest

from server_argv import parse_server_args


def test_parse_server_args():
    argv = ("server_main.py",)
    assert parse_server_args(argv) == (None, None)

    argv = ("server_main.py", "-a")
    assert parse_server_args(argv) == (None, None)

    argv = ("server_main.py", "-p")
    assert parse_server_args(argv) == (None, None)
    
    argv = ("server_main.py", "-a", "localhost")
    assert parse_server_args(argv) == ("localhost", None)

    argv = ("server_main.py", "-p", "7777")
    assert parse_server_args(argv) == (None, 7777)
    
    argv = ("server_main.py", "-p", "XXX")
    assert parse_server_args(argv) == (None, None)
    
    argv = ("server_main.py", "-a", "localhost", "-p", "7777")
    assert parse_server_args(argv) == ("localhost", 7777)

