from sqlmodel import SQLModel, create_engine, Session, select
from models import Flower, Paper, Ribbon
import os

DATABASE_URL = "sqlite:///./flower_shop.db"

engine = create_engine(DATABASE_URL, echo=True)


def create_db_and_tables():
    """Tworzy wszystkie tabele w bazie danych"""
    SQLModel.metadata.create_all(engine)


def get_session():
    """Generator sesji bazy danych"""
    with Session(engine) as session:
        yield session


def seed_database():
    """Ładuje przykładowe dane do bazy danych"""
    
    # Sprawdź czy dane już istnieją
    with Session(engine) as session:
        existing_flowers = session.exec(select(Flower)).first()
        if existing_flowers:
            print("Baza danych już zawiera dane. Pomijam seed.")
            return
    
    print("Ładowanie przykładowych danych...")
    
    # Przykładowe kwiaty
    flowers = [
        Flower(name="Róża Czerwona", icon="🌹", price=5.50),
        Flower(name="Tulipan", icon="🌷", price=4.00),
        Flower(name="Lilia", icon="🌺", price=6.50),
        Flower(name="Słonecznik", icon="🌻", price=4.50),
        Flower(name="Goździk", icon="🌸", price=3.50),
        Flower(name="Orchidea", icon="🌼", price=8.00),
        Flower(name="Peonia", icon="💐", price=7.50),
        Flower(name="Margaretka", icon="🌼", price=3.00),
        Flower(name="Gerbera", icon="🌺", price=5.00),
        Flower(name="Frezja", icon="🌷", price=4.50),
    ]
    
    # Przykładowe papiery ozdobne
    papers = [
        Paper(name="Papier Klasyczny Biały", icon="📄", price=3.50),
        Paper(name="Papier Kremowy", icon="📃", price=4.00),
        Paper(name="Papier Premium Złoty", icon="📜", price=6.00),
        Paper(name="Papier Premium Srebrny", icon="📋", price=6.00),
        Paper(name="Papier Kraftowy", icon="📄", price=3.00),
        Paper(name="Papier Kolorowy Różowy", icon="📃", price=4.50),
        Paper(name="Papier Kolorowy Niebieski", icon="📄", price=4.50),
        Paper(name="Papier Transparentny", icon="📋", price=5.00),
    ]
    
    # Przykładowe wstążki
    ribbons = [
        Ribbon(name="Wstążka Jedwabna Czerwona", icon="🎀", price=2.50),
        Ribbon(name="Wstążka Satynowa Różowa", icon="🎗️", price=3.00),
        Ribbon(name="Wstążka Aksamitna Bordowa", icon="🎀", price=3.50),
        Ribbon(name="Wstążka Złota", icon="🎗️", price=4.00),
        Ribbon(name="Wstążka Srebrna", icon="🎀", price=4.00),
        Ribbon(name="Wstążka Organza Biała", icon="🎗️", price=2.50),
        Ribbon(name="Wstążka Jutowa", icon="🎀", price=2.00),
        Ribbon(name="Wstążka Koronkowa", icon="🎗️", price=3.50),
    ]
    
    # Dodaj do bazy danych
    with Session(engine) as session:
        for flower in flowers:
            session.add(flower)
        for paper in papers:
            session.add(paper)
        for ribbon in ribbons:
            session.add(ribbon)
        
        session.commit()
    
    print("✅ Przykładowe dane zostały załadowane do bazy danych!")
