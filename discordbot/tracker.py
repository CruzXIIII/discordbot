import logging
import discord
from discord.ext import tasks
from typing import Optional, List
from config import STOCK_CHECK_INTERVAL_SECONDS
from bot_config import config_store
from embeds import build_announcement_embed
import stock_api

logger = logging.getLogger("bloxfruits.tracker")


class StockTracker:
    def __init__(self, bot: discord.Client):
        self.bot = bot
        self.is_first_run = True

    def start(self):
        if not self.track_loop.is_running():
            logger.info("Starting background stock tracking task (interval=%ds)...", STOCK_CHECK_INTERVAL_SECONDS)
            self.track_loop.change_interval(seconds=STOCK_CHECK_INTERVAL_SECONDS)
            self.track_loop.start()
        else:
            logger.debug("Stock tracking task is already running.")

    def stop(self):
        if self.track_loop.is_running():
            self.track_loop.cancel()
            logger.info("Stock tracking task stopped.")

    @tasks.loop(seconds=STOCK_CHECK_INTERVAL_SECONDS)
    async def track_loop(self):
        try:
            snapshot = await stock_api.fetch_stock_async(force_refresh=False)
            curr_normal_reset = snapshot.normal_window.resets_at
            curr_mirage_reset = snapshot.mirage_window.resets_at

            last_normal_reset = config_store.last_normal_reset
            last_mirage_reset = config_store.last_mirage_reset

            # First run initialization: store current reset times to avoid spamming on initial launch
            if self.is_first_run or (last_normal_reset == 0 and last_mirage_reset == 0):
                self.is_first_run = False
                config_store.update_last_resets(curr_normal_reset, curr_mirage_reset)
                logger.info("Stock tracker initialized with current reset times (Normal: %d, Mirage: %d).",
                            curr_normal_reset, curr_mirage_reset)
                return

            # Check if rotation has occurred and is ready (not in pending/scan state)
            normal_changed = (curr_normal_reset != last_normal_reset) and (curr_normal_reset > 0)
            mirage_changed = (curr_mirage_reset != last_mirage_reset) and (curr_mirage_reset > 0)

            # If dealer is still pending/scanning in Roblox, wait until fresh inventory is loaded
            if normal_changed and snapshot.normal_pending:
                logger.info("Normal dealer restock detected but data is pending. Waiting for scan to complete...")
                normal_changed = False

            if mirage_changed and snapshot.mirage_pending:
                logger.info("Mirage dealer restock detected but data is pending. Waiting for scan to complete...")
                mirage_changed = False

            if not normal_changed and not mirage_changed:
                return

            dealer_type = "both" if (normal_changed and mirage_changed) else ("normal" if normal_changed else "mirage")
            logger.info("Stock rotation confirmed! Dealer: %s", dealer_type)

            # Update saved timestamps for the rotated dealer(s)
            new_normal_reset = curr_normal_reset if normal_changed else last_normal_reset
            new_mirage_reset = curr_mirage_reset if mirage_changed else last_mirage_reset
            config_store.update_last_resets(new_normal_reset, new_mirage_reset)

            # Broadcast to all registered channels
            all_channels = config_store.data.get("channels", {})
            for guild_id_str, channel_id in list(all_channels.items()):
                try:
                    guild_id = int(guild_id_str)
                    channel = self.bot.get_channel(channel_id)
                    if channel is None:
                        try:
                            channel = await self.bot.fetch_channel(channel_id)
                        except Exception:
                            logger.warning("Channel %d not found or bot lacks access, skipping", channel_id)
                            continue

                    # Check for watchlist fruits in this guild with flexible matching
                    watchlist = config_store.get_watchlist(guild_id)
                    active_fruit_names = []
                    if dealer_type in ("both", "normal"):
                        active_fruit_names.extend([f.name.lower() for f in snapshot.normal_fruits])
                    if dealer_type in ("both", "mirage"):
                        active_fruit_names.extend([f.name.lower() for f in snapshot.mirage_fruits])

                    hits = []
                    for w in watchlist:
                        w_low = w.lower()
                        if any(w_low == fn or w_low in fn or fn in w_low for fn in active_fruit_names):
                            hits.append(w)

                    embed = build_announcement_embed(snapshot, watched_hits=hits, dealer_type=dealer_type)

                    ping_content: Optional[str] = None
                    ping_role_id = config_store.get_ping_role(guild_id)
                    if hits and ping_role_id:
                        ping_content = f"<@&{ping_role_id}> 🚨 High value fruit alert!"
                    elif ping_role_id and not hits:
                        ping_content = f"<@&{ping_role_id}>"

                    await channel.send(content=ping_content, embed=embed)
                    logger.info("Sent stock announcement to channel %d in guild %d", channel_id, guild_id)
                except Exception as ex:
                    logger.error("Failed to send announcement to guild %s: %s", guild_id_str, ex)

        except Exception as e:
            logger.error("Error in stock tracker loop: %s", e)

    @track_loop.before_loop
    async def before_track_loop(self):
        await self.bot.wait_until_ready()
