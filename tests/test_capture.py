import pytest

def f(n):
    return n+1

def test_f():
    assert f(1) == 2
