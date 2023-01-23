import pages as ui

from transformers import T5Tokenizer, T5ForConditionalGeneration

tokenizer = T5Tokenizer.from_pretrained("t5-small")
model = T5ForConditionalGeneration.from_pretrained("t5-small")

def translate(text):
    input_ids = tokenizer(text, return_tensors="pt").input_ids
    outputs = model.generate(input_ids, max_new_tokens=256)
    return tokenizer.decode(outputs[0], skip_special_tokens=True)

if __name__ == "__main__":
    ui.Page(translate, ["text"], ["text"], model.config).launch()