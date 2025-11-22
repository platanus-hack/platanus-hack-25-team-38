from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from config import settings
import os

# Usar POSTGRES_URL de settings o del entorno directamente
SQLALCHEMY_DATABASE_URL = settings.POSTGRES_URL or os.getenv("POSTGRES_URL", "postgresql://user:password@localhost/dbname")

engine = create_engine(SQLALCHEMY_DATABASE_URL, 
                        pool_pre_ping=True, 
                        pool_recycle=3600,
                        connect_args={
                            "keepalives": 1,
                            "keepalives_idle": 30,
                            "keepalives_interval": 10,
                            "keepalives_count": 5,
                        })

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    
    finally:
        db.close()