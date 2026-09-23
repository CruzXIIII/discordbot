from typing import Dict, Optional, List
from models import Fruit

# Comprehensive Blox Fruits catalog with canonical prices, rarities, types, and values
_FRUITS_RAW_DATA = [
    # Common
    {
        "name": "Rocket",
        "beli_price": 5000,
        "robux_price": 50,
        "rarity": "Common",
        "fruit_type": "Natural",
        "regular_value": 5000,
        "permanent_value": 10000000,
        "regular_demand": 1,
        "permanent_demand": 2,
        "best_used_for": "Beginner mobility",
        "image_url": "https://i.postimg.cc/cHdrRJVP/Rocket.png",
        "aliases": ["rocket"]
    },
    {
        "name": "Spin",
        "beli_price": 7500,
        "robux_price": 75,
        "rarity": "Common",
        "fruit_type": "Natural",
        "regular_value": 7500,
        "permanent_value": 15000000,
        "regular_demand": 1,
        "permanent_demand": 1,
        "best_used_for": "Flight / Gliding",
        "image_url": "https://i.postimg.cc/jj4jSbLc/Spin.png",
        "aliases": ["spin"]
    },
    {
        "name": "Blade",
        "beli_price": 30000,
        "robux_price": 100,
        "rarity": "Common",
        "fruit_type": "Natural",
        "regular_value": 50000,
        "permanent_value": 20000000,
        "regular_demand": 1,
        "permanent_demand": 2,
        "best_used_for": "PvP (Sword Immunity)",
        "image_url": "https://i.postimg.cc/bYQmYVTJ/Blade.png",
        "aliases": ["blade", "chop"]
    },
    {
        "name": "Spring",
        "beli_price": 60000,
        "robux_price": 180,
        "rarity": "Common",
        "fruit_type": "Natural",
        "regular_value": 60000,
        "permanent_value": 30000000,
        "regular_demand": 1,
        "permanent_demand": 1,
        "best_used_for": "Jumping / Mobility",
        "image_url": "https://i.postimg.cc/y8NjP1zg/Spring.png",
        "aliases": ["spring"]
    },
    {
        "name": "Bomb",
        "beli_price": 80000,
        "robux_price": 220,
        "rarity": "Common",
        "fruit_type": "Natural",
        "regular_value": 80000,
        "permanent_value": 90000000,
        "regular_demand": 1,
        "permanent_demand": 1,
        "best_used_for": "Early game grinding / AoE",
        "image_url": "https://i.postimg.cc/y8NjP1zg/Bomb.png",
        "aliases": ["bomb"]
    },
    {
        "name": "Smoke",
        "beli_price": 100000,
        "robux_price": 250,
        "rarity": "Common",
        "fruit_type": "Elemental",
        "regular_value": 100000,
        "permanent_value": 95000000,
        "regular_demand": 1,
        "permanent_demand": 2,
        "best_used_for": "First Sea Grinding (Elemental)",
        "image_url": "https://i.postimg.cc/CLxbycr9/Smoke.png",
        "aliases": ["smoke"]
    },
    {
        "name": "Spike",
        "beli_price": 180000,
        "robux_price": 380,
        "rarity": "Common",
        "fruit_type": "Natural",
        "regular_value": 180000,
        "permanent_value": 110000000,
        "regular_demand": 1,
        "permanent_demand": 1,
        "best_used_for": "Beginner AoE",
        "image_url": "https://i.postimg.cc/CLxbycr9/Spike.png",
        "aliases": ["spike"]
    },

    # Uncommon
    {
        "name": "Flame",
        "beli_price": 250000,
        "robux_price": 550,
        "rarity": "Uncommon",
        "fruit_type": "Elemental",
        "regular_value": 250000,
        "permanent_value": 250000000,
        "regular_demand": 2,
        "permanent_demand": 3,
        "best_used_for": "Grinding & Sea Events (Awakened)",
        "image_url": "https://i.postimg.cc/vB8Z125M/Flame.png",
        "aliases": ["flame", "fire"]
    },
    {
        "name": "Eagle",
        "beli_price": 300000,
        "robux_price": 650,
        "rarity": "Uncommon",
        "fruit_type": "Beast",
        "regular_value": 300000,
        "permanent_value": 220000000,
        "regular_demand": 1,
        "permanent_demand": 1,
        "best_used_for": "Flight / Agility",
        "image_url": "https://i.postimg.cc/L5vjJvP9/Eagle.png",
        "aliases": ["eagle", "falcon"]
    },
    {
        "name": "Ice",
        "beli_price": 350000,
        "robux_price": 750,
        "rarity": "Uncommon",
        "fruit_type": "Elemental",
        "regular_value": 350000,
        "permanent_value": 300000000,
        "regular_demand": 3,
        "permanent_demand": 4,
        "best_used_for": "Early PvP, Grinding, Walking on Water",
        "image_url": "https://i.postimg.cc/QxFVkwyN/Ice.png",
        "aliases": ["ice"]
    },
    {
        "name": "Sand",
        "beli_price": 420000,
        "robux_price": 850,
        "rarity": "Uncommon",
        "fruit_type": "Elemental",
        "regular_value": 420000,
        "permanent_value": 660000000,
        "regular_demand": 1,
        "permanent_demand": 2,
        "best_used_for": "Stun combos in PvP (Awakened)",
        "image_url": "https://i.postimg.cc/QxFVkwyN/Sand.png",
        "aliases": ["sand"]
    },
    {
        "name": "Dark",
        "beli_price": 500000,
        "robux_price": 950,
        "rarity": "Uncommon",
        "fruit_type": "Elemental",
        "regular_value": 500000,
        "permanent_value": 680000000,
        "regular_demand": 2,
        "permanent_demand": 3,
        "best_used_for": "Sword Main PvP Combos (Awakened)",
        "image_url": "https://i.postimg.cc/fRP8k0yL/Dark.png",
        "aliases": ["dark"]
    },
    {
        "name": "Diamond",
        "beli_price": 600000,
        "robux_price": 1000,
        "rarity": "Uncommon",
        "fruit_type": "Natural",
        "regular_value": 600000,
        "permanent_value": 450000000,
        "regular_demand": 1,
        "permanent_demand": 1,
        "best_used_for": "Defense boost (+25%)",
        "image_url": "https://i.postimg.cc/CLxbycr9/Diamond.png",
        "aliases": ["diamond"]
    },

    # Rare
    {
        "name": "Light",
        "beli_price": 650000,
        "robux_price": 1100,
        "rarity": "Rare",
        "fruit_type": "Elemental",
        "regular_value": 650000,
        "permanent_value": 750000000,
        "regular_demand": 4,
        "permanent_demand": 5,
        "best_used_for": "Best First Sea Grinding fruit & Fast Flight",
        "image_url": "https://i.postimg.cc/CLxbycr9/Light.png",
        "aliases": ["light"]
    },
    {
        "name": "Rubber",
        "beli_price": 750000,
        "robux_price": 1200,
        "rarity": "Rare",
        "fruit_type": "Natural",
        "regular_value": 750000,
        "permanent_value": 550000000,
        "regular_demand": 2,
        "permanent_demand": 2,
        "best_used_for": "Guns & Rumble immunity, Gear Transformation",
        "image_url": "https://i.postimg.cc/y8wP7d0P/Rubber.png",
        "aliases": ["rubber"]
    },
    {
        "name": "Barrier",
        "beli_price": 800000,
        "robux_price": 1250,
        "rarity": "Rare",
        "fruit_type": "Natural",
        "regular_value": 800000,
        "permanent_value": 400000000,
        "regular_demand": 1,
        "permanent_demand": 1,
        "best_used_for": "Trolling / Blocking attacks",
        "image_url": "https://i.postimg.cc/CLxbycr9/Barrier.png",
        "aliases": ["barrier"]
    },
    {
        "name": "Ghost",
        "beli_price": 940000,
        "robux_price": 1275,
        "rarity": "Rare",
        "fruit_type": "Natural",
        "regular_value": 940000,
        "permanent_value": 650000000,
        "regular_demand": 2,
        "permanent_demand": 2,
        "best_used_for": "Revival / Ghost Clones",
        "image_url": "https://i.postimg.cc/k47tXh8G/Ghost.png",
        "aliases": ["ghost", "revive"]
    },
    {
        "name": "Magma",
        "beli_price": 960000,
        "robux_price": 1300,
        "rarity": "Rare",
        "fruit_type": "Elemental",
        "regular_value": 960000,
        "permanent_value": 850000000,
        "regular_demand": 5,
        "permanent_demand": 6,
        "best_used_for": "Highest DPS in game, Sea Beast Hunting",
        "image_url": "https://i.postimg.cc/CLxbycr9/Magma.png",
        "aliases": ["magma"]
    },

    # Legendary
    {
        "name": "Quake",
        "beli_price": 1000000,
        "robux_price": 1500,
        "rarity": "Legendary",
        "fruit_type": "Natural",
        "regular_value": 1000000,
        "permanent_value": 800000000,
        "regular_demand": 2,
        "permanent_demand": 3,
        "best_used_for": "Massive AoE & Raid unlocking",
        "image_url": "https://i.postimg.cc/CLxbycr9/Quake.png",
        "aliases": ["quake"]
    },
    {
        "name": "Buddha",
        "beli_price": 1200000,
        "robux_price": 1650,
        "rarity": "Legendary",
        "fruit_type": "Beast",
        "regular_value": 10000000,
        "permanent_value": 1900000000,
        "regular_demand": 9,
        "permanent_demand": 10,
        "best_used_for": "Best Grinding & Raid fruit in entire game",
        "image_url": "https://i.postimg.cc/CLxbycr9/Buddha.png",
        "aliases": ["buddha"]
    },
    {
        "name": "Love",
        "beli_price": 1300000,
        "robux_price": 1700,
        "rarity": "Legendary",
        "fruit_type": "Natural",
        "regular_value": 1300000,
        "permanent_value": 950000000,
        "regular_demand": 2,
        "permanent_demand": 3,
        "best_used_for": "Flamingo ride, Support, PvP",
        "image_url": "https://i.postimg.cc/CLxbycr9/Love.png",
        "aliases": ["love"]
    },
    {
        "name": "Spider",
        "beli_price": 1500000,
        "robux_price": 1800,
        "rarity": "Legendary",
        "fruit_type": "Natural",
        "regular_value": 1500000,
        "permanent_value": 950000000,
        "regular_demand": 2,
        "permanent_demand": 2,
        "best_used_for": "Web mobility & Long-range snipes",
        "image_url": "https://i.postimg.cc/9F4sN5kS/Spider.png",
        "aliases": ["spider", "string"]
    },
    {
        "name": "Sound",
        "beli_price": 1700000,
        "robux_price": 1900,
        "rarity": "Legendary",
        "fruit_type": "Natural",
        "regular_value": 2500000,
        "permanent_value": 1100000000,
        "regular_demand": 4,
        "permanent_demand": 4,
        "best_used_for": "Buffs, Speed, PvP combos",
        "image_url": "https://i.postimg.cc/CLxbycr9/Sound.png",
        "aliases": ["sound"]
    },
    {
        "name": "Phoenix",
        "beli_price": 1800000,
        "robux_price": 2000,
        "rarity": "Legendary",
        "fruit_type": "Beast",
        "regular_value": 2000000,
        "permanent_value": 1200000000,
        "regular_demand": 3,
        "permanent_demand": 4,
        "best_used_for": "Healing, Flight, Sea events",
        "image_url": "https://i.postimg.cc/CLxbycr9/Phoenix.png",
        "aliases": ["phoenix"]
    },
    {
        "name": "Portal",
        "beli_price": 1900000,
        "robux_price": 2000,
        "rarity": "Legendary",
        "fruit_type": "Natural",
        "regular_value": 12000000,
        "permanent_value": 2100000000,
        "regular_demand": 9,
        "permanent_demand": 10,
        "best_used_for": "World Teleportation, Sword PvP Combos",
        "image_url": "https://i.postimg.cc/CLxbycr9/Portal.png",
        "aliases": ["portal", "door"]
    },
    {
        "name": "Rumble",
        "beli_price": 2100000,
        "robux_price": 2100,
        "rarity": "Legendary",
        "fruit_type": "Elemental",
        "regular_value": 7000000,
        "permanent_value": 1800000000,
        "regular_demand": 7,
        "permanent_demand": 8,
        "best_used_for": "Stun, Sword Main PvP (Awakened)",
        "image_url": "https://i.postimg.cc/CLxbycr9/Rumble.png",
        "aliases": ["rumble", "lightning", "thunder"]
    },
    {
        "name": "Pain",
        "beli_price": 2300000,
        "robux_price": 2200,
        "rarity": "Legendary",
        "fruit_type": "Natural",
        "regular_value": 2300000,
        "permanent_value": 1000000000,
        "regular_demand": 2,
        "permanent_demand": 2,
        "best_used_for": "Repel, Long range PvP",
        "image_url": "https://i.postimg.cc/CLxbycr9/Pain.png",
        "aliases": ["pain", "paw"]
    },
    {
        "name": "Blizzard",
        "beli_price": 2400000,
        "robux_price": 2250,
        "rarity": "Legendary",
        "fruit_type": "Elemental",
        "regular_value": 5000000,
        "permanent_value": 1500000000,
        "regular_demand": 5,
        "permanent_demand": 6,
        "best_used_for": "AoE Flight & Grinding & Sea Beast",
        "image_url": "https://i.postimg.cc/CLxbycr9/Blizzard.png",
        "aliases": ["blizzard"]
    },

    # Mythical
    {
        "name": "Gravity",
        "beli_price": 2500000,
        "robux_price": 2300,
        "rarity": "Mythical",
        "fruit_type": "Natural",
        "regular_value": 2500000,
        "permanent_value": 1300000000,
        "regular_demand": 2,
        "permanent_demand": 2,
        "best_used_for": "Meteor AoE / PvP",
        "image_url": "https://i.postimg.cc/CLxbycr9/Gravity.png",
        "aliases": ["gravity"]
    },
    {
        "name": "Mammoth",
        "beli_price": 2700000,
        "robux_price": 2350,
        "rarity": "Mythical",
        "fruit_type": "Beast",
        "regular_value": 12500000,
        "permanent_value": 2200000000,
        "regular_demand": 6,
        "permanent_demand": 7,
        "best_used_for": "Stampede / Sea Event Armor",
        "image_url": "https://i.postimg.cc/CLxbycr9/Mammoth.png",
        "aliases": ["mammoth"]
    },
    {
        "name": "T-Rex",
        "beli_price": 2700000,
        "robux_price": 2350,
        "rarity": "Mythical",
        "fruit_type": "Beast",
        "regular_value": 20000000,
        "permanent_value": 2500000000,
        "regular_demand": 8,
        "permanent_demand": 8,
        "best_used_for": "Prehistoric roar & Fast M1 PvP",
        "image_url": "https://i.postimg.cc/CLxbycr9/T-Rex.png",
        "aliases": ["t-rex", "trex", "t rex"]
    },
    {
        "name": "Dough",
        "beli_price": 2800000,
        "robux_price": 2400,
        "rarity": "Mythical",
        "fruit_type": "Elemental",
        "regular_value": 25000000,
        "permanent_value": 3100000000,
        "regular_demand": 9,
        "permanent_demand": 10,
        "best_used_for": "Top Tier PvP One-Shot Combos (Awakened)",
        "image_url": "https://i.postimg.cc/CLxbycr9/Dough.png",
        "aliases": ["dough"]
    },
    {
        "name": "Shadow",
        "beli_price": 2900000,
        "robux_price": 2425,
        "rarity": "Mythical",
        "fruit_type": "Natural",
        "regular_value": 6000000,
        "permanent_value": 1600000000,
        "regular_demand": 4,
        "permanent_demand": 4,
        "best_used_for": "Life leech & Umbra meter PvP",
        "image_url": "https://i.postimg.cc/CLxbycr9/Shadow.png",
        "aliases": ["shadow"]
    },
    {
        "name": "Venom",
        "beli_price": 3000000,
        "robux_price": 2450,
        "rarity": "Mythical",
        "fruit_type": "Natural",
        "regular_value": 9000000,
        "permanent_value": 2200000000,
        "regular_demand": 6,
        "permanent_demand": 7,
        "best_used_for": "Poison DoT & Easy PvP Transformation",
        "image_url": "https://i.postimg.cc/CLxbycr9/Venom.png",
        "aliases": ["venom"]
    },
    {
        "name": "Control",
        "beli_price": 3200000,
        "robux_price": 2500,
        "rarity": "Mythical",
        "fruit_type": "Natural",
        "regular_value": 8000000,
        "permanent_value": 2100000000,
        "regular_demand": 5,
        "permanent_demand": 5,
        "best_used_for": "Levitating buildings / Area control",
        "image_url": "https://i.postimg.cc/CLxbycr9/Control.png",
        "aliases": ["control", "room"]
    },
    {
        "name": "Gas",
        "beli_price": 3200000,
        "robux_price": 2500,
        "rarity": "Mythical",
        "fruit_type": "Elemental",
        "regular_value": 35000000,
        "permanent_value": 3300000000,
        "regular_demand": 9,
        "permanent_demand": 9,
        "best_used_for": "Suffocation AoE & Flight & PvP",
        "image_url": "https://i.postimg.cc/CLxbycr9/Gas.png",
        "aliases": ["gas"]
    },
    {
        "name": "Spirit",
        "beli_price": 3400000,
        "robux_price": 2550,
        "rarity": "Mythical",
        "fruit_type": "Natural",
        "regular_value": 10000000,
        "permanent_value": 2300000000,
        "regular_demand": 6,
        "permanent_demand": 6,
        "best_used_for": "Fire & Ice Spirits, Speed & Healing",
        "image_url": "https://i.postimg.cc/CLxbycr9/Spirit.png",
        "aliases": ["spirit", "soul"]
    },
    {
        "name": "Leopard",
        "beli_price": 5000000,
        "robux_price": 3000,
        "rarity": "Mythical",
        "fruit_type": "Beast",
        "regular_value": 40000000,
        "permanent_value": 4200000000,
        "regular_demand": 9,
        "permanent_demand": 9,
        "best_used_for": "Insane speed, M1 spam & PvP Meta",
        "image_url": "https://i.postimg.cc/CLxbycr9/Leopard.png",
        "aliases": ["leopard", "leo"]
    },
    {
        "name": "Tiger",
        "beli_price": 5000000,
        "robux_price": 3000,
        "rarity": "Mythical",
        "fruit_type": "Beast",
        "regular_value": 45000000,
        "permanent_value": 4400000000,
        "regular_demand": 9,
        "permanent_demand": 9,
        "best_used_for": "High-mobility predator attacks & PvP",
        "image_url": "https://i.postimg.cc/pT3Y3J8s/Tiger.png",
        "aliases": ["tiger"]
    },
    {
        "name": "Yeti",
        "beli_price": 5000000,
        "robux_price": 3000,
        "rarity": "Mythical",
        "fruit_type": "Beast",
        "regular_value": 55000000,
        "permanent_value": 4600000000,
        "regular_demand": 9,
        "permanent_demand": 10,
        "best_used_for": "Blizzard fury & Freeze attacks & PvP",
        "image_url": "https://i.postimg.cc/CLxbycr9/Yeti.png",
        "aliases": ["yeti"]
    },
    {
        "name": "Kitsune",
        "beli_price": 8000000,
        "robux_price": 4000,
        "rarity": "Mythical",
        "fruit_type": "Beast",
        "regular_value": 600000000,
        "permanent_value": 5490000000,
        "regular_demand": 10,
        "permanent_demand": 10,
        "best_used_for": "Extreme Mobility, Water Running, Top Tier PvP",
        "image_url": "https://i.postimg.cc/CLxbycr9/Kitsune.png",
        "aliases": ["kitsune", "kit"]
    },
    {
        "name": "Dragon",
        "beli_price": 10000000,
        "robux_price": 5000,
        "rarity": "Mythical",
        "fruit_type": "Beast",
        "regular_value": 850000000,
        "permanent_value": 6000000000,
        "regular_demand": 10,
        "permanent_demand": 10,
        "best_used_for": "Highest AoE, Dragon Flight, Rework God-Tier",
        "image_url": "https://i.postimg.cc/CLxbycr9/Dragon.png",
        "aliases": ["dragon", "east-dragon", "west-dragon", "east dragon", "west dragon"]
    },
]

