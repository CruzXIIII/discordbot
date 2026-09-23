import discord
from typing import List, Optional
from datetime import datetime, timezone
from models import Fruit, StockSnapshot, StockWindow
from config import RARITY_COLORS, RARITY_EMOJIS

DEFAULT_THUMBNAIL = "https://i.postimg.cc/cHdrRJVP/Rocket.png"


def get_rarity_color(rarity: str) -> int:
    return RARITY_COLORS.get(rarity, RARITY_COLORS["Default"])


def format_fruit_line(fruit: Fruit) -> str:
    """Formats a single fruit into a concise, readable line for Discord embeds."""
    emoji = fruit.rarity_emoji
    name = f"**{fruit.name}**"
    beli = fruit.formatted_beli
    robux = fruit.formatted_robux
    val = fruit.formatted_value
    demand = f"{fruit.regular_demand}/10" if fruit.regular_demand else "N/A"
    return f"{emoji} {name} • {beli} | {robux} | Val: `{val}` | Dem: `{demand}`"


def build_stock_embed(snapshot: StockSnapshot, view_type: str = "all") -> discord.Embed:
    """Builds the main stock embed for all, regular, or mirage stocks."""
    now_utc = datetime.now(timezone.utc)
    highest_rarity = snapshot.get_highest_rarity(view_type)
    embed_color = get_rarity_color(highest_rarity)

    if view_type == "regular":
        title = "🏪 Blox Fruits — Regular Dealer Stock"
        desc = (
            f"**Next Rotation:** {snapshot.normal_window.discord_relative_timestamp} "
            f"({snapshot.normal_window.discord_time_timestamp})\n"
            f"**Cycle:** Every 4 Hours • **Items in Stock:** {len(snapshot.normal_fruits)}"
        )
    elif view_type == "mirage":
        title = "🌊 Blox Fruits — Mirage Island Dealer Stock"
        desc = (
            f"**Next Rotation:** {snapshot.mirage_window.discord_relative_timestamp} "
            f"({snapshot.mirage_window.discord_time_timestamp})\n"
            f"**Cycle:** Every 2 Hours • **Items in Stock:** {len(snapshot.mirage_fruits)}"
        )
    else:
        title = "🍈 Blox Fruits — Live Dealer Stock"
        desc = (
            f"🏪 **Regular Restock:** {snapshot.normal_window.discord_relative_timestamp} "
            f"({snapshot.normal_window.discord_time_timestamp})\n"
            f"🌊 **Mirage Restock:** {snapshot.mirage_window.discord_relative_timestamp} "
            f"({snapshot.mirage_window.discord_time_timestamp})"
        )

    embed = discord.Embed(
        title=title,
        description=desc,
        color=embed_color,
        timestamp=now_utc,
    )

    # Set thumbnail to the rarest fruit currently in stock if image exists
    top_fruit: Optional[Fruit] = None
    all_fruits = []
    if view_type in ("all", "regular"):
        all_fruits.extend(snapshot.normal_fruits)
    if view_type in ("all", "mirage"):
        all_fruits.extend(snapshot.mirage_fruits)

    for f in all_fruits:
        if f.rarity == highest_rarity and f.image_url:
            top_fruit = f
            break
    if top_fruit and top_fruit.image_url:
        embed.set_thumbnail(url=top_fruit.image_url)

    # Add Normal Stock Field
    if view_type in ("all", "regular"):
        if snapshot.normal_fruits:
            lines = [format_fruit_line(f) for f in snapshot.normal_fruits]
            content = "\n".join(lines)
            if len(content) > 1024:
                content = content[:1020] + "..."
        else:
            content = "*No stock data available or dealer is currently resting.*"

        embed.add_field(
            name=f"🏪 Regular Dealer ({len(snapshot.normal_fruits)} Fruits)",
            value=content,
            inline=False,
        )

    # Add Mirage Stock Field
    if view_type in ("all", "mirage"):
        if snapshot.mirage_fruits:
            lines = [format_fruit_line(f) for f in snapshot.mirage_fruits]
            content = "\n".join(lines)
            if len(content) > 1024:
                content = content[:1020] + "..."
        else:
            content = "*No stock data available or mirage island has not spawned.*"

        embed.add_field(
            name=f"🌊 Mirage Island Dealer ({len(snapshot.mirage_fruits)} Fruits)",
            value=content,
            inline=False,
        )

    embed.set_footer(
        text="Blox Fruits Stock Tracker • Click buttons below to filter or refresh",
    )
    return embed


