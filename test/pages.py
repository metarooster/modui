import gradio as g

from typing import Callable, List, Any
from inspect import signature, isfunction, getmembers

class Page():
    known_g_types = ["text", "number", "bool"]

    def __init__(self, fn: Callable, inputs: List, outputs: List, config: Any):
        if not isfunction(fn) or type(inputs) is not list or type(outputs) is not list:
            raise ValueError('Page has an initial argument of a mismatched type.')

        for input in inputs:
            if not isinstance(input, str) or input not in self.known_g_types:
                raise ValueError('Invalid input type to the callback function.')

        for output in outputs:
            if not isinstance(output, str) or output not in self.known_g_types:
                raise ValueError('Invalid output type from the callback function.')

        if len(inputs) != fn.__code__.co_argcount:
            raise ValueError('The number of callback inputs and its argument count are not the same.')

        def is_basic_type(o):
            t = type(o)
            return t is int or t is float or t is str or t is bool

        controls = {}
        members = getmembers(config)
        for member in members:
            if not member[0].startswith("_") and is_basic_type(member[1]):
                controls[member[0]] = member[1]

        if len(controls) == 0:
            raise ValueError('The config parameter has no controllable attribute.')

        self.fn = fn
        self.inputs = inputs
        self.outputs = outputs
        self.config = config
        self.controls = controls

    def launch(self):
        members = getmembers(self.config)
        for member in members:
            print(member)