from sqlalchemy import Column, String, Integer, DateTime, create_engine, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
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


class Session(Base):
    __tablename__ = "sessions"
    
    session_id = Column(String, primary_key=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    messages = relationship("Message", back_populates="session", cascade="all, delete-orphan")


class Message(Base):
    __tablename__ = "messages"
    
    message_id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String, ForeignKey("sessions.session_id"), nullable=False)
    role = Column(String, nullable=False)
    content = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    session = relationship("Session", back_populates="messages")

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