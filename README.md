# Model UI

Model UI builds a Web UI page from a configuration via type inspection. It automatically updates the configuration whenever the corresponding UI widget is updated by the user. It then calls back to the specified user function whenever the Submit button on the generated page is clicked. The generated Web UI is launched via a local web server.

It can be used for testing the ML models you're working on, or demoing to interested parties. Under the hood, it leverages Gradio for UI construction and web server integration. 

## Sample

**Prerequisite**: Model UI requires Gradio 3.16 and Python 3.7 or above.

### Hello, Transformers ⚡

To launch a Model UI for "T5-small", one of the HuggingFace Transformer models

1. Install Gradio from pip. Note, the minimal supported Python version is 3.7.

```bash
pip install gradio 
```

2. Run the code below as a Python script. Only the first and last line are related to Model UI. In the middle, it's whatever code you're testing with. In this sample, it's the code necessary to run the "t5-small" model.

The `translate` function is the callback you give to Model UI. It will be called when the Submit button on the generated page is clicked. 

The `model.config` is the model configuration with a bunch of properties. Each of these properties corresponds one-to-one to a UI widget on the page.

Lastly, the `launch` method launches the generated page in a local web server. 

```python
import modui

from transformers import T5Tokenizer, T5ForConditionalGeneration

tokenizer = T5Tokenizer.from_pretrained("t5-small")
model = T5ForConditionalGeneration.from_pretrained("t5-small")

def translate(text: str) -> str:
    input_ids = tokenizer(text, return_tensors="pt").input_ids
    outputs = model.generate(input_ids, max_new_tokens=512)
    return tokenizer.decode(outputs[0], skip_special_tokens=True)

modui.Page(fn=translate, config=model.config).launch()
```

3. This sample will launch a local web server serving the generated page on [http://localhost:7860](http://localhost:7860/). Here is what it looks like in the web browser.

![Sample screenshot](./images/sample_screenshot.jpg)