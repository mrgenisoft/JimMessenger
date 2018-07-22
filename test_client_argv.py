# This Python file uses the following encoding: utf-8

import pytest

from client_argv import parse_client_args


def test_parse_server_args():
    argv = ("client_main.py",)
    assert parse_client_args(argv) == (None, None)

    argv = ("client_main.py", "localhost")
    assert parse_client_args(argv) == ("localhost", None)

    argv = ("client_main.py", "localhost", "XXX")
    assert parse_client_args(argv) == ("localhost", None)
    
    argv = ("client_main.py", "localhost", "7777")
    assert parse_client_args(argv) == ("localhost", 7777)
