import random
import string
from typing import Optional, List, Tuple

from sqlalchemy import select
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
    def __init__(self, sessionmaker: AsyncSessionLocal, content_loader: ContentLoader):
        self.sessionmaker = sessionmaker
        self.content_loader = content_loader
        
    def _generate_unique_code(self, length: int = 4) -> str:
        characters = string.ascii_uppercase + string.digits
        return ''.join(random.choice(characters) for _ in range(length))
    
    async def create_new_room(self, creator_id: int, theme: str) -> GameRoom:
        async with self.sessionmaker() as session:
            code = self._generate_unique_code()

            while await self._get_room_by_code(session, code) is not None:
                code = self._generate_unique_code()

            new_room = GameRoom(
                room_code=code,
                creator_id=creator_id,
                status=STATUS_WAITING,
                theme=theme
            )

            session.add(new_room)
            await session.commit()
            await session.refresh(new_room)

            await self._add_player_to_room(session, new_room.room_code, creator_id, username=None)

            return new_room
    
    async def get_room_by_code(self, code: str) -> Optional[GameRoom]:
        async with self.sessionmaker() as session:
            return await self._get_room_by_code(session, code)
    
    async def add_player_to_room(self, code: str, telegram_id: int, username: Optional[str]) -> bool:
        async with self.sessionmaker() as session:
            return await self._add_player_to_room(session, code, telegram_id, username)
    
    async def get_room_players(self, code: str) -> List[Player]:
        async with self.sessionmaker() as session:
            code = code.upper()
            stmt = (
                select(GameRoom)
                .where(GameRoom.room_code == code)
                .options(selectinload(GameRoom.players))
            )
            result = await session.execute(stmt)
            room = result.scalars().first()

            if room:
                players = sorted(room.players, key=lambda p: p.telegram_id != room.creator_id)
                return players
            return []
    
    async def distribute_roles(self, room_code: str, min_players: int = 3) -> Optional[GameRoom]:
        async with self.sessionmaker() as session:
            room = await self._get_room_by_code(session, room_code)
            if not room or room.status != STATUS_WAITING:
                return None

            stmt = (
                select(GameRoom)
                .where(GameRoom.room_code == room_code.upper())
                .options(selectinload(GameRoom.players))
            )
            result = await session.execute(stmt)
            room = result.scalars().first()
            if not room:
                return None

            players = list(room.players)
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

                session.add(player)

            session.add(room)
            await session.commit()
            await session.refresh(room)

            return room
    
    async def get_player_role_info(self, telegram_id: int, room_code: str) -> Optional[Tuple[str, str, str]]:
        async with self.sessionmaker() as session:
            room = await self._get_room_by_code(session, room_code)
            if not room or room.status != STATUS_ACTIVE:
                return None

            stmt = select(Player).where(
                (Player.room_id == room.id) & (Player.telegram_id == telegram_id)
            )
            player = (await session.execute(stmt)).scalars().first()

            if player:
                if player.role == ROLE_SPY:
                    return (ROLE_SPY, room.theme, room.theme)
                else:
                    return (ROLE_PLAYER, room.location, room.theme)

            return None
        
    async def finish_game(self, room_code: str) -> bool:
        async with self.sessionmaker() as session:
            room = await self._get_room_by_code(session, room_code)

            if room and room.status == STATUS_ACTIVE:
                room.status = STATUS_FINISHED
                session.add(room)

                await session.commit()

                return True

            return False

    async def get_active_room_by_creator(self, creator_id: int) -> Optional[GameRoom]:
        async with self.sessionmaker() as session:
            stmt = (
                select(GameRoom)
                .where((GameRoom.creator_id == creator_id) & (GameRoom.status == STATUS_ACTIVE))
                .order_by(GameRoom.created_at.desc())
            )
            result = await session.execute(stmt)
            return result.scalars().first()

    async def restart_game(self, room_code: str, min_players: int = 3) -> bool:
        async with self.sessionmaker() as session:
            stmt = (
                select(GameRoom)
                .where(GameRoom.room_code == room_code.upper())
                .options(selectinload(GameRoom.players))
            )
            result = await session.execute(stmt)
            room = result.scalars().first()

            if not room or room.status != STATUS_ACTIVE:
                return False

            players = list(room.players)
            if len(players) < min_players:
                return False

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

                session.add(player)

            session.add(room)
            await session.commit()

            return True

    async def _get_room_by_code(self, session: AsyncSessionLocal, code: str) -> Optional[GameRoom]:
        code = code.upper()
        stmt = select(GameRoom).where(GameRoom.room_code == code)
        result = await session.execute(stmt)
        return result.scalars().first()

    async def _add_player_to_room(
        self,
        session: AsyncSessionLocal,
        code: str,
        telegram_id: int,
        username: Optional[str]
    ) -> bool:
        room = await self._get_room_by_code(session, code)

        if not room or room.status != STATUS_WAITING:
            return False

        stmt_check = select(Player).where(
            (Player.room_id == room.id) & (Player.telegram_id == telegram_id)
        )
        if (await session.execute(stmt_check)).scalars().first():
            return True

        new_player = Player(
            telegram_id=telegram_id,
            username=username,
            room_id=room.id,
            role=ROLE_PLAYER
        )

        session.add(new_player)
        await session.commit()

        return True
    

async def create_game_manager() -> GameManager:
    await content_loader.load_content()
    
    return GameManager(AsyncSessionLocal, content_loader)