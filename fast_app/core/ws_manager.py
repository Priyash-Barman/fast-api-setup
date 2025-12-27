from typing import Dict, Set, DefaultDict
from collections import defaultdict
from fastapi import WebSocket
import asyncio


class WSManager:
    def __init__(self):
        # user_id -> set of websockets
        self.connections: DefaultDict[str, Set[WebSocket]] = defaultdict(set)

        # room_id -> set of user_ids
        self.rooms: DefaultDict[str, Set[str]] = defaultdict(set)

        self._lock = asyncio.Lock()

    # ----------------------------------
    # CONNECTION
    # ----------------------------------

    async def connect(self, user_id: str, websocket: WebSocket):
        await websocket.accept()
        async with self._lock:
            self.connections[user_id].add(websocket)

    async def disconnect(self, user_id: str, websocket: WebSocket):
        async with self._lock:
            self.connections[user_id].discard(websocket)
            if not self.connections[user_id]:
                del self.connections[user_id]

            for users in self.rooms.values():
                users.discard(user_id)

    # ----------------------------------
    # ROOMS
    # ----------------------------------

    async def join_room(self, room_id: str, user_id: str):
        async with self._lock:
            self.rooms[room_id].add(user_id)

    async def leave_room(self, room_id: str, user_id: str):
        async with self._lock:
            self.rooms[room_id].discard(user_id)
            if not self.rooms[room_id]:
                del self.rooms[room_id]

    # ----------------------------------
    # EMIT
    # ----------------------------------

    async def emit_user(self, user_id: str, payload: dict):
        for ws in list(self.connections.get(user_id, [])):
            await ws.send_json(payload)

    async def emit_room(self, room_id: str, payload: dict):
        for user_id in self.rooms.get(room_id, set()):
            await self.emit_user(user_id, payload)

    # ----------------------------------
    # CLEANUP
    # ----------------------------------

    def close_all(self):
        self.connections.clear()
        self.rooms.clear()