# Build lookup dictionaries
_CATALOG_BY_NAME: Dict[str, Fruit] = {}
_CATALOG_BY_ALIAS: Dict[str, Fruit] = {}
ALL_FRUIT_NAMES: List[str] = []

for item in _FRUITS_RAW_DATA:
    f = Fruit(
        name=item["name"],
        beli_price=item["beli_price"],
        robux_price=item["robux_price"],
        fruit_type=item["fruit_type"],
        image_url=item["image_url"],
        rarity=item["rarity"],
        regular_value=item["regular_value"],
        permanent_value=item["permanent_value"],
        regular_demand=item["regular_demand"],
        permanent_demand=item["permanent_demand"],
        best_used_for=item.get("best_used_for"),
        regular_trend="Stable",
        permanent_trend="Stable",
    )
    _CATALOG_BY_NAME[f.name.lower()] = f
    ALL_FRUIT_NAMES.append(f.name)
    for alias in item.get("aliases", []):
        _CATALOG_BY_ALIAS[alias.lower()] = f


def get_fruit_by_name(query: str) -> Optional[Fruit]:
    """Finds a fruit by exact name, alias, or substring in the catalog."""
    if not query:
        return None
    q = query.strip().lower()

    # Exact alias/name match
    if q in _CATALOG_BY_ALIAS:
        return _CATALOG_BY_ALIAS[q]
    if q in _CATALOG_BY_NAME:
        return _CATALOG_BY_NAME[q]

    # Partial / substring match
    for key, f in _CATALOG_BY_NAME.items():
        if q in key or key in q:
            return f

    return None


def get_all_catalog_fruits() -> List[Fruit]:
    """Returns list of all canonical fruits in the catalog."""
    return list(_CATALOG_BY_NAME.values())
