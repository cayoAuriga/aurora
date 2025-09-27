# services/decorators.py
from fastapi import HTTPException
import functools
import logging

def with_error_handling(fn):
    @functools.wraps(fn)
    def wrapper(*args, **kwargs):
        try:
            return fn(*args, **kwargs)
        except HTTPException:
            raise
        except Exception as e:
            logging.error(f"Error in {fn.__name__}: {e}")
            raise HTTPException(500, "Internal server error")
    return wrapper

def with_logging(fn):
    @functools.wraps(fn)
    def wrapper(*args, **kwargs):
        logging.info(f"Executing {fn.__name__} with args {args} kwargs {kwargs}")
        result = fn(*args, **kwargs)
        logging.info(f"Completed {fn.__name__}")
        return result
    return wrapper
