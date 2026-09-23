import asyncio
import pytest
import discord
from config import DISCORD_TOKEN
from bot import bot


def test_discord_gateway_auth():
    if not DISCORD_TOKEN or DISCORD_TOKEN == "your_discord_bot_token_here":
        pytest.skip("No valid DISCORD_TOKEN configured")

    async def _runner():
        # Authenticate using the actual bot instance and its configured intents
        client = discord.Client(intents=bot.intents)
        logged_in = False

        @client.event
        async def on_ready():
            nonlocal logged_in
            logged_in = True
            await client.close()

        try:
            await asyncio.wait_for(client.start(DISCORD_TOKEN), timeout=12.0)
        except (asyncio.TimeoutError, Exception):
            await client.close()
        return logged_in

    success = asyncio.run(_runner())
    assert success is True, "Bot should successfully authenticate and reach on_ready with bot.intents"
