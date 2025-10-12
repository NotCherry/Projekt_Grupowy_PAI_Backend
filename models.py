from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel


# Database Models
class Flower(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    icon: str
    price: float


class Paper(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    icon: str
    price: float


class Ribbon(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    icon: str
    price: float


class Order(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    order_number: str = Field(index=True, unique=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    total_price: float
    
    # Gift options
    is_gift: bool = False
    recipient_name: Optional[str] = None
    recipient_address: Optional[str] = None
    greeting_card: Optional[str] = None
    
    # Visualization
    visualization_url: Optional[str] = None
    
    # Relationships
    order_flowers: List["OrderFlower"] = Relationship(back_populates="order")
    order_papers: List["OrderPaper"] = Relationship(back_populates="order")
    order_ribbons: List["OrderRibbon"] = Relationship(back_populates="order")


class OrderFlower(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    order_id: int = Field(foreign_key="order.id")
    flower_id: int = Field(foreign_key="flower.id")
    quantity: int
    price_at_order: float
    
    order: Order = Relationship(back_populates="order_flowers")


class OrderPaper(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    order_id: int = Field(foreign_key="order.id")
    paper_id: int = Field(foreign_key="paper.id")
    price_at_order: float
    
    order: Order = Relationship(back_populates="order_papers")


class OrderRibbon(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    order_id: int = Field(foreign_key="order.id")
    ribbon_id: int = Field(foreign_key="ribbon.id")
    price_at_order: float
    
    order: Order = Relationship(back_populates="order_ribbons")


# Request/Response Models
class FlowerItem(BaseModel):
    id: int
    quantity: int


class PaperItem(BaseModel):
    id: int


class RibbonItem(BaseModel):
    id: int


class GiftOptions(BaseModel):
    isGift: bool
    recipientName: str
    recipientAddress: str
    greetingCard: str


class OrderCreate(BaseModel):
    flowers: List[FlowerItem]
    papers: List[PaperItem]
    ribbons: List[RibbonItem]
    totalPrice: float
    giftOptions: Optional[GiftOptions] = None


class VisualizationRequest(BaseModel):
    flowers: List[FlowerItem]
    papers: List[PaperItem]
    ribbons: List[RibbonItem]
    totalPrice: float
    giftOptions: Optional[GiftOptions] = None


class VisualizationResponse(BaseModel):
    imageUrl: str


class OrderResponse(BaseModel):
    orderId: str
    message: str


class FlowerDetail(BaseModel):
    id: int
    name: str
    quantity: int
    price: float


class PaperDetail(BaseModel):
    id: int
    name: str
    price: float


class RibbonDetail(BaseModel):
    id: int
    name: str
    price: float


class GiftOptionsResponse(BaseModel):
    recipientName: str
    recipientAddress: str
    greetingCard: str


class OrderHistoryItem(BaseModel):
    id: str
    createdAt: datetime
    totalPrice: float
    flowers: List[FlowerDetail]
    papers: List[PaperDetail]
    ribbons: List[RibbonDetail]
    giftOptions: Optional[GiftOptionsResponse] = None
    visualizationUrl: Optional[str] = None
