import discord
from discord.ext import commands
import os

cogs = ['commands.kaggl', 'commands.codeforces']

class CodeA2ZManager(commands.Bot):
    def __init__(self, command_prefix: str, intents: discord.Intents, **kwargs):
        super().__init__(command_prefix=command_prefix, intents=intents, **kwargs)
    
    async def setup_hook(self) -> None:
        for cog in cogs:
            await self.load_extension(cog)
        await self.tree.sync()

    async def on_ready(self):
        print('Manager is on duty!')

if __name__ == '__main__':
    bot = CodeA2ZManager(command_prefix='!', intents=discord.Intents.all())
    bot.run(os.getenv("DISCORD_TOKEN"))
