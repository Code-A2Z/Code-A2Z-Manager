import discord
from discord.ext import commands
from discord import app_commands
from manager import CodeA2ZManager
from kaggle.api.kaggle_api_extended import KaggleApi
import random
import os

class Kaggl(commands.Cog):
    def __init__(self, bot: CodeA2ZManager):
        self.bot = bot
        self.api = KaggleApi()
        self.api.authenticate()

    @app_commands.command(name="kaggle_competitions", description="List ongoing Kaggle competitions")
    async def kaggle_competitions(self, ctx: discord.Interaction):
        # Check if the command is invoked in the correct channel
        if ctx.channel_id != int(os.getenv("KAGGLE_CHANNEL_ID")):
            await ctx.response.send_message("This command can only be used in the Kaggle channel.", ephemeral=True)
            return

        # Fetch the ongoing competitions sorted by latest deadline
        competitions = self.api.competitions_list(sort_by="latestDeadline")
        
        if not competitions:
            await ctx.response.send_message("No competitions found.", ephemeral=True)
            return

        competitions.sort(key=lambda x: x.deadline)
        for competition in competitions[:5]:
            embed = discord.Embed(
                title=competition.title,
                description=competition.description if competition.description else "No description available.",
                color=discord.Color.blue()
            )
            embed.set_thumbnail(url="https://github.com/user-attachments/assets/d6cdddfe-8d79-4af6-92f5-d9593c5f5768")
            embed.add_field(name="Deadline", value=str(competition.deadline), inline=False)
            embed.add_field(name="URL", value=f"[Visit Competition]({competition.url})", inline=True)
            embed.add_field(name="Category", value=competition.category, inline=True)

            await ctx.followup.send(embed=embed, ephemeral=True)

    @app_commands.command(name="kaggle_datasets", description="Search for Kaggle datasets")
    async def kaggle_datasets(self, ctx: discord.Interaction, *, query: str):
        # Check if the command is invoked in the correct channel
        if ctx.channel_id != int(os.getenv("KAGGLE_CHANNEL_ID")):
            await ctx.response.send_message("This command can only be used in the Kaggle channel.", ephemeral=True)
            return

        all_datasets = []
        for page in range(1, 3):
            datasets = self.api.dataset_list(search=query, page=page)
            all_datasets.extend(datasets)

        if not all_datasets:
            await ctx.response.send_message(f"No datasets found for '{query}'.", ephemeral=True)
            return

        await ctx.response.send_message(f"Here are the top datasets for '{query}':", ephemeral=True)
        random_datasets = random.sample(all_datasets, min(5, len(all_datasets)))
        random_datasets.sort(key=lambda x: x.downloadCount, reverse=True)

        for dataset in random_datasets:
            embed = discord.Embed(
                title=dataset.title,
                description=dataset.description if dataset.description else "No description available.",
                color=discord.Color.green()
            )
            embed.set_thumbnail(url="https://github.com/user-attachments/assets/d6cdddfe-8d79-4af6-92f5-d9593c5f5768")
            embed.add_field(name="URL", value=f"[Visit Dataset]({dataset.url})", inline=False)
            embed.add_field(name="Size", value=dataset.size, inline=False)
            embed.add_field(name="Last Updated", value=dataset.lastUpdated, inline=False)
            embed.add_field(name="Number of Downloads", value=dataset.downloadCount, inline=False)

            await ctx.followup.send(embed=embed, ephemeral=True)

async def setup(bot):
    await bot.add_cog(Kaggl(bot))
