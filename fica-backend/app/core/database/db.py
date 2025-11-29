from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from app.core.config import config 

engine          = create_engine(config.DB_URL)
SessionLocal    = sessionmaker(
    autocommit      = False, 
    autoflush       = False, 
    bind            = engine
)
Base            = declarative_base()

def db_status():
    db = SessionLocal()
    try:
        yield db
    finally: 
        db.close()
