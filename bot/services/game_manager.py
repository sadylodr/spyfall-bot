import random
import string
from typing import Optional, List, Tuple, AsyncGenerator

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from db.database import AsyncSessionLocal
from db.models.game import GameRoom
from db.models.player import Player

from .content_loader import ContentLoader, content_loader


ROLE_SPY = "SPY"
ROLE_PLAYER = "PLAYER"
STATUS_ACTIVE = "ACTIVE"
STATUS_WAITING = "WAITING"
STATUS_FINISHED = "FINISHED"


class GameManager:
    def __init__(self, session: AsyncSession, content_loader: ContentLoader):
        self.session = session
        self.content_loader = content_loader
        
    def _generate_unique_code(self, length: int = 4) -> str:
        characters = string.ascii_uppercase + string.digits
        return ''.join(random.choice(characters) for _ in range(length))
    
    async def create_new_room(self, creator_id: int, theme: str) -> GameRoom:
        code = self._generate_unique_code()
        
        while await self.get_room_by_code(code) is not None:
            code = self._generate_unique_code()
            
        new_room = GameRoom(
            room_code=code,
            creator_id=creator_id,
            status=STATUS_WAITING,
            theme=theme
        )
        
        self.session.add(new_room)
        await self.session.commit()
        await self.session.refresh(new_room)
        
        await self.add_player_to_room(new_room.room_code, creator_id, username=None)
        
        return new_room
    
    async def get_room_by_code(self, code: str) -> Optional[GameRoom]:
        code = code.upper() 
        stmt = select(GameRoom).where(GameRoom.room_code == code)
        result = await self.session.execute(stmt)
        return result.scalars().first()
    
    async def add_player_to_room(self, code: str, telegram_id: int, username: Optional[str]) -> bool:
        room = await self.get_room_by_code(code)
        
        if not room or room.status != STATUS_WAITING:
            return False 
            
        stmt_check = select(Player).where(
            (Player.room_id == room.id) & (Player.telegram_id == telegram_id)
        )
        if (await self.session.execute(stmt_check)).scalars().first():
             return True 
             
        new_player = Player(
            telegram_id=telegram_id,
            username=username,
            room_id=room.id,
            role=ROLE_PLAYER 
        )
        
        self.session.add(new_player)
        await self.session.commit()
        return True
    
    async def get_room_players(self, code: str) -> List[Player]:
        code = code.upper()
        stmt = (
            select(GameRoom)
            .where(GameRoom.room_code == code)
            .options(selectinload(GameRoom.players))
        )
        result = await self.session.execute(stmt)
        room = result.scalars().first()
        
        if room:
            players = sorted(room.players, key=lambda p: p.telegram_id != room.creator_id)
            return players
        return []
    
    async def distribute_roles(self, room_code: str, min_players: int = 3) -> Optional[GameRoom]:
        room = await self.get_room_by_code(room_code)
        if not room or room.status != STATUS_WAITING:
            return None

        players = await self.get_room_players(room_code)
        
        if len(players) < min_players:
            return room 
            
        location = self.content_loader.get_random_location(room.theme)
        if not location:
            raise ValueError(f"Content list is empty or theme '{room.theme}' is invalid.")
            
        spy_player: Player = random.choice(players)
        
        room.location = location
        room.spy_id = spy_player.telegram_id
        room.status = STATUS_ACTIVE
        
        for player in players:
            if player.telegram_id == spy_player.telegram_id:
                player.role = ROLE_SPY
            else:
                player.role = ROLE_PLAYER 
                
            self.session.add(player)
            
        self.session.add(room)
        await self.session.commit()
        await self.session.refresh(room)
        
        return room
    
    async def get_player_role_info(self, telegram_id: int, room_code: str) -> Optional[Tuple[str, str, str]]:
        room = await self.get_room_by_code(room_code)
        if not room or room.status != STATUS_ACTIVE:
            return None

        stmt = select(Player).where(
            (Player.room_id == room.id) & (Player.telegram_id == telegram_id)
        )
        player = (await self.session.execute(stmt)).scalars().first()
        
        if player:
            if player.role == ROLE_SPY:
                return (ROLE_SPY, room.theme, room.theme)
            else:
                return (ROLE_PLAYER, room.location, room.theme)
        
        return None
        
    async def finish_game(self, room_code: str) -> bool:
        room = await self.get_room_by_code(room_code)
        
        if room and room.status == STATUS_ACTIVE:
            room.status = STATUS_FINISHED
            self.session.add(room)
            
            await self.session.commit()
            
            return True
        
        return False
    

async def get_game_manager() -> AsyncGenerator[GameManager, None]: # <-- ИЗМЕНЯЕМ ТАЙП-ХИНТ
    await content_loader.load_content()
    
    async with AsyncSessionLocal() as session:
        yield GameManager(session, content_loader)