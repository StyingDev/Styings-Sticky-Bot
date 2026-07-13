import os
import json
import logging
import datetime
import aiosqlite

DEFAULT_THRESHOLD = 20


class Database:
    """SQLite-backed storage for sticky messages, with an in-memory read cache."""

    def __init__(self, db_file=None, legacy_json_file=None):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        self.db_file = db_file or os.path.join(base_dir, 'sticky.db')
        self.legacy_json_file = legacy_json_file or os.path.join(base_dir, 'sticky_config.json')
        self.cache = {}
        self._conn = None

    async def connect(self):
        db_existed = os.path.exists(self.db_file)
        self._conn = await aiosqlite.connect(self.db_file)
        self._conn.row_factory = aiosqlite.Row
        await self._init_schema()
        if not db_existed and os.path.exists(self.legacy_json_file):
            await self._migrate_json()
        await self._load_all()

    async def close(self):
        if self._conn:
            await self._conn.close()
            self._conn = None

    async def _init_schema(self):
        await self._conn.execute('''
            CREATE TABLE IF NOT EXISTS sticky_messages (
                guild_id INTEGER NOT NULL,
                channel_id INTEGER PRIMARY KEY,
                message TEXT NOT NULL,
                message_id INTEGER,
                is_embed INTEGER NOT NULL DEFAULT 0,
                active INTEGER NOT NULL DEFAULT 1,
                threshold INTEGER NOT NULL DEFAULT 20,
                embed_color TEXT,
                embed_title TEXT,
                embed_image TEXT,
                created_by INTEGER,
                created_at TEXT,
                updated_by INTEGER,
                updated_at TEXT
            )
        ''')
        await self._conn.commit()

    async def _load_all(self):
        self.cache = {}
        async with self._conn.execute('SELECT * FROM sticky_messages') as cursor:
            rows = await cursor.fetchall()
        for row in rows:
            info = dict(row)
            info['weight'] = 0
            self.cache[info['channel_id']] = info

    async def _migrate_json(self):
        """One-time import of the old JSON config into sqlite, if present."""
        try:
            with open(self.legacy_json_file, 'r') as f:
                legacy = json.load(f)
        except (OSError, json.JSONDecodeError) as e:
            logging.error(f"Could not read legacy sticky_config.json for migration: {e}")
            return

        now = datetime.datetime.now(datetime.timezone.utc).isoformat()
        migrated = 0
        for guild_id, channels in legacy.get('sticky_messages', {}).items():
            if not isinstance(channels, dict) or not guild_id.isdigit():
                continue
            for channel_id, info in channels.items():
                if not channel_id.isdigit() or not isinstance(info, dict):
                    continue
                await self.upsert_sticky(
                    int(channel_id), int(guild_id),
                    message=info.get('message', ''),
                    message_id=info.get('message_id'),
                    is_embed=1 if info.get('embed') else 0,
                    active=1 if info.get('active') else 0,
                    threshold=DEFAULT_THRESHOLD,
                    created_at=now, updated_at=now,
                )
                migrated += 1
        if migrated:
            logging.warning(f"Migrated {migrated} sticky message(s) from sticky_config.json into sticky.db.")

    async def upsert_sticky(self, channel_id, guild_id, **fields):
        row = self.cache.get(channel_id)
        if row is None:
            row = {
                'guild_id': guild_id, 'channel_id': channel_id, 'message': '', 'message_id': None,
                'is_embed': 0, 'active': 1, 'threshold': DEFAULT_THRESHOLD,
                'embed_color': None, 'embed_title': None, 'embed_image': None,
                'created_by': None, 'created_at': None, 'updated_by': None, 'updated_at': None,
                'weight': 0,
            }
        row = {**row, **fields, 'guild_id': guild_id, 'channel_id': channel_id}
        weight = row.pop('weight', 0)
        self.cache[channel_id] = {**row, 'weight': weight}

        await self._conn.execute('''
            INSERT INTO sticky_messages (guild_id, channel_id, message, message_id, is_embed, active, threshold,
                                          embed_color, embed_title, embed_image, created_by, created_at, updated_by, updated_at)
            VALUES (:guild_id, :channel_id, :message, :message_id, :is_embed, :active, :threshold,
                    :embed_color, :embed_title, :embed_image, :created_by, :created_at, :updated_by, :updated_at)
            ON CONFLICT(channel_id) DO UPDATE SET
                message=excluded.message, message_id=excluded.message_id, is_embed=excluded.is_embed,
                active=excluded.active, threshold=excluded.threshold,
                embed_color=excluded.embed_color, embed_title=excluded.embed_title, embed_image=excluded.embed_image,
                created_by=excluded.created_by, created_at=excluded.created_at,
                updated_by=excluded.updated_by, updated_at=excluded.updated_at
        ''', row)
        await self._conn.commit()

    async def set_message_id(self, channel_id, message_id):
        if channel_id in self.cache:
            self.cache[channel_id]['message_id'] = message_id
        await self._conn.execute('UPDATE sticky_messages SET message_id = ? WHERE channel_id = ?', (message_id, channel_id))
        await self._conn.commit()

    async def delete_sticky(self, channel_id):
        self.cache.pop(channel_id, None)
        await self._conn.execute('DELETE FROM sticky_messages WHERE channel_id = ?', (channel_id,))
        await self._conn.commit()

    def get(self, channel_id):
        return self.cache.get(channel_id)

    def for_guild(self, guild_id):
        return [info for info in self.cache.values() if info['guild_id'] == guild_id]
