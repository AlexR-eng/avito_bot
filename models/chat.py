from sqlalchemy import Column, String, Integer, Boolean, Text, ForeignKey
from core.database import Base

class ChatSession(Base):
    __tablename__ = "chat_sessions"
    
    chat_id = Column(String, primary_key=True, index=True)
    item_id = Column(Integer, index=True)
    ai_reply_count = Column(Integer, default=0)
    is_operator_connected = Column(Boolean, default=False)

class ChatMessage(Base):
    __tablename__ = "chat_messages"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    chat_id = Column(String, ForeignKey("chat_sessions.chat_id"), index=True)
    role = Column(String) # "user", "assistant", "system"
    content = Column(Text)