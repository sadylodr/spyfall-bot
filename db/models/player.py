from sqlalchemy import Column, Integer, BigInteger, String, ForeignKey
from sqlalchemy.orm import relationship
from db.database import Base

class Player(Base):
    __tablename__ = "players"
    
    id = Column()
    telegram_id = Column()
    username = Column()
    
    room_id = Column(Integer, ForeignKey("game_rooms.id", on_delete="CASCADE"), nullable=False)
    
    role = Column(String, nullable=False)
    
    room = relationship("GameRoom", back_populates="players")
    
    def __repr__(self):
        return f"<Player(tg_id={self.telegram_id}, role='{self.role}')>"