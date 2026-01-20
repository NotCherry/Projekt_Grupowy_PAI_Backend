"""!
@file database.py
@brief Konfiguracja połączenia z bazą danych SQLite.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


## URL połączenia do bazy danych SQLite
SQLALCHEMY_DATABASE_URL = "sqlite:///./flowers.db"


## Silnik bazy danych SQLAlchemy
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

## Fabryka sesji bazodanowych
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    """!
    @brief Tworzy sesję bazodanową dla endpointów FastAPI.
    
    @yield Sesja SQLAlchemy
    @note Sesja jest automatycznie zamykana po użyciu
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
