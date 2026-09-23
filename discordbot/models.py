import time
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from config import RARITY_COLORS, RARITY_EMOJIS


def format_short_number(num: Any) -> str:
    """Formats large numbers into human-readable compact strings like 120M or 500K."""
    if num is None:
        return "N/A"
    try:
        val = float(num)
    except (ValueError, TypeError):
        return "N/A"
    abs_num = abs(val)
    if abs_num >= 1_000_000_000:
        return f"{val / 1_000_000_000:.1f}".rstrip('0').rstrip('.') + "B"
    if abs_num >= 1_000_000:
        return f"{val / 1_000_000:.1f}".rstrip('0').rstrip('.') + "M"
    if abs_num >= 1_000:
        return f"{val / 1_000:.1f}".rstrip('0').rstrip('.') + "K"
    if val.is_integer():
        return str(int(val))
    return str(val)


@dataclass
class Fruit:
    name: str
    beli_price: int = 0
    robux_price: int = 0
    fruit_type: str = "Unknown"
    image_url: Optional[str] = None
    item_id: Optional[str] = None
    rarity: str = "Common"
    regular_value: int = 0
    permanent_value: int = 0
    regular_demand: int = 0
    permanent_demand: int = 0
    regular_trend: str = "Stable"
    permanent_trend: str = "Stable"
    best_used_for: Optional[str] = None
    value_path: Optional[str] = None

    @property
    def formatted_beli(self) -> str:
        return f"{self.beli_price:,} Beli" if self.beli_price else "N/A"

    @property
    def formatted_robux(self) -> str:
        return f"{self.robux_price:,} R$" if self.robux_price else "N/A"

    @property
    def formatted_value(self) -> str:
        return format_short_number(self.regular_value)

    @property
    def rarity_color(self) -> int:
        return RARITY_COLORS.get(self.rarity, RARITY_COLORS["Default"])

    @property
    def rarity_emoji(self) -> str:
        return RARITY_EMOJIS.get(self.rarity, "⚪")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "beli_price": self.beli_price,
            "robux_price": self.robux_price,
            "fruit_type": self.fruit_type,
            "image_url": self.image_url,
            "item_id": self.item_id,
            "rarity": self.rarity,
            "regular_value": self.regular_value,
            "permanent_value": self.permanent_value,
            "regular_demand": self.regular_demand,
            "permanent_demand": self.permanent_demand,
            "regular_trend": self.regular_trend,
            "permanent_trend": self.permanent_trend,
            "best_used_for": self.best_used_for,
            "value_path": self.value_path,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Fruit":
        # Supports both camelCase (from API) and snake_case (internal)
        return cls(
            name=data.get("name", "Unknown Fruit"),
            beli_price=data.get("beliPrice", data.get("beli_price", 0)),
            robux_price=data.get("robuxPrice", data.get("robux_price", 0)),
            fruit_type=data.get("fruitType", data.get("fruit_type", "Unknown")),
            image_url=data.get("image", data.get("image_url")),
            item_id=str(data.get("itemId", data.get("item_id", ""))) or None,
            rarity=data.get("rarity", "Common"),
            regular_value=data.get("regularValue", data.get("regular_value", 0)),
            permanent_value=data.get("permanentValue", data.get("permanent_value", 0)),
            regular_demand=data.get("regularDemand", data.get("regular_demand", 0)),
            permanent_demand=data.get("permanentDemand", data.get("permanent_demand", 0)),
            regular_trend=data.get("regularTrend", data.get("regular_trend", "Stable")),
            permanent_trend=data.get("permanentTrend", data.get("permanent_trend", "Stable")),
            best_used_for=data.get("bestUsedFor", data.get("best_used_for")),
            value_path=data.get("valuePath", data.get("value_path")),
        )


