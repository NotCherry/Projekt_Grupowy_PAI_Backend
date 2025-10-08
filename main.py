from fastapi import FastAPI, Depends, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import Session, select
from typing import List
import uuid
from datetime import datetime

from database import create_db_and_tables, get_session, seed_database
from models import (
    Flower, Paper, Ribbon, Order, OrderFlower, OrderPaper, OrderRibbon,
    OrderCreate, VisualizationRequest, VisualizationResponse, OrderResponse,
    FlowerDetail, PaperDetail, RibbonDetail, OrderHistoryItem,
    GiftOptionsResponse
)
from ai_service import generate_bouquet_visualization

app = FastAPI(title="Flower Shop API", version="1.0.0")

# CORS - pozwól na requesty z frontendu
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # W produkcji ustaw konkretne domeny
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serwuj statyczne pliki (obrazy wizualizacji)
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.on_event("startup")
def on_startup():
    """Inicjalizacja przy starcie aplikacji"""
    create_db_and_tables()
    seed_database()


@app.get("/")
def read_root():
    """Endpoint testowy"""
    return {"message": "Flower Shop API is running! 🌸"}


@app.get("/api/flowers", response_model=List[Flower])
def get_flowers(session: Session = Depends(get_session)):
    """Zwraca listę wszystkich kwiatów"""
    flowers = session.exec(select(Flower)).all()
    return flowers


@app.get("/api/papers", response_model=List[Paper])
def get_papers(session: Session = Depends(get_session)):
    """Zwraca listę wszystkich papierów ozdobnych"""
    papers = session.exec(select(Paper)).all()
    return papers


@app.get("/api/ribbons", response_model=List[Ribbon])
def get_ribbons(session: Session = Depends(get_session)):
    """Zwraca listę wszystkich wstążek"""
    ribbons = session.exec(select(Ribbon)).all()
    return ribbons


@app.post("/api/visualization", response_model=VisualizationResponse)
async def generate_visualization(
    request: VisualizationRequest,
    session: Session = Depends(get_session)
):
    """Generuje wizualizację bukietu używając AI"""
    
    # Pobierz szczegóły kwiatów, papierów i wstążek
    order_data = {
        'flowers': [],
        'papers': [],
        'ribbons': []
    }
    
    for flower_item in request.flowers:
        flower = session.get(Flower, flower_item.id)
        if flower:
            order_data['flowers'].append({
                'name': flower.name,
                'quantity': flower_item.quantity,
                'icon': flower.icon
            })
    
    for paper_item in request.papers:
        paper = session.get(Paper, paper_item.id)
        if paper:
            order_data['papers'].append({
                'name': paper.name,
                'icon': paper.icon
            })
    
    for ribbon_item in request.ribbons:
        ribbon = session.get(Ribbon, ribbon_item.id)
        if ribbon:
            order_data['ribbons'].append({
                'name': ribbon.name,
                'icon': ribbon.icon
            })
    
    # Generuj wizualizację
    image_url = await generate_bouquet_visualization(order_data)
    
    return VisualizationResponse(imageUrl=image_url)


@app.post("/api/orders", response_model=OrderResponse)
def create_order(
    order_data: OrderCreate,
    session: Session = Depends(get_session)
):
    """Tworzy nowe zamówienie"""
    
    # Generuj unikalny numer zamówienia
    order_number = f"ORD-{datetime.now().year}-{str(uuid.uuid4())[:8].upper()}"
    
    # Utwórz zamówienie
    order = Order(
        order_number=order_number,
        total_price=order_data.totalPrice,
        is_gift=order_data.giftOptions.isGift if order_data.giftOptions else False,
        recipient_name=order_data.giftOptions.recipientName if order_data.giftOptions else None,
        recipient_address=order_data.giftOptions.recipientAddress if order_data.giftOptions else None,
        greeting_card=order_data.giftOptions.greetingCard if order_data.giftOptions else None
    )
    
    session.add(order)
    session.commit()
    session.refresh(order)
    
    # Dodaj kwiaty do zamówienia
    for flower_item in order_data.flowers:
        flower = session.get(Flower, flower_item.id)
        if not flower:
            raise HTTPException(status_code=404, detail=f"Flower {flower_item.id} not found")
        
        order_flower = OrderFlower(
            order_id=order.id,
            flower_id=flower.id,
            quantity=flower_item.quantity,
            price_at_order=flower.price
        )
        session.add(order_flower)
    
    # Dodaj papiery do zamówienia
    for paper_item in order_data.papers:
        paper = session.get(Paper, paper_item.id)
        if not paper:
            raise HTTPException(status_code=404, detail=f"Paper {paper_item.id} not found")
        
        order_paper = OrderPaper(
            order_id=order.id,
            paper_id=paper.id,
            price_at_order=paper.price
        )
        session.add(order_paper)
    
    # Dodaj wstążki do zamówienia
    for ribbon_item in order_data.ribbons:
        ribbon = session.get(Ribbon, ribbon_item.id)
        if not ribbon:
            raise HTTPException(status_code=404, detail=f"Ribbon {ribbon_item.id} not found")
        
        order_ribbon = OrderRibbon(
            order_id=order.id,
            ribbon_id=ribbon.id,
            price_at_order=ribbon.price
        )
        session.add(order_ribbon)
    
    session.commit()
    
    return OrderResponse(
        orderId=order_number,
        message="Order placed successfully"
    )


@app.get("/api/orders", response_model=List[OrderHistoryItem])
def get_orders(session: Session = Depends(get_session)):
    """Zwraca historię zamówień"""
    
    orders = session.exec(select(Order).order_by(Order.created_at.desc())).all()
    
    result = []
    for order in orders:
        # Pobierz kwiaty
        flowers = []
        for order_flower in order.order_flowers:
            flower = session.get(Flower, order_flower.flower_id)
            if flower:
                flowers.append(FlowerDetail(
                    id=flower.id,
                    name=flower.name,
                    quantity=order_flower.quantity,
                    price=order_flower.price_at_order
                ))
        
        # Pobierz papiery
        papers = []
        for order_paper in order.order_papers:
            paper = session.get(Paper, order_paper.paper_id)
            if paper:
                papers.append(PaperDetail(
                    id=paper.id,
                    name=paper.name,
                    price=order_paper.price_at_order
                ))
        
        # Pobierz wstążki
        ribbons = []
        for order_ribbon in order.order_ribbons:
            ribbon = session.get(Ribbon, order_ribbon.ribbon_id)
            if ribbon:
                ribbons.append(RibbonDetail(
                    id=ribbon.id,
                    name=ribbon.name,
                    price=order_ribbon.price_at_order
                ))
        
        # Opcje prezentu
        gift_options = None
        if order.is_gift:
            gift_options = GiftOptionsResponse(
                recipientName=order.recipient_name,
                recipientAddress=order.recipient_address,
                greetingCard=order.greeting_card
            )
        
        result.append(OrderHistoryItem(
            id=order.order_number,
            createdAt=order.created_at,
            totalPrice=order.total_price,
            flowers=flowers,
            papers=papers,
            ribbons=ribbons,
            giftOptions=gift_options,
            visualizationUrl=order.visualization_url
        ))
    
    return result


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
