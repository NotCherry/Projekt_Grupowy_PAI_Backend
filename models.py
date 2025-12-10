from typing import List, Optional
from datetime import date, time
from sqlalchemy import Column, Integer, String, ForeignKey, Date, Time
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from pydantic import BaseModel

Base = declarative_base()

class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    price = Column(Integer)
    image = Column(String)
    category = Column(String, default="flower")
    max_quantity = Column(Integer, default=0)


class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    image_url = Column(String, nullable=True)
    
    # Nowe pola z formularza HTML
    pseudonim = Column(String(100), nullable=True)
    data = Column(Date, nullable=True)
    godzina = Column(Time, nullable=True)
    odbior = Column(String(50), nullable=True)
    platnosc = Column(String(50), nullable=True)

    items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")


class OrderItem(Base):
    __tablename__ = "order_items"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    category = Column(String, nullable=False)   # flower/paper/ribbon/foliage
    quantity = Column(Integer, default=1)
    viz_id = Column(Integer, nullable=True)
    
    order = relationship("Order", back_populates="items")
    product = relationship("Product")


# Pydantic Models
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


class CreateOrderRequest(BaseModel):
    # Dane z formularza HTML
    pseudonim: Optional[str] = None
    data: Optional[date] = None
    godzina: Optional[time] = None
    odbior: Optional[str] = None
    platnosc: Optional[str] = None
    
    # Dane produktów
    flowers: List[FlowerItem] = []
    papers: List[PaperItem] = []
    ribbons: List[RibbonItem] = []
    visualization_id: Optional[int] = None

class CreateOrderResponse(BaseModel):
    order_id: int
    message: str

class OrderItemResponse(BaseModel):
    product_id: int
    product_name: str
    category: str
    quantity: int
    price: int

class OrderDetailResponse(BaseModel):
    order_id: int
    # Dane klienta z formularza
    pseudonim: Optional[str] = None
    data: Optional[date] = None
    godzina: Optional[time] = None
    odbior: Optional[str] = None
    platnosc: Optional[str] = None
    # Dane zamówienia
    items: List[OrderItemResponse]
    total_price: int
    image_url: Optional[str] = None
