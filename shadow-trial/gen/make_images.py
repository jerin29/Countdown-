"""Generate photoreal stills locally with SDXL-Turbo on CPU.
Usage: python make_images.py prompts.json outdir
prompts.json: [{"name": "...", "prompt": "...", "w": 768, "h": 432, "seed": 1}]"""
import json, sys, os, time, torch
from diffusers import AutoPipelineForText2Image
torch.set_num_threads(os.cpu_count())
STYLE = ", photorealistic cinematic film still, 35mm, moody lighting, film grain"
NEG = "cartoon, anime, illustration, painting, 3d render, cgi, deformed, extra fingers, text, watermark, blurry"
pipe = AutoPipelineForText2Image.from_pretrained("stabilityai/sdxl-turbo", torch_dtype=torch.bfloat16, variant="fp16")
items = json.load(open(sys.argv[1])); out = sys.argv[2]; os.makedirs(out, exist_ok=True)
for it in items:
    path = os.path.join(out, it["name"] + ".png")
    if os.path.exists(path): continue
    t = time.time()
    img = pipe(prompt=it["prompt"] + STYLE, negative_prompt=NEG, num_inference_steps=it.get("steps", 4), guidance_scale=0.0,
               width=it.get("w", 512), height=it.get("h", 512), generator=torch.Generator().manual_seed(it.get("seed", 7))).images[0]
    img.save(path); print(it["name"], f"{time.time()-t:.0f}s", flush=True)
