from sqlalchemy import Column, Integer, BigInteger, String, DateTime, func
from sqlalchemy.orm import relationship
from db.database import Base


class GameRoom(Base):
    __tablename__ = "game_rooms"
    
    id = Column(Integer, primary_key=True)
    room_code = Column(String, unique=True, nullable=False, index=True)
    creator_id = Column(BigInteger, nullable=False)
    
    status = Column(String, default="WAITING", nullable=False)
    theme = Column(String, nullable=False)
    location = Column(String, nullable=True)
    spy_id = Column(BigInteger, nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default = func.now())
    
    players = relationship("Player", back_populates="room", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<GameRoom(code='{self.room_code}', status='{self.status}', theme='{self.theme}')>"