@dataclass
class StockWindow:
    kind: str
    started_at: int
    resets_at: int
    period_ms: int

    @property
    def resets_at_seconds(self) -> int:
        return max(0, self.resets_at // 1000)

    @property
    def started_at_seconds(self) -> int:
        return max(0, self.started_at // 1000)

    @property
    def countdown_seconds(self) -> int:
        if self.resets_at <= 0:
            return 0
        now_ms = int(time.time() * 1000)
        diff_s = (self.resets_at - now_ms) // 1000
        return max(0, diff_s)

    @property
    def countdown_formatted(self) -> str:
        if self.resets_at <= 0:
            return "Pending"
        secs = self.countdown_seconds
        if secs == 0:
            return "Restocking..."
        hours = secs // 3600
        minutes = (secs % 3600) // 60
        seconds = secs % 60
        if hours > 0:
            return f"{hours}h {minutes}m {seconds}s"
        return f"{minutes}m {seconds}s"

    @property
    def discord_relative_timestamp(self) -> str:
        if self.resets_at <= 0:
            return "*Pending restock*"
        return f"<t:{self.resets_at_seconds}:R>"

    @property
    def discord_time_timestamp(self) -> str:
        if self.resets_at <= 0:
            return "*Pending*"
        return f"<t:{self.resets_at_seconds}:T>"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "kind": self.kind,
            "started_at": self.started_at,
            "resets_at": self.resets_at,
            "period_ms": self.period_ms,
            "countdown_seconds": self.countdown_seconds,
            "countdown_formatted": self.countdown_formatted,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "StockWindow":
        return cls(
            kind=data.get("kind", "normal"),
            started_at=data.get("startedAt", data.get("started_at", 0)),
            resets_at=data.get("resetsAt", data.get("resets_at", 0)),
            period_ms=data.get("periodMs", data.get("period_ms", 14400000)),
        )


@dataclass
class StockSnapshot:
    timestamp: int = field(default_factory=lambda: int(time.time() * 1000))
    normal_window: StockWindow = field(default_factory=lambda: StockWindow("normal", 0, 0, 14400000))
    normal_fruits: List[Fruit] = field(default_factory=list)
    normal_stale: bool = False
    normal_pending: bool = False
    mirage_window: StockWindow = field(default_factory=lambda: StockWindow("mirage", 0, 0, 7200000))
    mirage_fruits: List[Fruit] = field(default_factory=list)
    mirage_stale: bool = False
    mirage_pending: bool = False

    def find_fruit(self, name: str) -> Optional[Fruit]:
        query = name.strip().lower()
        for f in self.normal_fruits + self.mirage_fruits:
            if f.name.lower() == query:
                return f
        # partial match fallback
        for f in self.normal_fruits + self.mirage_fruits:
            if query in f.name.lower():
                return f
        return None

    def get_highest_rarity(self, stock_type: str = "all") -> str:
        rarity_ranks = {
            "Common": 1,
            "Uncommon": 2,
            "Rare": 3,
            "Legendary": 4,
            "Mythical": 5,
        }
        fruits = []
        if stock_type in ("all", "normal", "regular"):
            fruits.extend(self.normal_fruits)
        if stock_type in ("all", "mirage"):
            fruits.extend(self.mirage_fruits)

        highest = "Common"
        highest_rank = 1
        for f in fruits:
            rank = rarity_ranks.get(f.rarity, 0)
            if rank > highest_rank:
                highest_rank = rank
                highest = f.rarity
        return highest

    def to_dict(self) -> Dict[str, Any]:
        return {
            "timestamp": self.timestamp,
            "normal": {
                "window": self.normal_window.to_dict(),
                "fruits": [f.to_dict() for f in self.normal_fruits],
                "stale": self.normal_stale,
                "pending": self.normal_pending,
            },
            "mirage": {
                "window": self.mirage_window.to_dict(),
                "fruits": [f.to_dict() for f in self.mirage_fruits],
                "stale": self.mirage_stale,
                "pending": self.mirage_pending,
            },
        }

    @classmethod
    def from_raw_snapshot(cls, data: Dict[str, Any]) -> "StockSnapshot":
        normal_data = data.get("normal", {})
        mirage_data = data.get("mirage", {})

        normal_window = StockWindow.from_dict(normal_data.get("window", {}))
        mirage_window = StockWindow.from_dict(mirage_data.get("window", {}))

        normal_fruits = [Fruit.from_dict(f) for f in normal_data.get("fruits", [])]
        mirage_fruits = [Fruit.from_dict(f) for f in mirage_data.get("fruits", [])]

        return cls(
            timestamp=data.get("timestamp", int(time.time() * 1000)),
            normal_window=normal_window,
            normal_fruits=normal_fruits,
            normal_stale=bool(normal_data.get("stale", False)),
            normal_pending=bool(normal_data.get("pending", False)),
            mirage_window=mirage_window,
            mirage_fruits=mirage_fruits,
            mirage_stale=bool(mirage_data.get("stale", False)),
            mirage_pending=bool(mirage_data.get("pending", False)),
        )
