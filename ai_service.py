import os
from dotenv import load_dotenv
import uuid
from pathlib import Path
from optimum.intel import OVStableDiffusionPipeline
load_dotenv()

# Katalog na wygenerowane obrazy
IMAGES_DIR = Path("static/visualizations")
IMAGES_DIR.mkdir(parents=True, exist_ok=True)

import torch
from optimum.intel.openvino.modeling_diffusion import OVStableDiffusionPipeline
import io
import base64

_pipe = None

def get_model():
    """Lazy loading modelu OpenVINO"""
    global _pipe
    if _pipe is None:
        print("Loading SDXS-512 OpenVINO model...")
        # Użyj gotowego modelu OpenVINO (szybsze!)
        _pipe = OVStableDiffusionPipeline.from_pretrained(
            "rupeshs/sdxs-512-0.9-openvino",
            ov_config={"CACHE_DIR": ""}
        )
        print("Model loaded!")
    return _pipe


async def generate_bouquet_visualization(order_data: dict) -> str:    
    # Przygotuj opis bukietu dla AI
    prompt = create_prompt_from_order(order_data)
    print(order_data)
    
    try:
        pipe = get_model()
        
        images = pipe(
            prompt=prompt,
            width=512,
            height=512,
            num_inference_steps=1,
            guidance_scale=1.0
        ).images
        
        buffered = io.BytesIO()
        images[0].save(buffered, format="PNG")
        img_base64 = base64.b64encode(buffered.getvalue()).decode()
        
        return f"data:image/png;base64,{img_base64}"
        
    except Exception as e:
        print(f"Błąd generowania wizualizacji: {e}")
        return generate_placeholder_image()


def create_prompt_from_order(order_data: dict) -> str:
    """Tworzy prompt dla AI na podstawie danych zamówienia"""
    
    flowers = order_data.get('flowers', [])
    papers = order_data.get('papers', [])
    ribbons = order_data.get('ribbons', [])
    
    # Buduj opis
    flower_desc = []
    for flower in flowers:
        flower_desc.append(f"{flower['quantity']} {flower['name'].lower()}")
    
    prompt = f"As a wonderfull florist create bouquet containing exacly {', '.join(flower_desc)}. "
    
    if papers:
        paper_names = [p['name'].lower() for p in papers]
        prompt += f"Wrapped in {', '.join(paper_names)}. "
    
    if ribbons:
        ribbon_names = [r['name'].lower() for r in ribbons]
        prompt += f"Decorated with {', '.join(ribbon_names)}. "
    
    prompt += "High quality, photorealistic, studio lighting, white background, elegant composition."
    
    return prompt


def generate_placeholder_image() -> str:
    """
    Generuje placeholder URL dla trybu demo
    W produkcji możesz zwrócić domyślny obraz
    """
    # Możesz użyć serwisu placeholder lub zwrócić lokalny obraz
    return "https://via.placeholder.com/1024x1024.png?text=Bouquet+Visualization"
