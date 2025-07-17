import discord
from discord.ext import commands, tasks
import os
from datetime import datetime, timedelta

TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

reminders = []

class Reminder:
    def __init__(self, user_id, message, remind_at):
        self.user_id = user_id
        self.message = message
        self.remind_at = remind_at

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
    reminder_task.start()

@bot.command()
async def remindme(ctx, time: int, *, message: str):
    """
    Set a reminder in minutes.
    Usage: !remindme <minutes> <message>
    """
    remind_at = datetime.utcnow() + timedelta(minutes=time)
    reminders.append(Reminder(ctx.author.id, message, remind_at))
    await ctx.send(f"⏰ Reminder set for {time} minutes from now!")

@tasks.loop(seconds=30)
async def reminder_task():
    now = datetime.utcnow()
    to_remove = []
    for reminder in reminders:
        if now >= reminder.remind_at:
            user = await bot.fetch_user(reminder.user_id)
            embed = discord.Embed(
                title="Reminder ⏰",
                description=reminder.message,
                color=discord.Color.blue(),
                timestamp=datetime.utcnow()
            )
            await user.send(embed=embed)
            to_remove.append(reminder)
    for r in to_remove:
        reminders.remove(r)

# Railway keepalive: simple web server using Flask
from flask import Flask

app = Flask(__name__)

@app.route("/")
def home():
    return "Discord Reminder Bot is running!"

if __name__ == "__main__":
    import threading

    def run_flask():
        app.run(host="0.0.0.0", port=int(os.getenv("PORT", 8080)))
    
    flask_thread = threading.Thread(target=run_flask)
    flask_thread.start()

    bot.run(TOKEN)
