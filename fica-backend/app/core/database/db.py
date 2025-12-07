from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from app.core.config import config
from contextlib import contextmanager

engine = create_engine(config.DB_URL)

SessionLocal = sessionmaker(
    autocommit  = False,
    autoflush   = False,
    bind        = engine,
)

Base = declarative_base()

def db_status():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@contextmanager
def get_raw_connection():
    conn = engine.raw_connection()
    try:
        yield conn
    finally:
        conn.close()
