import logging
from typing import Literal, Optional, Union
import discord
from discord import app_commands
from discord.ext import commands

from config import DISCORD_TOKEN, BOT_PREFIX
from bot_config import config_store
from models import Fruit, StockSnapshot
from embeds import (
    build_stock_embed,
    build_countdown_embed,
    build_fruit_detail_embed,
)
from views import StockView
from tracker import StockTracker
import stock_api
from fruit_catalog import get_fruit_by_name, ALL_FRUIT_NAMES

logger = logging.getLogger("bloxfruits.bot")

# Standard default intents - avoids requesting unapproved privileged message_content intent
intents = discord.Intents.default()


class BloxFruitsBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix=BOT_PREFIX, intents=intents, help_command=None)
        self.tracker = StockTracker(self)
        self._synced = False

    async def setup_hook(self):
        # Sync slash commands once at startup
        if not self._synced:
            try:
                synced = await self.tree.sync()
                self._synced = True
                logger.info("Successfully synced %d application (slash) commands.", len(synced))
            except Exception as e:
                logger.error("Failed to sync application commands: %s", e)


bot = BloxFruitsBot()
tracker = bot.tracker


@bot.event
async def on_ready():
    logger.info("Logged in as %s (ID: %s)", bot.user.name, bot.user.id)

    # Set bot rich presence activity
    activity = discord.Activity(
        type=discord.ActivityType.watching,
        name="/stock • Blox Fruits Dealer"
    )
    await bot.change_presence(status=discord.Status.online, activity=activity)

    # Start background stock tracker
    tracker.start()
    logger.info("Blox Fruits Stock Bot is fully initialized and operational.")


# ==========================================================
# AUTOCOMPLETE HELPER
# ==========================================================

async def fruit_autocomplete(interaction: discord.Interaction, current: str):
    current_lower = current.strip().lower()
    matches = [
        name for name in ALL_FRUIT_NAMES
        if current_lower in name.lower()
    ]
    return [
        app_commands.Choice(name=name, value=name)
        for name in matches[:25]
    ]


# ==========================================================
# SLASH COMMANDS (app_commands)
# ==========================================================

@bot.tree.command(name="stock", description="Check the current Blox Fruits dealer stock and countdown to restock.")
@app_commands.describe(dealer="Select which dealer inventory to view (All, Regular, or Mirage)")
async def slash_stock(
    interaction: discord.Interaction,
    dealer: Literal["all", "regular", "mirage"] = "all"
):
    await interaction.response.defer()
    try:
        snapshot = await stock_api.fetch_stock_async(force_refresh=False)
        embed = build_stock_embed(snapshot, view_type=dealer)
        view = StockView(snapshot, current_view=dealer)
        msg = await interaction.followup.send(embed=embed, view=view)
        if isinstance(msg, discord.Message):
            view.message = msg
        else:
            try:
                view.message = await interaction.original_response()
            except Exception:
                pass
    except Exception as e:
        logger.error("Error in /stock command: %s", e)
        await interaction.followup.send(
            f"❌ Unable to retrieve stock data right now. Please try again shortly.\n*Error: {e}*",
            ephemeral=True
        )


@bot.tree.command(name="countdown", description="View countdown timers for the Regular and Mirage dealer resets.")
async def slash_countdown(interaction: discord.Interaction):
    await interaction.response.defer()
    try:
        snapshot = await stock_api.fetch_stock_async(force_refresh=False)
        embed = build_countdown_embed(snapshot)
        view = StockView(snapshot, current_view="countdown")
        msg = await interaction.followup.send(embed=embed, view=view)
        if isinstance(msg, discord.Message):
            view.message = msg
        else:
            try:
                view.message = await interaction.original_response()
            except Exception:
                pass
    except Exception as e:
        logger.error("Error in /countdown command: %s", e)
        await interaction.followup.send(f"❌ Error fetching countdown: {e}", ephemeral=True)


