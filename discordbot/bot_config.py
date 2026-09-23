import json
import logging
from typing import Dict, List, Optional, Any
from pathlib import Path
from config import CONFIG_FILE_PATH

logger = logging.getLogger("bloxfruits.config_store")

DEFAULT_WATCHLIST = ["Kitsune", "Dragon", "Leopard", "Dough", "Buddha", "Portal", "T-Rex", "Venom", "Spirit", "Mammoth"]


class BotConfigStore:
    def __init__(self, file_path: Path = CONFIG_FILE_PATH):
        self.file_path = file_path
        self.data: Dict[str, Any] = {
            "channels": {},           # guild_id -> channel_id
            "ping_roles": {},         # guild_id -> role_id
            "watchlists": {},         # guild_id -> list of fruit names
            "last_normal_reset": 0,
            "last_mirage_reset": 0,
        }
        self.load()

    def load(self) -> None:
        if self.file_path.exists():
            try:
                with open(self.file_path, "r", encoding="utf-8") as f:
                    loaded = json.load(f)
                    self.data.update(loaded)
                logger.info("Loaded bot configuration from %s", self.file_path)
            except Exception as e:
                logger.error("Error loading config from %s: %s", self.file_path, e)
        else:
            self.save()

    def save(self) -> None:
        try:
            self.file_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.file_path, "w", encoding="utf-8") as f:
                json.dump(self.data, f, indent=2)
            logger.debug("Saved bot configuration to %s", self.file_path)
        except Exception as e:
            logger.error("Error saving config to %s: %s", self.file_path, e)

    def set_channel(self, guild_id: int, channel_id: int) -> None:
        self.data["channels"][str(guild_id)] = channel_id
        self.save()

    def remove_channel(self, guild_id: int) -> bool:
        guild_key = str(guild_id)
        if guild_key in self.data["channels"]:
            del self.data["channels"][guild_key]
            self.save()
            return True
        return False

    def get_channel(self, guild_id: int) -> Optional[int]:
        return self.data["channels"].get(str(guild_id))

    def get_all_channels(self) -> List[int]:
        return list(self.data["channels"].values())

    def set_ping_role(self, guild_id: int, role_id: Optional[int]) -> None:
        guild_key = str(guild_id)
        if role_id is None:
            self.data["ping_roles"].pop(guild_key, None)
        else:
            self.data["ping_roles"][guild_key] = role_id
        self.save()

    def get_ping_role(self, guild_id: int) -> Optional[int]:
        return self.data["ping_roles"].get(str(guild_id))

    def get_watchlist(self, guild_id: Optional[int] = None) -> List[str]:
        if guild_id is not None:
            custom = self.data["watchlists"].get(str(guild_id))
            if custom is not None:
                return custom
        return DEFAULT_WATCHLIST

    def add_to_watchlist(self, guild_id: int, fruit_name: str) -> bool:
        guild_key = str(guild_id)
        current = self.data["watchlists"].get(guild_key)
        if current is None:
            current = list(DEFAULT_WATCHLIST)
        name_clean = fruit_name.strip().title()
        if name_clean not in current:
            current.append(name_clean)
            self.data["watchlists"][guild_key] = current
            self.save()
            return True
        return False

    def remove_from_watchlist(self, guild_id: int, fruit_name: str) -> bool:
        guild_key = str(guild_id)
        current = self.data["watchlists"].get(guild_key)
        if current is None:
            current = list(DEFAULT_WATCHLIST)
        name_clean = fruit_name.strip().title()
        if name_clean in current:
            current.remove(name_clean)
            self.data["watchlists"][guild_key] = current
            self.save()
            return True
        return False

    def update_last_resets(self, normal_reset: int, mirage_reset: int) -> None:
        self.data["last_normal_reset"] = normal_reset
        self.data["last_mirage_reset"] = mirage_reset
        self.save()

    @property
    def last_normal_reset(self) -> int:
        return self.data.get("last_normal_reset", 0)

    @property
    def last_mirage_reset(self) -> int:
        return self.data.get("last_mirage_reset", 0)


config_store = BotConfigStore()
