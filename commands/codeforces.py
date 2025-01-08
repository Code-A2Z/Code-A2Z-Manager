import discord
from discord.ext import commands
from discord import app_commands
from manager import CodeA2ZManager
from datetime import datetime
import requests
import random
import os

PROBLEMS_URL = "https://codeforces.com/api/problemset.problems"
CONTESTS_URL = "https://codeforces.com/api/contest.list"

TAGS = ["dp", "math", "greedy", "graphs", "binary search", "brute force", "strings", "trees", "number theory",
        "geometry", "sortings", "implementation", "data structures", "combinatorics", "constructive algorithms",
        "two pointers", "bitmasks"]

RATINGS = [800, 900, 1000, 1100, 1200, 1300, 1400, 1500, 1600, 1700, 1800, 1900, 2000, 2100, 
           2500, 2600, 2700, 2800, 2900, 3000, 3100, 3200, 3300, 3400, 3500]

class Codeforces(commands.Cog):
    def __init__(self, bot: CodeA2ZManager):
        self.bot = bot

    @app_commands.command(name="cf_problems", description="Get Codeforces problems filtered by tags and rating")
    @app_commands.choices(
        tag=[app_commands.Choice(name=tag, value=tag) for tag in TAGS],
        rating=[app_commands.Choice(name=str(rating), value=rating) for rating in RATINGS]
    )
    async def cf_problems(self, interaction: discord.Interaction, tag: app_commands.Choice[str], rating: app_commands.Choice[int]):
        """
        Fetch problems from Codeforces API filtered by tag and rating.
        """
        # Check if the command is invoked in the correct channel
        if str(interaction.channel_id) != os.getenv("CP_CHANNEL_ID"):
            await interaction.response.send_message("This command can only be used in the Competitive Programming channel.", ephemeral=True)
            return

        await interaction.response.defer()

        response = requests.get(PROBLEMS_URL)
        if response.status_code != 200:
            await interaction.followup.send("Failed to fetch problems from Codeforces API. Please try again later.")
            return

        data = response.json()
        if data["status"] != "OK":
            await interaction.followup.send("Failed to fetch problems from Codeforces API. Please try again later.")
            return

        problems = data["result"]["problems"]
        filtered_problems = []

        for problem in problems:
            if tag and tag.value not in problem.get("tags", []):
                continue
            if rating and problem.get("rating") != rating.value:
                continue
            filtered_problems.append(problem)

        if not filtered_problems:
            await interaction.followup.send("No problems found matching the given criteria.")
            return

        random_problems = random.sample(filtered_problems, min(5, len(filtered_problems)))
        for problem in random_problems:
            problem_url = f"https://codeforces.com/problemset/problem/{problem['contestId']}/{problem['index']}"
            tags = ", ".join(problem.get("tags", []))

            embed = discord.Embed(
                title=problem["name"],
                description=f"[Solve Problem]({problem_url})",
                color=discord.Color.gold()
            )
            embed.set_thumbnail(url="https://codeforces.org/s/118231/images/codeforces-logo-with-telegram.png")
            embed.set_footer(text=f"Contest ID: {problem['contestId']} | Index: {problem['index']}")
            embed.add_field(name="Type", value=problem.get("type", "Unknown"), inline=True)
            embed.add_field(name="Rating", value=str(problem.get("rating", "Unknown")), inline=True)
            embed.add_field(name="Tags", value=tags or "No Tags", inline=False)

            await interaction.followup.send(embed=embed, ephemeral=True)

    @app_commands.command(name="cf_contests", description="Get upcoming Codeforces contests")
    async def cf_contests(self, interaction: discord.Interaction):
        """
        Fetch and display upcoming contests from Codeforces API.
        """
        # Check if the command is invoked in the correct channel
        if str(interaction.channel_id) != os.getenv("CP_CHANNEL_ID"):
            await interaction.response.send_message("This command can only be used in the Competitive Programming channel.", ephemeral=True)
            return

        await interaction.response.defer()

        response = requests.get(CONTESTS_URL)
        if response.status_code != 200:
            await interaction.followup.send("Failed to fetch contests from Codeforces API. Please try again later.")
            return

        data = response.json()
        if data["status"] != "OK":
            await interaction.followup.send("Failed to fetch contests from Codeforces API. Please try again later.")
            return

        contests = []
        for contest in data["result"]:
            if contest['phase'] == 'BEFORE' or contest['phase'] == 'CODING':
                contests.append(contest)

        if not contests:
            await interaction.followup.send("No upcoming contests found.")
            return

        contests.sort(key=lambda x: x['relativeTimeSeconds']//3600, reverse=True)
        for contest in contests:
            embed = discord.Embed(title=contest['name'], color=discord.Color.gold())
            embed.set_thumbnail(url="https://codeforces.org/s/118231/images/codeforces-logo-with-telegram.png")
            embed.add_field(name="Type", value=contest['type'], inline=True)
            embed.add_field(name="Duration", value=f"{contest['durationSeconds'] // 3600} hours", inline=True)
            embed.add_field(name="Contest Date & Time", value=datetime.utcfromtimestamp(contest['startTimeSeconds'] + 19800).strftime('%A, %d %B %Y %I:%M:%S %p'), inline=False)
            embed.set_footer(text=f"Contest ID: {contest['id']} | Phase: {contest['phase']} | Left Time: {contest['relativeTimeSeconds'] // 3600} hours")

            await interaction.followup.send(embed=embed, ephemeral=True)

async def setup(bot):
    await bot.add_cog(Codeforces(bot))
