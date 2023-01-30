import gradio as g

from typing import Callable, List, Any
from inspect import isfunction, getmembers

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
        filters = kwargs.get('filters')

        def is_filtered(name):
            if not filters or type(filters) is not list: return False
            return name not in filters

        def is_basic_type(v):
            t = type(v)
            return t is int or (t is float and v > 0.001) or t is str or t is bool

        controls = {}
        members = getmembers(config)
        for member in members:
            if not member[0].startswith("_") and is_basic_type(member[1]) and not is_filtered(member[0]):
                controls[member[0]] = member[1]

        if not controls:
            raise ValueError('The config parameter has no controllable attribute.')

        if 'model_type' in controls:
            self.model_type = controls['model_type']
            controls.pop('model_type')
        else:
            self.model_type = '(null)'

        self.fn = fn
        self.config = config
        self.controls = controls
        self.inputs = fn_inputs
        self.outputs = fn_outputs

    def launch(self, share=False):
        """
        Create a UI page based on the controllable config parameters and launch a local web server to serve it.
        """
        def get_input_output_widgets():
            input = None
            input_type = self.inputs[0]
            if input_type == 'text':
                input = g.Textbox(lines=20, label=self.fn.__code__.co_varnames[0])
            elif input_type == 'number':
                input = g.Number(label=self.fn.__code__.co_varnames[0])

            output = None
            output_type = self.outputs[0]
            if output_type == 'text':
                output = g.Textbox(lines=20, label=self.fn.__name__)
            elif output_type == 'number':
                output = g.Number(label=self.fn.__name__)
            elif output_type == 'bool':
                output = g.Checkbox(label=self.fn.__name__)

            return input, output

        def get_primary_widget(k, v):
            t = type(v)
            if t is float and v <= 1:
                return g.Slider(value=v, minimum=0, maximum=1, label=k, interactive=True)
            if t is float or t is int:
                return g.Number(value=v, label=k, interactive=True)
            if t is bool:
                return g.Checkbox(value=v, label=k)
            return None

        def get_dropdown_widget(k, v):
            t = type(v)
            if t is str:
                return g.Dropdown(choices=[v], value=v, label=k, interactive=True)
            return None

        widgets = []

        def add_widget(widget):
            def fn(v):
                self.config.update({widget.label: v})
            widget.change(fn=fn, inputs=[widget], outputs=[])
            widgets.append(widget)

        def update_config(k, v):
            self.config.update({k:v})

        with g.Blocks() as form:
            with g.Row():
                g.Markdown("## Model UI 🚀")
            with g.Row():
                with g.Column(scale=5):
                    input_widget, output_widget = get_input_output_widgets()
                    with g.Row():
                        with g.Column(scale=1, min_width=100):
                            submit_button = g.Button(value='Submit')
                        with g.Column(scale=8):
                            g.Button(visible=False)

                with g.Column(scale=1, min_width=320):
                    g.Dropdown(choices=[self.model_type], value=self.model_type, label='model_type', interactive=True)
                    for k, v in self.controls.items():
                        widget = get_primary_widget(k, v)
                        if widget: add_widget(widget)

                    # it's more visually pleasing to have all the dropdowns show up towards the bottom of the page
                    for k, v in self.controls.items():
                        widget = get_dropdown_widget(k, v)
                        if widget: add_widget(widget)

            submit_button.click(fn=self.fn, inputs=[input_widget], outputs=[output_widget])

        form.launch(share=share)

