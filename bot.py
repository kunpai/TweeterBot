from click import command
import discord
import os
import random
import interactions
from discord_slash import SlashCommand, SlashContext
from discord.ext import tasks
from dotenv import load_dotenv
from datetime import datetime, date, time, timedelta
import numpy as np
import tweepy
import openai
import sqlite3
load_dotenv()

intents = discord.Intents.default()
intents.members = True
client = discord.Client(intents = intents)
slash = SlashCommand(client, sync_commands=True)
openai.api_key = os.environ['API']
DATABASE = './userids.db'
connection = sqlite3.connect(DATABASE)
cursor = connection.cursor()

create_table = "CREATE TABLE IF NOT EXISTS data (name TEXT, userid TEXT, usernum TEXT)"
cursor.execute(create_table)

pictureflag = 0
tweetwithpic = ""
userid = ""
query = ""
number = ""

userids = {}
usernum = {}

#authenticating to access the twitter API
auth=tweepy.OAuthHandler(os.environ['consumer_key'],os.environ['consumer_secret_key'])
auth.set_access_token(os.environ['access_token'],os.environ['access_token_secret'])
api=tweepy.API(auth)

@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))
    for guild in client.guilds:
          print(
            f'{client.user} is connected to the following guild:\n'
          f'{guild.name}\n'
          )
    global members
    members = guild.members
    sendtweet.start()
    tweet_at_loop.start()

@slash.slash(name ="tweet", description="Sends a text tweet")
async def _tweet (ctx = SlashContext, tweet=None):
    api.update_status(tweet)
    embed = discord.Embed(
            title="Status", description="", color=0x0000ff)
    embed.set_author(name=ctx.author.name, icon_url=ctx.author.avatar_url)
    embed.add_field(name = tweet, value="Check out Twitter @TweeterPy", inline=False)
    await ctx.send(embed=embed)

@slash.slash(name ="picture", description="Sends a tweet with a picture")
async def _picture (ctx = SlashContext, *, tweet=None):
    embed = discord.Embed(
            title="Status", description="", color=0x0000ff)
    embed.set_author(name=ctx.author.name, icon_url=ctx.author.avatar_url)
    embed.add_field(name = "Next Steps", value="Upload the image next", inline=False)
    global pictureflag
    pictureflag = 1
    global tweetwithpic
    tweetwithpic = tweet
    await ctx.send(embed=embed)

@slash.slash(name ="search", description="Searchs for a username from screen name")
async def _search (ctx = SlashContext, search=None):
    embed = discord.Embed(
            title="Status", description="", color=0x0000ff)
    embed.set_author(name=ctx.author.name, icon_url=ctx.author.avatar_url)
    obj = api.search_users(q=search)
    # user = [user for user in obj]
    user_ids = [user.id for user in obj]
    user_names = [user.screen_name for user in obj]
    global userid
    userid = user_names[0]
    url = "https://twitter.com/intent/user?user_id=" + str(user_ids[0])
    global query
    query = search
    global number
    number = str(user_ids[0])
    embed.add_field(name = search, value=url, inline=False)
    #https://twitter.com/intent/user?user_id=
    await ctx.send(embed=embed)

@slash.slash(name ="add", description="Adds last username for quick lookup")
async def _add (ctx = SlashContext):
    global userid
    global query
    global usernum
    global number
    if query=="" or userid=="":
        embed = discord.Embed(
            title="Status", description="", color=0x0000ff)
        embed.set_author(name=ctx.author.name, icon_url=ctx.author.avatar_url)
        embed.add_field(name = "No username searched", value="Search for a username", inline=False)
    
    embed = discord.Embed(
            title="Added", description="", color=0x0000ff)
    embed.set_author(name=ctx.author.name, icon_url=ctx.author.avatar_url)
    embed.add_field(name = query, value=userid, inline=False)
    userids[query] = "@"+ userid
    usernum[query] = number
    # add these to the database
    global DATABASE
    connection = sqlite3.connect(DATABASE)
    cursor = connection.cursor()
    cursor.execute("INSERT INTO data VALUES (?,?,?)", (query, userids[query], usernum[query]))
    connection.commit()
    print(userids)
    query = ""
    userid = ""
    number = ""
    await ctx.send(embed=embed)

