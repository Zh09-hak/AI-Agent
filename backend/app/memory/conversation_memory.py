from sqlalchemy.orm import Session as DBSession
from app.database.models import Session as SessionModel, Message
from datetime import datetime
import uuid


class ConversationMemory:    
    @staticmethod
    def get_or_create_session(db: DBSession, session_id: str | None = None) -> str:
        if session_id:
            session = db.query(SessionModel).filter(SessionModel.session_id == session_id).first()
            if session:
                return session.session_id
            else:
                new_session = SessionModel(session_id=session_id)
                db.add(new_session)
                db.commit()
                return session_id
        new_session_id = str(uuid.uuid4())
        new_session = SessionModel(session_id=new_session_id)
        db.add(new_session)
        db.commit()
        
        return new_session_id
    
    @staticmethod
    def add_message(db: DBSession, session_id: str, role: str, content: str) -> None:
        message = Message(
            session_id=session_id,
            role=role,
            content=content,
        )
        db.add(message)
        db.commit()
    
    @staticmethod
    def get_history(db: DBSession, session_id: str, max_messages: int = 5) -> list[dict]:
        messages = db.query(Message).filter(
            Message.session_id == session_id
        ).order_by(Message.created_at.desc()).limit(max_messages).all()
        
        return [
            {"role": msg.role, "content": msg.content}
            for msg in reversed(messages)
        ]
    
    @staticmethod
    def rewrite_query_with_history(
        current_query: str, 
        history: list[dict]
    ) -> str:
        if not history:
            return current_query
        
        last_user_message = ""
        for msg in reversed(history):
            if msg["role"] == "user":
                last_user_message = msg["content"]
                break
        
        if not last_user_message or last_user_message == current_query:
            return current_query
            
        if len(current_query.split()) < 5:
            return f"Previous context: {last_user_message}\n\nCurrent follow-up question: {current_query}"
            
        return current_query

memory = ConversationMemory()