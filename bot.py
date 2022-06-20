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
load_dotenv()

intents = discord.Intents.default()
intents.members = True
client = discord.Client(intents = intents)
slash = SlashCommand(client, sync_commands=True)
openai.api_key = os.environ['API']


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
    print(userids)
    query = ""
    userid = ""
    number = ""
    await ctx.send(embed=embed)

@slash.slash(name ="view", description="View the current username list")
async def _view (ctx = SlashContext):
    embed = discord.Embed(
            title="Saved Usernames", description="", color=0x0000ff)
    embed.set_author(name=ctx.author.name, icon_url=ctx.author.avatar_url)
    for key in userids:
        embed.add_field(name = key, value=userids[key], inline=False)
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
    
    api.send_direct_message(recipient_id=usernum[username], text=message)
    embed = discord.Embed(
            title="DM Sent", description="", color=0x0000ff)
    embed.set_author(name=ctx.author.name, icon_url=ctx.author.avatar_url)
    embed.add_field(name = username, value=message, inline=False)
    await ctx.send(embed=embed)

@tasks.loop(minutes=30.0)
async def sendtweet():
    print("Sending tweet")
    response = openai.Completion.create(
    engine="davinci",
    prompt="What is the best philosophy in life?",
    temperature=0.75,
    max_tokens=150,
    top_p=1,
    presence_penalty=0.6,
    stop=["\n"],
    )
    tweet = response.choices[0].text
    if tweet != "" and tweet != " " and tweet != "\"" and tweet != "\" " and len(tweet)<=140 and len(tweet)>1:
        print(tweet)
        api.update_status(tweet)
    else:
        print("No tweet")
    channel = client.get_channel(775764541278519304)
    await channel.send("Tweeted")
    

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
        
    # if message.content.startswith('🥫'):
    #     await message.channel.send('meow thank u for can')

    # if message.content.startswith('!'):
    #     await message.channel.send('meow meow I just want can')

client.run(os.environ['DISCORD_TOKEN'])