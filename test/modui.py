import gradio as g

from typing import Callable, List, Any
from inspect import signature, isfunction, getmembers, getsource

class Page():
    known_gtypes = ["text", "number", "bool"]

    def find_inputs_outputs(self, fn) -> List[str]:
        """
        Infer input and output types from function type annotations
        """
        def get_annotations(fn):
            return fn.__annotations__

        def to_gtype(t) -> str:
            if t is str: return "text"
            if t is float or t is int: return "number"
            if t is bool: return "bool"
            return ""

        def to_gtypes(t) -> List[str]:
            if t is not list:
                return None

            gtypes = []
            for i in t:
                gt = to_gtype(i)
                if gt: gtypes.append(gt)

            if len(gtypes) == len(t):
                return gtypes

            return None

        inputs = []
        outputs = []

        annotations = get_annotations(fn)

        if 'return' in annotations:
            return_type = to_gtype(annotations['return'])
            if return_type: 
                outputs.append(return_type)
            else:
                outputs = to_gtypes(annotations['return'])

        for i in range(fn.__code__.co_argcount):
            var_name = fn.__code__.co_varnames[i]
            if var_name in annotations:
                input = to_gtype(annotations[var_name])
                if input: inputs.append(input)

        if len(inputs) != fn.__code__.co_argcount:
            inputs = None

        return inputs, outputs

    def __init__(self, fn: Callable, config: Any, **kwargs):
        if not isfunction(fn) or fn.__code__.co_argcount == 0:
            raise ValueError('The first argument is either not a callable function or a parameterless function.')

        # first, infer input and output types from callback function signature
        fn_inputs, fn_outputs = self.find_inputs_outputs(fn)

        # if that doesn't work, then require explicit designations
        if not fn_inputs or not fn_outputs:
            inputs = kwargs.get('inputs')
            outputs = kwargs.get('outputs')

            if not fn_inputs and (not inputs or type(inputs) is not list):
                raise ValueError('Input type of the callback function is not specified.')

            if not fn_outputs and (not outputs or type(outputs) is not list):
                raise ValueError('Output type of the callback function is not specified.')

            if not fn_inputs:
                for input in inputs:
                    if not isinstance(input, str) or input not in self.known_gtypes:
                        raise ValueError('Invalid input type of the callback function.')

                if len(inputs) != fn.__code__.co_argcount:
                    raise ValueError("The number of inputs and the callback function's arguments are mismatched.")

                fn_inputs = inputs

            if not fn_outputs:
                for output in outputs:
                    if not isinstance(output, str) or output not in self.known_gtypes:
                        raise ValueError('Invalid output type of the callback function.')

                fn_outputs = outputs

        # filter out special attributes and class instances, only deal with regular attributes with basic types
        def is_basic_type(v):
            t = type(v)
            return t is int or t is float or t is str or t is bool

        controls = {}
        members = getmembers(config)
        for member in members:
            if not member[0].startswith("_") and is_basic_type(member[1]):
                controls[member[0]] = member[1]

        if len(controls) == 0:
            raise ValueError('The config parameter has no controllable attribute.')

        self.fn = fn
        self.config = config
        self.controls = controls
        self.inputs = fn_inputs
        self.outputs = fn_outputs

    def launch(self):
        for control in self.controls:
            print(control)