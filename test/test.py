import modui

from transformers import T5Tokenizer, T5ForConditionalGeneration

tokenizer = T5Tokenizer.from_pretrained("t5-small")
model = T5ForConditionalGeneration.from_pretrained("t5-small")

def translate(text: str) -> str:
    input_ids = tokenizer(text, return_tensors="pt").input_ids
    outputs = model.generate(input_ids, max_new_tokens=512)
    return tokenizer.decode(outputs[0], skip_special_tokens=True)

if __name__ == "__main__":
    modui.Page(translate, model.config).launch()