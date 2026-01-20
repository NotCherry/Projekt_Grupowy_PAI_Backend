from typing import List, Optional
from datetime import date, time
from sqlalchemy import Column, Integer, String, ForeignKey, Date, Time
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from pydantic import BaseModel


Base = declarative_base()


class Product(Base):
    """!
    @brief Model produktu w sklepie kwiaciarni.
    
    Klasa reprezentuje produkty dostępne w systemie. Produkty mogą należeć 
    do różnych kategorii (kwiaty, papier, wstążki, zieleń).
    """
    __tablename__ = "products"

    ## Unikalny identyfikator produktu (klucz główny)
    id = Column(Integer, primary_key=True, index=True)
    
    ## Nazwa produktu
    name = Column(String, index=True)
    
    ## Cena produktu w groszach
    price = Column(Integer)
    
    ## Ścieżka do pliku graficznego produktu
    image = Column(String)
    
    ## Kategoria produktu (domyślnie: "flower")
    category = Column(String, default="flower")
    
    ## Maksymalna dostępna ilość produktu w magazynie
    max_quantity = Column(Integer, default=0)


class Order(Base):
    """!
    @brief Model zamówienia klienta.
    
    Przechowuje informacje o zamówieniu wraz z danymi klienta oraz 
    wygenerowaną wizualizacją bukietu. Zamówienie zawiera listę 
    elementów (OrderItem).
    """
    __tablename__ = "orders"

    ## Unikalny identyfikator zamówienia (klucz główny)
    id = Column(Integer, primary_key=True, index=True)
    
    ## URL do wygenerowanego obrazu wizualizacji bukietu
    image_url = Column(String, nullable=True)
    
    ## Pseudonim klienta składającego zamówienie
    pseudonim = Column(String(100), nullable=True)
    
    ## Data odbioru zamówienia
    data = Column(Date, nullable=True)
    
    ## Godzina odbioru zamówienia
    godzina = Column(Time, nullable=True)
    
    ## Sposób odbioru zamówienia (np. "odbiór osobisty", "dostawa")
    odbior = Column(String(50), nullable=True)
    
    ## Forma płatności (np. "gotówka", "karta", "przelew")
    platnosc = Column(String(50), nullable=True)

    ## Relacja do pozycji zamówienia (kaskadowe usuwanie)
    items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")


class OrderItem(Base):
    """!
    @brief Pozycja w zamówieniu.
    
    Reprezentuje pojedynczy element zamówienia - konkretny produkt 
    z określoną kategorią i ilością.
    """
    __tablename__ = "order_items"

    ## Unikalny identyfikator pozycji zamówienia (klucz główny)
    id = Column(Integer, primary_key=True, index=True)
    
    ## Identyfikator zamówienia, do którego należy pozycja (klucz obcy)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    
    ## Identyfikator produktu w pozycji (klucz obcy)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    
    ## Kategoria produktu (flower/paper/ribbon/foliage)
    category = Column(String, nullable=False)
    
    ## Ilość produktu w pozycji
    quantity = Column(Integer, default=1)
    
    ## Identyfikator wizualizacji powiązanej z pozycją
    viz_id = Column(Integer, nullable=True)
    
    ## Relacja do zamówienia nadrzędnego
    order = relationship("Order", back_populates="items")
    
    ## Relacja do produktu
    product = relationship("Product")


# Pydantic Models

class ItemBase(BaseModel):
    """!
    @brief Bazowa klasa dla elementów w żądaniach API.
    
    Zawiera wspólne pola dla wszystkich typów elementów (kwiaty, papier, wstążki).
    """
    
    ## Identyfikator produktu
    id: int
    
    ## Opcjonalna ścieżka do ikony produktu
    icon: Optional[str] = None


class FlowerItem(ItemBase):
    """!
    @brief Model reprezentujący kwiat w żądaniu.
    
    Rozszerza ItemBase o pole ilości, specyficzne dla kwiatów.
    """
    
    ## Ilość kwiatów danego typu
    quantity: int


