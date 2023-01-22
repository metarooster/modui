import gradio as g

from typing import Any, Callable
from inspect import signature, isfunction

class Page():
    def __init__(self, fn: Callable, config: Any):
        self.fn = fn
        self.config = config

    def launch(self):
        if isfunction(self.fn):
            sig = signature(self.fn)
            code = self.fn.__code__
            arg_count = code.co_argcount