@bot.tree.command(name="fruit", description="Check details, value, and current stock status of a specific fruit.")
@app_commands.describe(name="Name of the fruit to check (e.g. Kitsune, Buddha, Leopard, Dragon)")
@app_commands.autocomplete(name=fruit_autocomplete)
async def slash_fruit(interaction: discord.Interaction, name: str):
    await interaction.response.defer()
    try:
        snapshot = await stock_api.fetch_stock_async(force_refresh=False)
        target = snapshot.find_fruit(name)

        if target:
            is_in_normal = any(f.name.lower() == target.name.lower() for f in snapshot.normal_fruits)
            is_in_mirage = any(f.name.lower() == target.name.lower() for f in snapshot.mirage_fruits)
        else:
            # Query comprehensive fruit catalog for canonical properties
            catalog_fruit = get_fruit_by_name(name)
            if catalog_fruit:
                target = catalog_fruit
                is_in_normal = False
                is_in_mirage = False
            else:
                popular_sample = ", ".join(ALL_FRUIT_NAMES[:8])
                await interaction.followup.send(
                    f"❌ Fruit **{name}** was not found in Blox Fruits.\n"
                    f"*Try searching for:* {popular_sample}...",
                    ephemeral=True
                )
                return

        embed = build_fruit_detail_embed(target, is_in_normal, is_in_mirage)
        await interaction.followup.send(embed=embed)
    except Exception as e:
        logger.error("Error in /fruit command: %s", e)
        await interaction.followup.send(f"❌ Error searching fruit: {e}", ephemeral=True)


# ==========================================================
# GROUP: /track (Server announcement management)
# ==========================================================
track_group = app_commands.Group(
    name="track",
    description="Configure stock tracking announcements for your server.",
    guild_only=True
)


@track_group.command(name="set", description="Set this channel (or a specified channel) for stock announcements.")
@app_commands.describe(channel="Channel to send announcements to (defaults to current channel)")
@app_commands.default_permissions(manage_guild=True)
async def slash_track_set(
    interaction: discord.Interaction,
    channel: Optional[Union[discord.TextChannel, discord.Thread]] = None
):
    guild_id = interaction.guild_id
    if not guild_id or not interaction.guild:
        await interaction.response.send_message("❌ This command can only be used in a Discord server.", ephemeral=True)
        return

    target_channel = channel or interaction.channel
    if not isinstance(target_channel, (discord.TextChannel, discord.Thread)):
        await interaction.response.send_message(
            "❌ Stock updates must be sent to a standard text channel or thread.",
            ephemeral=True
        )
        return

    # Verify bot permissions in the target channel
    me = interaction.guild.me
    perms = target_channel.permissions_for(me)
    if not (perms.send_messages and perms.embed_links):
        await interaction.response.send_message(
            f"❌ I don't have permission to send messages and embed links in {target_channel.mention}! "
            "Please check channel permissions.",
            ephemeral=True
        )
        return

    config_store.set_channel(guild_id, target_channel.id)
    await interaction.response.send_message(
        f"✅ Stock announcements will now be sent to {target_channel.mention} whenever dealer inventory rotates!"
    )


@track_group.command(name="stop", description="Disable stock announcements in this server.")
@app_commands.default_permissions(manage_guild=True)
async def slash_track_stop(interaction: discord.Interaction):
    guild_id = interaction.guild_id
    if not guild_id:
        await interaction.response.send_message("❌ This command can only be used in a server.", ephemeral=True)
        return

    removed = config_store.remove_channel(guild_id)
    if removed:
        await interaction.response.send_message("✅ Stock announcements disabled for this server.")
    else:
        await interaction.response.send_message("ℹ️ No stock announcement channel was configured for this server.", ephemeral=True)


@track_group.command(name="pingrole", description="Set a role to ping when stock rotates or high-value fruits appear.")
@app_commands.describe(role="Role to ping (leave empty to disable pings)")
@app_commands.default_permissions(manage_guild=True)
async def slash_track_pingrole(interaction: discord.Interaction, role: Optional[discord.Role] = None):
    guild_id = interaction.guild_id
    if not guild_id:
        await interaction.response.send_message("❌ This command can only be used in a server.", ephemeral=True)
        return

    if role is None:
        config_store.set_ping_role(guild_id, None)
        await interaction.response.send_message("✅ Disabled role pings for stock announcements.")
    else:
        config_store.set_ping_role(guild_id, role.id)
        await interaction.response.send_message(f"✅ Will now ping {role.mention} during stock announcements!")


@track_group.command(name="status", description="Check current stock announcement channel and settings.")
async def slash_track_status(interaction: discord.Interaction):
    guild_id = interaction.guild_id
    if not guild_id:
        await interaction.response.send_message("❌ This command can only be used in a server.", ephemeral=True)
        return

    chan_id = config_store.get_channel(guild_id)
    role_id = config_store.get_ping_role(guild_id)
    watchlist = config_store.get_watchlist(guild_id)

    chan_text = f"<#{chan_id}>" if chan_id else "*None (disabled)*"
    role_text = f"<@&{role_id}>" if role_id else "*None*"
    watch_text = ", ".join(watchlist)

    embed = discord.Embed(
        title="⚙️ Server Stock Tracker Settings",
        color=0x5865F2,
    )
    embed.add_field(name="Announcement Channel", value=chan_text, inline=False)
    embed.add_field(name="Ping Role", value=role_text, inline=False)
    embed.add_field(name="Watched Fruits (Alert)", value=watch_text or "*None*", inline=False)
    await interaction.response.send_message(embed=embed, ephemeral=True)

