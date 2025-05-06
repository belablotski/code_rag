import json
import logging

from functools import partial
from turtle import width
from pywebio import start_server, config
from pywebio.input import *
from pywebio.output import *
from pywebio.pin import *
from pywebio.session import set_env

# Theme: dark, sketchy, minty, yeti
@config(theme='dark', css_style='width: 100%')
def chat(q: str = None, iter: int = 0, clear=True) -> None:
    set_env(output_max_width = '100%')
    with use_scope('chat', clear=clear):
        if q is None:
            toast(f'Welcome to Code RAG app...', 3)
        else:
            put_text(q)
        put_textarea(f'user_input_{iter}', label='Enter your query:', rows=5, placeholder='Type your query here...')
        put_row([
            put_button('Submit', onclick=lambda: chat(pin[f'user_input_{iter}'], iter+1, False)),
            put_button('Reset', onclick=lambda: chat(None, 0, True))
        ], size='90px')

if __name__ == '__main__':
    logging.getLogger().setLevel(logging.DEBUG)
    start_server(chat, port=8080, debug=True)
