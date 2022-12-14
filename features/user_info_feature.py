import discord, asyncio

from discord.utils import get
from discord.ext import commands, tasks
from features.spreadsheet_extract import pull_sheet_data
from datetime import date, datetime

CHANNEL_ID = 1047618947761061898

def add_user_info_feature(client): 
    roster_data = pull_sheet_data()
    birthdays = __extract_birthdays(roster_data)

    @client.command()
    async def email(ctx, *args):
        if len(args) <= 1:
            await ctx.send("Please re-type command with a full name as an argument.")
            return
        
        full_name = ' '.join(args)
        user = roster_data.get(full_name)
        if user:
            user_email = user['email']
            await ctx.send(user_email)
        else:
            await ctx.send("User was not found, please re-enter a full name.")
    

    @client.command()
    async def phone(ctx, *args):
        if len(args) <= 1:
            await ctx.send("Please re-type command with a full name as an argument.")
            return
        
        full_name = ' '.join(args)
        user = roster_data.get(full_name)
        if user:
            user_email = user['phone']
            await ctx.send(user_email)
        else:
            await ctx.send("User was not found, please re-enter a full name.")
    
    @tasks.loop(minutes=1)
    async def birthday():
        current_day, current_month = str(date.today().day), str(date.today().month)
        if birthdays.get((current_month, current_day)):
            channel = client.get_channel(CHANNEL_ID)
            current_birthday = birthdays[(current_month, current_day)]
            birthday_message = "@everyone " + current_birthday[0] + " is now " + current_birthday[1] + " years old. " + "Everyone wish him a happy birthday!"
            sent = False
            current_year = date.today().year
            start_of_birthday = datetime(current_year, int(current_month), int(current_day))
            end_of_birthday = datetime(current_year, int(current_month), int(current_day)+1)
            async for old_msg in channel.history(after=start_of_birthday, before=end_of_birthday):
                if old_msg.content == birthday_message:
                    sent = True
                    break

            if not sent:
                await channel.send(birthday_message)
    
    @client.listen()
    async def on_ready():
        await birthday.start()
    
def __extract_birthdays(roster_data):
    birthdays = {}
    
    for name, data in roster_data.items():
        birthday = data["birthday"].split("/")
        month, day, year = str(birthday[0]), str(birthday[1]), int(birthday[2])
        birthdays[(month, day)] = (name, str(int(date.today().year) - year))
    return birthdays