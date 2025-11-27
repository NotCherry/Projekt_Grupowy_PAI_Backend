from sqlite3 import IntegrityError
from fastapi import FastAPI, Depends, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import func
import os
from database import engine, get_db, SessionLocal
from models import Base, Product
from typing import List, Optional
from pydantic import BaseModel
from ai_service import generate_bouquet_visualization

app = FastAPI()

origins = [
    "http://localhost:5500",    
    "http://127.0.0.1:5500",
    "http://localhost:9000",
    "http://127.0.0.1:9000",
    "*",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.mount("/images", StaticFiles(directory="images"), name="images")

Base.metadata.create_all(bind=engine)

@app.on_event("startup")
def startup_event():
    db = SessionLocal()
    try:
        flower_samples = [
            {"name": "Róża", "price": 10, "image": "roza_1.png", "category": "flower", "max_quantity": 0},
            {"name": "Goździk", "price": 5, "image": "gozdzika_1.png", "category": "flower", "max_quantity": 0},
            {"name": "Gerbera", "price": 6, "image": "gerber.png", "category": "flower", "max_quantity": 0},
            {"name": "Eustoma", "price": 8, "image": "eustoma.png", "category": "flower", "max_quantity": 0},
            {"name": "Frezja", "price": 4, "image": "frezja.png", "category": "flower", "max_quantity": 0},
            {"name": "Gipsówka", "price": 1, "image": "gipsowka.png", "category": "flower", "max_quantity": 0},
            {"name": "Hiacynt", "price": 9, "image": "hiacynt.png", "category": "flower", "max_quantity": 0},
            {"name": "Hortensje", "price": 15, "image": "hortensja.png", "category": "flower", "max_quantity": 0},
            {"name": "Chryzantema", "price": 6, "image": "hryzantemy.png", "category": "flower", "max_quantity": 0},
            {"name": "Irys", "price": 5, "image": "irys.png", "category": "flower", "max_quantity": 0},
            {"name": "Narcyz", "price": 3, "image": "narcyz.png", "category": "flower", "max_quantity": 0},
            {"name": "Piwonia", "price": 15, "image": "piwonia.png", "category": "flower", "max_quantity": 0},
            {"name": "Rumianek", "price": 1, "image": "rumianek.png", "category": "flower", "max_quantity": 0},
            {"name": "Słonecznik", "price": 7, "image": "slonecznik.png", "category": "flower", "max_quantity": 0},
            {"name": "Tulipan", "price": 4, "image": "tulipan.png", "category": "flower", "max_quantity": 0}
        ]
        
        foliage_samples = [
            {"name": "Asparagus", "price": 1, "image": "asparagus.png", "category": "foliage", "max_quantity": 0},
            {"name": "Aspidistra", "price": 2, "image": "aspidistra.png", "category": "foliage", "max_quantity": 0},
            {"name": "Bergrass", "price": 1, "image": "bergrass.png", "category": "foliage", "max_quantity": 0},
            {"name": "Pistacja", "price": 2, "image": "pistacja.png", "category": "foliage", "max_quantity": 0},
            {"name": "Salal", "price": 3, "image": "salal.png", "category": "foliage", "max_quantity": 0}
        ]
        
        paper_samples = [
            {"name": "Biały papier", "price": 2, "image": "papier_bialy.png", "category": "paper", "max_quantity": 1},
            {"name": "Różowy papier", "price": 2, "image": "papier_rozowy.png", "category": "paper", "max_quantity": 1},
            {"name": "Brązowy papier", "price": 2, "image": "papier_brazowy.png", "category": "paper", "max_quantity": 1},
            {"name": "Niebieski papier", "price": 2, "image": "papier_niebieski.png", "category": "paper", "max_quantity": 1},
            {"name": "Żółty papier", "price": 2, "image": "papier_zolty.png", "category": "paper", "max_quantity": 1}
        ]
        
        ribbon_samples = [
            {"name": "Czerwona wstążka", "price": 4, "image": "czerwona_wstazka.png", "category": "ribbon", "max_quantity": 1},
            {"name": "Różowa wstążka", "price": 4, "image": "rozowa_wstazka.png", "category": "ribbon", "max_quantity": 1},
            {"name": "Fioletowa wstążka", "price": 4, "image": "fioletowa_wstazka.png", "category": "ribbon", "max_quantity": 1},
            {"name": "Niebieska wstążka", "price": 4, "image": "niebieska_wstazka.png", "category": "ribbon", "max_quantity": 1},
            {"name": "Żółta wstążka", "price": 4, "image": "zolta_wstazka.png", "category": "ribbon", "max_quantity": 1}
        ]
        
        all_samples = flower_samples + foliage_samples + paper_samples + ribbon_samples
        
        count = db.query(func.count(Product.id)).scalar()
        if count == 0:
            for data in all_samples:
                item = Product(**data)
                db.add(item)
            db.commit()
            print("Database initialized with 15 flowers, 5 foliage, 5 papers, and 5 ribbons.")
    except IntegrityError:
        db.rollback()
    finally:
        db.close()

@app.get("/flowers")
def list_flowers(db: Session = Depends(get_db)):
    flowers = db.query(Product).filter(Product.category == "flower").all()
    return [
        {
            "id": f.id,
            "name": f.name,
            "price": f.price,
            "image": f"/images/{f.image}",
            "max_quantity": f.max_quantity
        }
        for f in flowers
    ]

@app.get("/foliage")
def list_foliage(db: Session = Depends(get_db)):
    foliage = db.query(Product).filter(Product.category == "foliage").all()
    return [
        {
            "id": f.id,
            "name": f.name,
            "price": f.price,
            "image": f"/images/{f.image}",
            "max_quantity": f.max_quantity
        }
        for f in foliage
    ]

@app.get("/papers")
def list_papers(db: Session = Depends(get_db)):
    papers = db.query(Product).filter(Product.category == "paper").all()
    return [
        {
            "id": f.id,
            "name": f.name,
            "price": f.price,
            "image": f"/images/{f.image}",
            "max_quantity": f.max_quantity
        }
        for f in papers
    ]

@app.get("/ribbons")
def list_ribbons(db: Session = Depends(get_db)):
    ribbons = db.query(Product).filter(Product.category == "ribbon").all()
    return [
        {
            "id": f.id,
            "name": f.name,
            "price": f.price,
            "image": f"/images/{f.image}",
            "max_quantity": f.max_quantity
        }
        for f in ribbons
    ]

@app.get("/flowers/{name}", response_class=FileResponse)
def get_flower_image(name: str, db: Session = Depends(get_db)):
    flower = db.query(Product).filter(Product.name == name, Product.category == "flower").first()
    if not flower:
        raise HTTPException(status_code=404, detail="Product not found")
    image_path = os.path.join("images", flower.image)
    if not os.path.exists(image_path):
        raise HTTPException(status_code=404, detail="Image file not found")
    return FileResponse(image_path)

@app.get("/foliage/{name}", response_class=FileResponse)
def get_foliage_image(name: str, db: Session = Depends(get_db)):
    foliage = db.query(Product).filter(Product.name == name, Product.category == "foliage").first()
    if not foliage:
        raise HTTPException(status_code=404, detail="Foliage not found")
    image_path = os.path.join("images", foliage.image)
    if not os.path.exists(image_path):
        raise HTTPException(status_code=404, detail="Image file not found")
    return FileResponse(image_path)

@app.get("/papers/{name}", response_class=FileResponse)
def get_paper_image(name: str, db: Session = Depends(get_db)):
    paper = db.query(Product).filter(Product.name == name, Product.category == "paper").first()
    if not paper:
        raise HTTPException(status_code=404, detail="Paper not found")
    image_path = os.path.join("images", paper.image)
    if not os.path.exists(image_path):
        raise HTTPException(status_code=404, detail="Image file not found")
    return FileResponse(image_path)

@app.get("/ribbons/{name}", response_class=FileResponse)
def get_ribbon_image(name: str, db: Session = Depends(get_db)):
    ribbon = db.query(Product).filter(Product.name == name, Product.category == "ribbon").first()
    if not ribbon:
        raise HTTPException(status_code=404, detail="Ribbon not found")
    image_path = os.path.join("images", ribbon.image)
    if not os.path.exists(image_path):
        raise HTTPException(status_code=404, detail="Image file not found")
    return FileResponse(image_path)

class ItemBase(BaseModel):
    id: int
    icon: Optional[str] = None

class FlowerItem(ItemBase):
    quantity: int

class PaperItem(ItemBase):
    pass

class RibbonItem(ItemBase):
    pass

class VisualizationRequest(BaseModel):
    flowers: List[FlowerItem] = []
    papers: List[PaperItem] = []
    ribbons: List[RibbonItem] = []

class VisualizationResponse(BaseModel):
    imageUrl: str

@app.post("/api/visualization", response_model=VisualizationResponse)
async def generate_visualization(
    request: VisualizationRequest,
    db: Session = Depends(get_db)
):    
    order_data = {'flowers': [], 'papers': [], 'ribbons': []}
    missing = []

    # flowers (allow category 'flower' AND 'foliage')
    for flower_item in request.flowers:
        product = db.query(Product).filter(Product.id == flower_item.id).first()
        if not product:
            missing.append(f"flower:{flower_item.id}")
            continue
        
        # Validate if it's acceptable category for "flowers" list in visualization
        if product.category not in ["flower", "foliage"]:
            missing.append(f"flower:{flower_item.id} (wrong category)")
            continue

        if product.max_quantity > 0 and flower_item.quantity > product.max_quantity:
            raise HTTPException(status_code=400, detail=f"Requested quantity for '{product.name}' exceeds max ({product.max_quantity})")
        order_data['flowers'].append({
            'id': product.id,
            'name': product.name,
            'quantity': flower_item.quantity,
            'icon': f"/images/{product.image}" if product.image else None
        })
    
    # papers
    for paper_item in request.papers:
        product = db.query(Product).filter(Product.id == paper_item.id, Product.category == "paper").first()
        if not product:
            missing.append(f"paper:{paper_item.id}")
            continue
        if product.max_quantity > 0:
            if product.max_quantity < 1:
                raise HTTPException(status_code=400, detail=f"Invalid max_quantity for paper '{product.name}'")
        order_data['papers'].append({
            'id': product.id,
            'name': product.name,
            'icon': f"/images/{product.image}" if product.image else None
        })
    
    # ribbons
    for ribbon_item in request.ribbons:
        product = db.query(Product).filter(Product.id == ribbon_item.id, Product.category == "ribbon").first()
        if not product:
            missing.append(f"ribbon:{ribbon_item.id}")
            continue
        if product.max_quantity > 0:
            if product.max_quantity < 1:
                raise HTTPException(status_code=400, detail=f"Invalid max_quantity for ribbon '{product.name}'")
        order_data['ribbons'].append({
            'id': product.id,
            'name': product.name,
            'icon': f"/images/{product.image}" if product.image else None
        })
    
    if missing:
        raise HTTPException(status_code=400, detail=f"Products error: {', '.join(missing)}")

    image_url = await generate_bouquet_visualization(order_data)
    
    return VisualizationResponse(imageUrl=image_url)
