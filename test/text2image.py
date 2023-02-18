import modui
from diffusers import StableDiffusionOnnxPipeline

pipeline = StableDiffusionOnnxPipeline.from_pretrained("./stable_diffusion_onnx", provider="DmlExecutionProvider")

def generate(prompt: str):
    return pipeline(prompt).images[0]

modui.Page(generate, pipeline.scheduler.config).launch()