def build_fruit_detail_embed(fruit: Fruit, is_in_normal: bool, is_in_mirage: bool) -> discord.Embed:
    """Builds a detailed informational card for a single fruit."""
    color = fruit.rarity_color
    embed = discord.Embed(
        title=f"{fruit.rarity_emoji} {fruit.name} Fruit",
        color=color,
        timestamp=datetime.now(timezone.utc),
    )

    if fruit.image_url:
        embed.set_thumbnail(url=fruit.image_url)

    # Stock status
    status_parts = []
    if is_in_normal:
        status_parts.append("✅ Regular Dealer")
    if is_in_mirage:
        status_parts.append("🌊 Mirage Dealer")
    stock_status = " & ".join(status_parts) if status_parts else "❌ Not in stock right now"

    embed.add_field(name="Current Stock", value=stock_status, inline=True)
    embed.add_field(name="Rarity", value=fruit.rarity, inline=True)
    embed.add_field(name="Fruit Type", value=fruit.fruit_type, inline=True)

    embed.add_field(name="Beli Price", value=fruit.formatted_beli, inline=True)
    embed.add_field(name="Robux Price", value=fruit.formatted_robux, inline=True)
    embed.add_field(name="Demand", value=f"{fruit.regular_demand}/10", inline=True)

    embed.add_field(name="Physical Value", value=fruit.formatted_value, inline=True)
    embed.add_field(
        name="Perm Value",
        value=f"{fruit.permanent_value:,}" if fruit.permanent_value else "N/A",
        inline=True
    )
    embed.add_field(name="Price Trend", value=fruit.regular_trend, inline=True)

    if fruit.best_used_for:
        embed.add_field(name="Best Used For", value=fruit.best_used_for, inline=False)

    embed.set_footer(text="Blox Fruits Values & Stock Tracker")
    return embed


def build_countdown_embed(snapshot: StockSnapshot) -> discord.Embed:
    """Builds a visual countdown embed for both dealers."""
    now_utc = datetime.now(timezone.utc)
    embed = discord.Embed(
        title="⏱️ Blox Fruits — Restock Countdowns",
        description="Countdown timers to the next global Blox Fruits dealer resets.",
        color=0x5865F2,
        timestamp=now_utc,
    )

    norm_cd = snapshot.normal_window.countdown_formatted
    norm_rel = snapshot.normal_window.discord_relative_timestamp
    norm_time = snapshot.normal_window.discord_time_timestamp

    mir_cd = snapshot.mirage_window.countdown_formatted
    mir_rel = snapshot.mirage_window.discord_relative_timestamp
    mir_time = snapshot.mirage_window.discord_time_timestamp

    embed.add_field(
        name="🏪 Regular Blox Fruit Dealer",
        value=(
            f"**Time Remaining:** `{norm_cd}`\n"
            f"**Reset Time:** {norm_rel} ({norm_time})\n"
            f"**Rotation Interval:** 4 Hours"
        ),
        inline=False,
    )

    embed.add_field(
        name="🌊 Mirage Island Dealer",
        value=(
            f"**Time Remaining:** `{mir_cd}`\n"
            f"**Reset Time:** {mir_rel} ({mir_time})\n"
            f"**Rotation Interval:** 2 Hours"
        ),
        inline=False,
    )

    embed.set_footer(text="Blox Fruits Stock Tracker • Stock is synchronized across all Roblox servers")
    return embed


def build_announcement_embed(snapshot: StockSnapshot, watched_hits: List[str], dealer_type: str = "both") -> discord.Embed:
    """Builds an announcement embed when a stock rotation occurs."""
    now_utc = datetime.now(timezone.utc)
    highest_rarity = snapshot.get_highest_rarity()
    color = get_rarity_color(highest_rarity)

    if dealer_type == "normal":
        dealer_name = "🏪 Regular Dealer"
        reset_time = snapshot.normal_window.discord_relative_timestamp
    elif dealer_type == "mirage":
        dealer_name = "🌊 Mirage Dealer"
        reset_time = snapshot.mirage_window.discord_relative_timestamp
    else:
        dealer_name = "🏪 Regular & 🌊 Mirage Dealers"
        reset_time = snapshot.normal_window.discord_relative_timestamp

    title = f"📢 Stock Rotated — {dealer_name}!"
    desc = f"The Blox Fruits dealer inventory has just refreshed!\n**Next Reset:** {reset_time}"

    if watched_hits:
        alert_str = ", ".join(f"**{name}**" for name in watched_hits)
        desc = f"🚨 **WATCHLIST ALERT!** 🚨\nHigh demand fruit(s) in stock: {alert_str}\n\n" + desc

    embed = discord.Embed(
        title=title,
        description=desc,
        color=color,
        timestamp=now_utc,
    )

    if dealer_type in ("both", "normal") and snapshot.normal_fruits:
        lines = [format_fruit_line(f) for f in snapshot.normal_fruits]
        embed.add_field(
            name=f"🏪 Regular Stock ({len(snapshot.normal_fruits)} Fruits)",
            value="\n".join(lines)[:1024],
            inline=False,
        )

    if dealer_type in ("both", "mirage") and snapshot.mirage_fruits:
        lines = [format_fruit_line(f) for f in snapshot.mirage_fruits]
        embed.add_field(
            name=f"🌊 Mirage Stock ({len(snapshot.mirage_fruits)} Fruits)",
            value="\n".join(lines)[:1024],
            inline=False,
        )

    embed.set_footer(text="Blox Fruits Auto-Tracker • Use /stock for live status")
    return embed
