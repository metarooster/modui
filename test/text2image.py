import modui
from diffusers import StableDiffusionOnnxPipeline

pipeline = StableDiffusionOnnxPipeline.from_pretrained("./stable_diffusion_onnx", provider="DmlExecutionProvider")

def generate(prompt: str):
    return pipeline(prompt).images[0]

generate("a photo of Elon Musk and Bill Gates fighting in a boxing match.").save("./sd_result.png")
#modui.Page(generate, pipeline.scheduler.config).launch()