class PaperItem(ItemBase):
    """!
    @brief Model reprezentujący papier ozdobny w żądaniu.
    
    Dziedziczy po ItemBase bez dodatkowych pól.
    """
    pass


class RibbonItem(ItemBase):
    """!
    @brief Model reprezentujący wstążkę w żądaniu.
    
    Dziedziczy po ItemBase bez dodatkowych pól.
    """
    pass


class VisualizationRequest(BaseModel):
    """!
    @brief Żądanie generowania wizualizacji bukietu.
    
    Zawiera listy wszystkich elementów (kwiaty, papier, wstążki), 
    które mają być uwzględnione w generowanej wizualizacji.
    """
    
    ## Lista kwiatów do wizualizacji
    flowers: List[FlowerItem] = []
    
    ## Lista papierów ozdobnych do wizualizacji
    papers: List[PaperItem] = []
    
    ## Lista wstążek do wizualizacji
    ribbons: List[RibbonItem] = []


class VisualizationResponse(BaseModel):
    """!
    @brief Odpowiedź z wygenerowaną wizualizacją.
    
    Zawiera URL do wygenerowanego obrazu bukietu.
    """
    
    ## URL do wygenerowanego obrazu wizualizacji
    imageUrl: str


class CreateOrderRequest(BaseModel):
    """!
    @brief Żądanie utworzenia nowego zamówienia.
    
    Zawiera dane klienta z formularza HTML oraz listę wybranych produktów 
    (kwiaty, papier, wstążki) wraz z opcjonalnym ID wizualizacji.
    """
    
    ## Pseudonim klienta
    pseudonim: Optional[str] = None
    
    ## Data odbioru zamówienia
    data: Optional[date] = None
    
    ## Godzina odbioru zamówienia
    godzina: Optional[time] = None
    
    ## Sposób odbioru (np. "odbiór osobisty", "dostawa")
    odbior: Optional[str] = None
    
    ## Forma płatności (np. "gotówka", "karta")
    platnosc: Optional[str] = None
    
    ## Lista wybranych kwiatów
    flowers: List[FlowerItem] = []
    
    ## Lista wybranych papierów
    papers: List[PaperItem] = []
    
    ## Lista wybranych wstążek
    ribbons: List[RibbonItem] = []
    
    ## ID wcześniej wygenerowanej wizualizacji (jeśli istnieje)
    visualization_id: Optional[int] = None


class CreateOrderResponse(BaseModel):
    """!
    @brief Odpowiedź po utworzeniu zamówienia.
    
    Zawiera ID utworzonego zamówienia oraz komunikat potwierdzający.
    """
    
    ## Identyfikator nowo utworzonego zamówienia
    order_id: int
    
    ## Komunikat potwierdzający utworzenie zamówienia
    message: str


class OrderItemResponse(BaseModel):
    """!
    @brief Model pozycji zamówienia w odpowiedzi API.
    
    Reprezentuje pojedynczy element zamówienia z danymi produktu.
    """
    
    ## Identyfikator produktu
    product_id: int
    
    ## Nazwa produktu
    product_name: str
    
    ## Kategoria produktu
    category: str
    
    ## Zamówiona ilość
    quantity: int
    
    ## Cena jednostkowa produktu w groszach
    price: int


class OrderDetailResponse(BaseModel):
    """!
    @brief Szczegółowe informacje o zamówieniu.
    
    Zawiera pełne dane zamówienia: informacje o kliencie, listę produktów,
    całkowitą cenę oraz URL wizualizacji.
    """
    
    ## Identyfikator zamówienia
    order_id: int
    
    ## Pseudonim klienta
    pseudonim: Optional[str] = None
    
    ## Data odbioru
    data: Optional[date] = None
    
    ## Godzina odbioru
    godzina: Optional[time] = None
    
    ## Sposób odbioru
    odbior: Optional[str] = None
    
    ## Forma płatności
    platnosc: Optional[str] = None
    
    ## Lista pozycji w zamówieniu
    items: List[OrderItemResponse]
    
    ## Całkowita cena zamówienia w groszach
    total_price: int
    
    ## URL do wizualizacji bukietu
    image_url: Optional[str] = None
