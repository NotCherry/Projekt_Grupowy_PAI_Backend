"""!
@file visualization.py
@brief Moduł generowania wizualizacji bukietów za pomocą modelu Stable Diffusion.
"""

import os
from dotenv import load_dotenv
import uuid
from pathlib import Path
from optimum.intel import OVStableDiffusionPipeline
import torch
from optimum.intel.openvino.modeling_diffusion import OVStableDiffusionPipeline
import io
import base64


load_dotenv()

## Katalog przechowywania wygenerowanych wizualizacji
IMAGES_DIR = Path("static/visualizations")
IMAGES_DIR.mkdir(parents=True, exist_ok=True)

## Globalny obiekt pipeline'u modelu (lazy loading)
_pipe = None


def get_model():
    """!
    @brief Ładuje model SDXS-512 OpenVINO przy pierwszym wywołaniu.
    
    @return Pipeline modelu Stable Diffusion
    @note Model jest ładowany tylko raz i przechowywany w pamięci
    """
    global _pipe
    if _pipe is None:
        print("Loading SDXS-512 OpenVINO model...")
        _pipe = OVStableDiffusionPipeline.from_pretrained(
            "rupeshs/sdxs-512-0.9-openvino",
            ov_config={"CACHE_DIR": ""}
        )
        print("Model loaded!")
    return _pipe


async def generate_bouquet_visualization(order_data: dict) -> str:
    """!
    @brief Generuje wizualizację bukietu na podstawie danych zamówienia.
    
    @param order_data Słownik zawierający listy: flowers, papers, ribbons
    @return Obraz w formacie base64 data URL lub placeholder w przypadku błędu
    """
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
    """!
    @brief Tworzy tekstowy prompt dla modelu AI na podstawie składu zamówienia.
    
    @param order_data Słownik z kluczami: flowers (quantity, name), papers (name), ribbons (name)
    @return Sformatowany prompt w języku angielskim
    """
    flowers = order_data.get('flowers', [])
    papers = order_data.get('papers', [])
    ribbons = order_data.get('ribbons', [])
    
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
    """!
    @brief Zwraca URL do obrazu zastępczego w przypadku błędu.
    
    @return URL do placeholder image
    """
    return "https://via.placeholder.com/1024x1024.png?text=Bouquet+Visualization"
