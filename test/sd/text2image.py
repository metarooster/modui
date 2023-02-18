from diffusers import StableDiffusionOnnxPipeline

pipe = StableDiffusionOnnxPipeline.from_pretrained("./test/sd/stable_diffusion_onnx", provider="DmlExecutionProvider")
prompt = "a photo of Elon Musk and Bill Gates fighting in a boxing match."
image = pipe(prompt).images[0] 
image.save("./test/sd/result.png")