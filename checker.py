from flask import session
from functools import wraps


def check_logged_in(func: object) -> bool:
    @wraps(func)
    def wrapper(*argc, **kwargs):
        if 'logged_in' in session:
            return func(*argc, **kwargs)
        return 'You are NOT logged in!'
    return wrapper