bot.tree.add_command(track_group)


# ==========================================================
# GROUP: /watchlist (High-demand fruit alerts)
# ==========================================================
watchlist_group = app_commands.Group(
    name="watchlist",
    description="Manage high-demand fruit alerts.",
    guild_only=True
)


@watchlist_group.command(name="add", description="Add a fruit to your server's alert watchlist.")
@app_commands.describe(fruit="Fruit name to watch")
@app_commands.autocomplete(fruit=fruit_autocomplete)
@app_commands.default_permissions(manage_guild=True)
async def slash_watchlist_add(interaction: discord.Interaction, fruit: str):
    guild_id = interaction.guild_id
    if not guild_id:
        await interaction.response.send_message("❌ This command can only be used in a server.", ephemeral=True)
        return

    added = config_store.add_to_watchlist(guild_id, fruit)
    if added:
        await interaction.response.send_message(f"✅ Added **{fruit.title()}** to the server stock alert watchlist!")
    else:
        await interaction.response.send_message(f"ℹ️ **{fruit.title()}** is already in the watchlist.", ephemeral=True)


@watchlist_group.command(name="remove", description="Remove a fruit from your server's alert watchlist.")
@app_commands.describe(fruit="Fruit name to remove")
@app_commands.autocomplete(fruit=fruit_autocomplete)
@app_commands.default_permissions(manage_guild=True)
async def slash_watchlist_remove(interaction: discord.Interaction, fruit: str):
    guild_id = interaction.guild_id
    if not guild_id:
        await interaction.response.send_message("❌ This command can only be used in a server.", ephemeral=True)
        return

    removed = config_store.remove_from_watchlist(guild_id, fruit)
    if removed:
        await interaction.response.send_message(f"✅ Removed **{fruit.title()}** from the watchlist.")
    else:
        await interaction.response.send_message(f"ℹ️ **{fruit.title()}** was not found in the watchlist.", ephemeral=True)


@watchlist_group.command(name="list", description="List all fruits currently being watched for alerts.")
async def slash_watchlist_list(interaction: discord.Interaction):
    guild_id = interaction.guild_id
    if not guild_id:
        await interaction.response.send_message("❌ This command can only be used in a server.", ephemeral=True)
        return

    watchlist = config_store.get_watchlist(guild_id)
    items = "\n".join(f"• **{f}**" for f in watchlist) if watchlist else "*No fruits in watchlist.*"
    embed = discord.Embed(
        title="📋 Stock Alert Watchlist",
        description=f"Whenever any of these fruits appear in dealer stock, an alert is triggered:\n\n{items}",
        color=0xE91E63
    )
    await interaction.response.send_message(embed=embed)

bot.tree.add_command(watchlist_group)


@bot.tree.command(name="help", description="Show all available Blox Fruits stock commands and help.")
async def slash_help(interaction: discord.Interaction):
    embed = discord.Embed(
        title="🍈 Blox Fruits Stock Bot — Command Guide",
        description="Real-time stock tracker for Regular and Mirage Blox Fruit Dealers.",
        color=0x5865F2,
    )
    embed.add_field(
        name="📊 Stock Checking",
        value=(
            "`/stock` — View live stock with interactive filter & refresh buttons\n"
            "`/countdown` — View remaining time until next dealer reset\n"
            "`/fruit <name>` — Check fruit price, rarity, demand, value, and current stock status"
        ),
        inline=False,
    )
    embed.add_field(
        name="📢 Stock Announcements & Alerts (Admin)",
        value=(
            "`/track set [channel]` — Set auto-announcements channel for stock rotations\n"
            "`/track stop` — Disable auto-announcements\n"
            "`/track pingrole [role]` — Mention a role when stock rotates\n"
            "`/track status` — View active announcement settings\n"
            "`/watchlist add <fruit>` — Add a fruit to highlight alert list\n"
            "`/watchlist remove <fruit>` — Remove a fruit from highlight alert list\n"
            "`/watchlist list` — View watched fruits"
        ),
        inline=False,
    )
    embed.set_footer(text="Data sourced live from bloxfruitsvalues • 100% synchronized")
    await interaction.response.send_message(embed=embed)


def start_bot():
    """Starts the bot with the configured token."""
    if not DISCORD_TOKEN:
        raise ValueError("DISCORD_TOKEN is not set in environment or config.")
    bot.run(DISCORD_TOKEN)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
    start_bot()
