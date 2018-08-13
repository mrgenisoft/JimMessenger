# This Python file uses the following encoding: utf-8

import pytest
import logging

from jim_client import parse_client_args


logging.disable(logging.CRITICAL)


def test_parse_client_args():
    argv = ("client_main.py",)
    assert parse_client_args(argv) == (None, None, None)
    
    argv = ("client_main.py", "-r")
    assert parse_client_args(argv) == (None, None, True)
    
    argv = ("client_main.py", "-w")
    assert parse_client_args(argv) == (None, None, False)
    
    argv = ("client_main.py", "-a")
    assert parse_client_args(argv) == (None, None, None)

    argv = ("client_main.py", "-p")
    assert parse_client_args(argv) == (None, None, None)
    
    argv = ("client_main.py", "-a", "localhost")
    assert parse_client_args(argv) == ("localhost", None, None)

    argv = ("client_main.py", "-p", "7777")
    assert parse_client_args(argv) == (None, 7777, None)
    
    argv = ("client_main.py", "-p", "XXX")
    assert parse_client_args(argv) == (None, None, None)
    
    argv = ("client_main.py", "-a", "localhost", "-p", "7777")
    assert parse_client_args(argv) == ("localhost", 7777, None)

    argv = ("client_main.py", "-r", "-a", "localhost", "-p", "7777")
    assert parse_client_args(argv) == ("localhost", 7777, True)

    argv = ("client_main.py", "-w", "-a", "localhost", "-p", "7777")
    assert parse_client_args(argv) == ("localhost", 7777, False)
    

