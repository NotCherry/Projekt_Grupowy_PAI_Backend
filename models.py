from typing import List, Optional
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

from typing import List
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

    items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")


class OrderItem(Base):
    __tablename__ = "order_items"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    category = Column(String, nullable=False)   # flower/paper/ribbon/foliage
    quantity = Column(Integer, default=1)

    order = relationship("Order", back_populates="items")
    product = relationship("Product")

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
    order_id: int


class CreateOrderRequest(BaseModel):
    flowers: List[FlowerItem] = []
    papers: List[PaperItem] = []
    ribbons: List[RibbonItem] = []

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
    image_url: Optional[str]
    items: List[OrderItemResponse]
    total_price: int
