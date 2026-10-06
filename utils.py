# -*- coding:utf-8 -*-
import sys, threading
from functools import wraps

def asyncc(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        threading.Thread(target=f, args=args, kwargs=kwargs).start()
    return wrapper

def write_txt(filename, content):
    with open(filename, 'a', encoding="utf-8") as txt:
        txt.write(content)

def rewriteable_word(word):
    for t in ['', word]: 
        sys.stdout.write('\033[K' + t + '\r')