@slash.slash(name ="view", description="View the current username list")
async def _view (ctx = SlashContext):
    global DATABASE
    connection = sqlite3.connect(DATABASE)
    cursor = connection.cursor()
    dumpTable = cursor.execute("SELECT * FROM data")
    dump = dumpTable.fetchall()
    embed = discord.Embed(
            title="Table", description="", color=0x0000ff)
    embed.set_author(name=ctx.author.name, icon_url=ctx.author.avatar_url)
    for row in dump:
        embed.add_field(name = row[0], value=row[1], inline=False)
    await ctx.send(embed=embed)

@slash.slash(name = "follow", description="Follows last username added")
async def _follow (ctx = SlashContext):
    global usernum
    if query=="" or userid=="":
        embed = discord.Embed(
            title="Status", description="", color=0x0000ff)
        embed.set_author(name=ctx.author.name, icon_url=ctx.author.avatar_url)
        embed.add_field(name = "No username added", value="Search for a username", inline=False)
    
    api.create_friendship(user_id=usernum[list(usernum.keys())[-1]])
    embed = discord.Embed(
            title="Followed", description="", color=0x0000ff)
    embed.set_author(name=ctx.author.name, icon_url=ctx.author.avatar_url)
    embed.add_field(name = list(usernum.keys())[-1], value=userids[list(usernum.keys())[-1]], inline=False)
    await ctx.send(embed=embed)

@slash.slash(name = "unfollow", description="Unfollows last username added")
async def _unfollow (ctx = SlashContext):
    global usernum
    if query=="" or userid=="":
        embed = discord.Embed(
            title="Status", description="", color=0x0000ff)
        embed.set_author(name=ctx.author.name, icon_url=ctx.author.avatar_url)
        embed.add_field(name = "No username added", value="Search for a username", inline=False)
    
    api.destroy_friendship(user_id=usernum[list(usernum.keys())[-1]])
    embed = discord.Embed(
            title="Unfollowed", description="", color=0x0000ff)
    embed.set_author(name=ctx.author.name, icon_url=ctx.author.avatar_url)
    embed.add_field(name = list(usernum.keys())[-1], value=userids[list(usernum.keys())[-1]], inline=False)
    await ctx.send(embed=embed)

@slash.slash(name = "follow_all", description="Follows all usernames added")
async def _follow_all (ctx = SlashContext):
    global usernum
    if query=="" or userid=="":
        embed = discord.Embed(
            title="Status", description="", color=0x0000ff)
        embed.set_author(name=ctx.author.name, icon_url=ctx.author.avatar_url)
        embed.add_field(name = "No username added", value="Search for a username", inline=False)
    
    for key in usernum:
        api.create_friendship(user_id=usernum[key])
    embed = discord.Embed(
            title="Followed", description="", color=0x0000ff)
    embed.set_author(name=ctx.author.name, icon_url=ctx.author.avatar_url)
    for key in usernum:
        embed.add_field(name = key, value=userids[key], inline=False)
    await ctx.send(embed=embed)

@slash.slash(name = "unfollow_all", description="Unfollows all usernames added")
async def _unfollow_all (ctx = SlashContext):
    global usernum
    if query=="" or userid=="":
        embed = discord.Embed(
            title="Status", description="", color=0x0000ff)
        embed.set_author(name=ctx.author.name, icon_url=ctx.author.avatar_url)
        embed.add_field(name = "No username added", value="Search for a username", inline=False)
    
    for key in usernum:
        api.destroy_friendship(user_id=usernum[key])
    embed = discord.Embed(
            title="Unfollowed", description="", color=0x0000ff)
    embed.set_author(name=ctx.author.name, icon_url=ctx.author.avatar_url)
    for key in usernum:
        embed.add_field(name = key, value=userids[key], inline=False)
    await ctx.send(embed=embed)


@slash.slash(name = "dm", description="DMs last username added")
async def _dm (ctx = SlashContext, message = ""):
    global usernum
    if query=="" or userid=="":
        embed = discord.Embed(
            title="Status", description="", color=0x0000ff)
        embed.set_author(name=ctx.author.name, icon_url=ctx.author.avatar_url)
        embed.add_field(name = "No username added", value="Search for a username", inline=False)
    
    api.send_direct_message(recipient_id=usernum[list(usernum.keys())[-1]], text=message)
    embed = discord.Embed(
            title="DM Sent", description="", color=0x0000ff)
    embed.set_author(name=ctx.author.name, icon_url=ctx.author.avatar_url)
    embed.add_field(name = list(usernum.keys())[-1], value=message, inline=False)
    await ctx.send(embed=embed)

