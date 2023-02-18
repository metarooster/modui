## CompVis Stable Diffusion from HuggingFace

This instruction downloads and set up CompVis Stable Diffusion model through the HuggingFace diffusers and transformers library. It pulls relevant Python packages that allows the model to run on a discrete consumer graphics GPU e.g. NVIDIA RTX 2070, AMD RX 6500 XT, etc. with the help of DirectML. You won't need the huge CUDA package as a prerequisite. It is based on the prior work of [Neil McAlister](https://www.travelneil.com/stable-diffusion-windows-amd.html) with additional steps for better execution performance.

### Installing Dependency Packages
We need a few Python packages, namely the HuggingFace script libraries for transformers and diffusers along with ONNX Runtime for DirectML.

```
pip install diffusers transformers onnxruntime-directml onnx
```

### Downloading the Model
We first need to download the model from HuggingFace. You need an account at HuggingFace, so if you haven't done so, now is the time. Once you've set up a HuggingFace account, go generate an access token (just follow their instruction in the web site). 

Once you have the account and an access token, authenticate yourself in a terminal or powershell console by running the following command.

```
huggingface-cli.exe login
```

It'll ask for your access token, which you can find on your account profile `Settings -> Access Tokens`, just copy it from here and carefully paste it on this prompt. Note that you won't see anything appear on the prompt when you paste it, that's fine. It's there already, just hit Enter. You'll start downloading the model from HuggingFace.

### Converting to ONNX
The model is trained with PyTorch so it can naturally convert to ONNX. Since we'll be using DirectML through ONNX Runtime, this step is needed. The script `convert_stable_diffusion_checkpoint_to_onnx.py` you already have here is just a local copy of the same file from the [HuggingFace diffusers GitHub repo](https://github.com/huggingface/diffusers/blob/main/scripts/convert_stable_diffusion_checkpoint_to_onnx.py), so you don't need to clone that repo. 

```
python convert_stable_diffusion_checkpoint_to_onnx.py --model_path="CompVis/stable-diffusion-v1-4" --output_path="./stable_diffusion_onnx" --fp16
```
This will run the conversion and put the result ONNX files under the `stable_diffusion_onnx` folder. For better performance, we recommend you convert the model to half-precision floating point data type using the `--fp16` option. 

*Note: As of this writing, you cannot run this `--fp16` option until you have installed CUDA support with Torch packages. That's a bit inefficient and will require up to 3 GB of extra disk space, but here is how to do it:*
```
pip install torch>=1.13.0+cu116 torchvision>=0.13.0+cu116 torchaudio>=0.13.0 --extra-index-url https://download.pytorch.org/whl/cu116
```

### Running the Model
You'll need a script that looks like what in the `text2image.py` file as follow. On a mid-range NVIDIA RTX 2070, a single image currently takes 20 seconds to generate from a prompt. It'll take up to 10 mins on the CPU.

```
from diffusers import StableDiffusionOnnxPipeline
pipe = StableDiffusionOnnxPipeline.from_pretrained("./stable_diffusion_onnx", provider="DmlExecutionProvider")
prompt = "a photo of Elon Musk and Bill Gates fighting in a boxing match."
image = pipe(prompt).images[0] 
image.save("./result.png")
```
*Note: The relative path specified here is relative to the base location of the project folder e.g. /modui/, not where this README.md file is located. Also, if you have an NVIDIA card and really want to run the model on CUDA for some reason, just replace the `onnxruntime-directml` package with `onnxruntime-gpu` package. Do not keep them both. Then, replace the `"DmlExecutionProvider"` name in the script above with `"CUDAExecutionProvider"`.*

