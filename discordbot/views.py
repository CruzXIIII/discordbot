import discord
from typing import Optional
from models import StockSnapshot
from embeds import build_stock_embed, build_countdown_embed
import stock_api


class StockView(discord.ui.View):
    def __init__(self, snapshot: StockSnapshot, current_view: str = "all", timeout: Optional[float] = 180.0):
        super().__init__(timeout=timeout)
        self.snapshot = snapshot
        self.current_view = current_view
        self.message: Optional[discord.Message] = None
        self._update_button_styles()

    def _update_button_styles(self):
        for child in self.children:
            if isinstance(child, discord.ui.Button):
                if child.custom_id == "btn_all":
                    child.style = discord.ButtonStyle.primary if self.current_view == "all" else discord.ButtonStyle.secondary
                elif child.custom_id == "btn_regular":
                    child.style = discord.ButtonStyle.primary if self.current_view == "regular" else discord.ButtonStyle.secondary
                elif child.custom_id == "btn_mirage":
                    child.style = discord.ButtonStyle.primary if self.current_view == "mirage" else discord.ButtonStyle.secondary
                elif child.custom_id == "btn_countdown":
                    child.style = discord.ButtonStyle.primary if self.current_view == "countdown" else discord.ButtonStyle.secondary

    async def on_timeout(self):
        for child in self.children:
            if isinstance(child, discord.ui.Button):
                child.disabled = True
        if self.message:
            try:
                await self.message.edit(view=self)
            except Exception:
                pass

    @discord.ui.button(label="All Stock", style=discord.ButtonStyle.primary, emoji="🍈", custom_id="btn_all")
    async def on_all_clicked(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.current_view = "all"
        self._update_button_styles()
        embed = build_stock_embed(self.snapshot, view_type="all")
        await interaction.response.edit_message(embed=embed, view=self)

    @discord.ui.button(label="Regular Dealer", style=discord.ButtonStyle.secondary, emoji="🏪", custom_id="btn_regular")
    async def on_regular_clicked(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.current_view = "regular"
        self._update_button_styles()
        embed = build_stock_embed(self.snapshot, view_type="regular")
        await interaction.response.edit_message(embed=embed, view=self)

    @discord.ui.button(label="Mirage Dealer", style=discord.ButtonStyle.secondary, emoji="🌊", custom_id="btn_mirage")
    async def on_mirage_clicked(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.current_view = "mirage"
        self._update_button_styles()
        embed = build_stock_embed(self.snapshot, view_type="mirage")
        await interaction.response.edit_message(embed=embed, view=self)

    @discord.ui.button(label="Countdown", style=discord.ButtonStyle.secondary, emoji="⏱️", custom_id="btn_countdown")
    async def on_countdown_clicked(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.current_view = "countdown"
        self._update_button_styles()
        embed = build_countdown_embed(self.snapshot)
        await interaction.response.edit_message(embed=embed, view=self)

    @discord.ui.button(label="Refresh", style=discord.ButtonStyle.success, emoji="🔄", custom_id="btn_refresh")
    async def on_refresh_clicked(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        try:
            new_snapshot = await stock_api.fetch_stock_async(force_refresh=True)
            self.snapshot = new_snapshot
            if self.current_view == "countdown":
                embed = build_countdown_embed(self.snapshot)
            else:
                embed = build_stock_embed(self.snapshot, view_type=self.current_view)
            await interaction.edit_original_response(embed=embed, view=self)
        except Exception as e:
            await interaction.followup.send(f"⚠️ Error refreshing stock: {e}", ephemeral=True)