@slash.slash(name = "dm_specific", description="DMs a specific username")
async def _dm_specific (ctx = SlashContext, message = "", username = ""):
    global usernum
    if query=="" or userid=="":
        embed = discord.Embed(
            title="Status", description="", color=0x0000ff)
        embed.set_author(name=ctx.author.name, icon_url=ctx.author.avatar_url)
        embed.add_field(name = "No username added", value="Search for a username", inline=False)
    global DATABASE
    connection = sqlite3.connect(DATABASE)
    cursor = connection.cursor()
    searchTable = cursor.execute("SELECT * FROM data WHERE name = ?", (username,)).fetchall()
    userid = searchTable[0][2]
    api.send_direct_message(recipient_id=userid, text=message)
    embed = discord.Embed(
            title="DM Sent", description="", color=0x0000ff)
    embed.set_author(name=ctx.author.name, icon_url=ctx.author.avatar_url)
    embed.add_field(name = username, value=message, inline=False)
    await ctx.send(embed=embed)

@slash.slash(name = "tweet_ques", description="Tweets a question to a username from saved dictionary")
async def _tweet_at (ctx = SlashContext, person = ""):
    global DATABASE
    connection = sqlite3.connect(DATABASE)
    cursor = connection.cursor()
    command = cursor.execute("SELECT userid FROM data where name = ?", (person,)).fetchall()
    print(command)
    username = command[0][0]
    response = openai.Completion.create(
                engine="text-davinci-002",
                prompt="Ask an insightful question.",
                temperature=1,
                max_tokens=280
        )
    question = response.choices[0].text
    tweet = username + " " + question
    api.update_status(tweet)
    embed = discord.Embed(
            title="Tweeted", description="", color=0x0000ff)
    embed.set_author(name=ctx.author.name, icon_url=ctx.author.avatar_url)
    embed.add_field(name = username, value=question, inline=False)
    await ctx.send(embed=embed)

@tasks.loop(hours=12.0)
async def tweet_at_loop():
    print("tweeting")
    global DATABASE
    connection = sqlite3.connect(DATABASE)
    cursor = connection.cursor()
    # select random entry from database
    command = cursor.execute("SELECT * FROM data ORDER BY RANDOM() LIMIT 1").fetchall()
    print(command)
    username = command[0][1]
    response = openai.Completion.create(
            engine="text-davinci-002",
            prompt="Ask an insightful question.",
            temperature=1,
            max_tokens=280
    )
    question = response.choices[0].text
    tweet = username + " " + question
    api.update_status(tweet)

@tasks.loop(minutes=60.0)
async def sendtweet():
    print("Sending tweet")
    flag = random.randint(0,5)
    if flag == 0:
        response = openai.Completion.create(
                engine="text-davinci-002",
                prompt="What is your philosophy?",
                temperature=1,
                max_tokens=280
        )
    if flag == 1:
        response = openai.Completion.create(
                engine="text-davinci-002",
                prompt="What is the best piece of advice?",
                temperature=1,
                max_tokens=280
        )
    if flag == 2:
        response = openai.Completion.create(
                engine="text-davinci-002",
                prompt="What do self-help authors recommend?",
                temperature=1,
                max_tokens=280
        )
    if flag == 3:
        response = openai.Completion.create(
                engine="text-davinci-002",
                prompt="What is the best way to deal with your problems?",
                temperature=1,
                max_tokens=280
        )
    if flag == 4:
        response = openai.Completion.create(
                engine="text-davinci-002",
                prompt="What is the best quote?",
                temperature=1,
                max_tokens=280
        )
    if flag == 5:
        response = openai.Completion.create(
                engine="text-davinci-002",
                prompt="How to be a good human being?",
                temperature=1,
                max_tokens=280
        )
    tweet = response.choices[0].text
    print(tweet)
    if tweet != "" and tweet != " " and tweet != "\"" and tweet != "\" " and len(tweet)<=280 and len(tweet)>1:
        print(tweet)
        api.update_status(tweet)
    else:
        print("No tweet")
    

@client.event
async def on_message(message):
    if message.author == client.user:
        return
    
    global pictureflag
    if pictureflag == 1:
        if message.attachments:
            print("true")
            intro = message.author.name + '.jpg'  # file path where the intro will be saved to
            # save the mp3 file
            await message.attachments[0].save(intro)
            api.update_status_with_media(tweetwithpic, intro)
            return
        else:
            pictureflag = 0
            return
        
client.run(os.environ['DISCORD_TOKEN'])