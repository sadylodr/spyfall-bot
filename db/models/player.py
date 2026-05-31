from sqlalchemy import Column, Integer, BigInteger, String, ForeignKey
from sqlalchemy.orm import relationship
from db.database import Base

class Player(Base):
    __tablename__ = "players"
    
    id = Column(Integer, primary_key=True)
    telegram_id = Column(BigInteger, nullable=False)
    username = Column(String, nullable=True)
    
    room_id = Column(Integer, ForeignKey("game_rooms.id", ondelete="CASCADE"), nullable=False)
    
    role = Column(String, nullable=False)
    
    room = relationship("GameRoom", back_populates="players")
    
    def __repr__(self):
        return f"<Player(tg_id={self.telegram_id}, role='{self.role}')>"