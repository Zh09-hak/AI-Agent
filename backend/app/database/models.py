from sqlalchemy import Column, String, Integer, DateTime, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from pathlib import Path

Base = declarative_base()

class Document(Base):
    __tablename__ = "documents"
    
    document_id = Column(String, primary_key=True)
    filename = Column(String, nullable=False)
    file_hash = Column(String, nullable=False)
    file_size_bytes = Column(Integer, nullable=False)
    mime_type = Column(String, nullable=False)
    num_chunks = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    storage_path = Column(String, nullable=False)

db_dir = Path("data")
db_dir.mkdir(parents=True, exist_ok=True)

DATABASE_URL = f"sqlite:///{db_dir / 'app.db'}"
engine = create_engine(DATABASE_URL, echo=False)

Base.metadata.create_all(engine)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()