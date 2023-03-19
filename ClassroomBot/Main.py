from __future__ import print_function
import discord
#from discord import app_commands
import os
from os import environ

from dotenv import load_dotenv

import quickstart

import google.auth
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

import os.path

from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow

from discord.ui import Button, Select, View
#from keep_alive import keep_alive

load_dotenv()
token = os.environ["TOKEN"]

intents = discord.Intents.all()

bot = discord.Bot(intents=intents)

commandList = {
    
  "/commands": "Gets command List",
  "/hello": "Says Hello",
  "/authenticate": "Prompts Authentication",
  "/assignments": "Returns an embed of all your assignments (WIP)",
  "/courses": "Returns an embed of all your courses",
  "/classroom": "Sends a link to Google Classroom",
  "/message": "The bot will DM you",
  "/toggledm": "Toggle between DM and channel messages"

}

#say hello
@bot.slash_command(description = commandList["/hello"])
async def hello(ctx):
    def check(c):
      return c.content("hello")
    await ctx.respond(f"Hello {ctx.author.mention}!")

#get list of commands
@bot.slash_command(description = commandList["/commands"])
async def commands(ctx):
    embed = discord.Embed(title = "Help Commands", colour = (discord.Colour.blue()))

    for i, v in commandList.items():
      embed.add_field(name = i, value = v)
    
    await ctx.respond(embed=embed)

# doDM = False
@bot.slash_command(description = commandList["/message"])
async def message(ctx, choice):
  if (choice == "DM"):
    await ctx.author.send("Well hello there!")
    await ctx.respond("Amogus")
  else:
    await ctx.respond(f"You, {ctx.author.mention} are sus")
  
  # DM = bot.create_dm(ctx.author)
  # await DM.send("Hi")

# @bot.slash_command(description = commandList["/toggledm"])
# async def toggledm(ctx):
#    doDM = not doDM
#    await ctx.respond(f"Set DM Toggle to {doDM}")
   

#authenticate google account
@bot.slash_command(description = commandList["/authenticate"])
async def authenticate(ctx):
  if os.path.exists("token.json"):
    os.remove("token.json")

  await ctx.respond(f"Please paste your authentication code in channel. The link will expire in 5 minutes")

  # flow = InstalledAppFlow.from_client_secrets_file(
  #               'credentials.json', quickstart.getScopes())
  
  # creds = flow.run_local_server(port=0)

  flow = Flow.from_client_secrets_file(
                'credentials.json', quickstart.getScopes(),
                redirect_uri='urn:ietf:wg:oauth:2.0:oob')

  auth_url, _ = flow.authorization_url(time = 300, prompt='consent')

  await ctx.respond(f"Please go to this URL: {auth_url}")

  def check(m):
    return m.author == ctx.author and m.channel == ctx.channel
  
  
  code = (await bot.wait_for("message", check=check)).content
  print(code)
  
  try:
    flow.fetch_token(code=code)
    creds = flow.credentials
  except:
     await ctx.respond(f"Authentication Failed, please try again.")
  else:
    if creds:
      await ctx.send(f"Authentication successful {ctx.author.mention}")
      with open('token.json', 'w') as token:
            token.write(creds.to_json())

      try:
        service = build('classroom', 'v1', credentials=creds, static_discovery = False)

      except HttpError as error:
        print('An error occurred: %s' % error)
    else:
      await ctx.send(f"Authentication unsuccessful {ctx.author.mention}")

#get courses
@bot.slash_command(description = commandList["/courses"])
async def courses(ctx):
  embed = discord.Embed(title = "Courses")

  creds = quickstart.main()
  try:
      service = build('classroom', 'v1', credentials=creds, static_discovery = False)
      courses = []
      page_token = None

      while True:
          response = service.courses().list(pageToken=page_token,
                                              pageSize=100).execute()
          courses.extend(response.get('courses', []))
          page_token = response.get('nextPageToken', None)
          if not page_token:
              break

      if not courses:
          await ctx.respond("No Courses found.")
          return
      for course in courses:
          embed.add_field(name = f"{course.get('name')}", value = f"Course ID: {course.get('id')}")
  except HttpError as error:
      await ctx.respond(f"An error occured: {error}")
      
      return error
  
  await ctx.respond(embed=embed)  

#get assignments
@bot.slash_command(description = commandList["/assignments"])
async def assignments(ctx):
  embed = discord.Embed(title = "Assignments")
  creds = quickstart.main()
  try:
      service = build('classroom', 'v1', credentials=creds, static_discovery = False)
      courses = []
      page_token = None

      while True:
        response = service.courses().list(pageToken=page_token,
                                              pageSize=100).execute()
        courses.extend(response.get('courses', []))
        page_token = response.get('nextPageToken', None)
        if not page_token:
          break


      if not courses:
        await ctx.respond("No Assignments found.")
      for cNum in courses:
          coursework = service.courses().courseWork().list(courseId = cNum.get('id'))
          if not coursework:
            await ctx.respond("No Assignments found.")

          for course in coursework:
            embed.add_field(name = f"{course.get('name')}")   

  except HttpError as error:
      await ctx.respond(f"An error occured: {error}")
      
      return error
  
  await ctx.respond(embed=embed) 

@bot.slash_command(description = commandList["/classroom"])
async def classroom(ctx):
    await ctx.respond(f"https://www.classroom.google.com")

#run 
bot.run(token)
bot.respond("started!")

  
  # flow = Flow.from_client_secrets_file(
  #               'credentials.json', quickstart.getScopes(),
  #               redirect_uri='urn:ietf:wg:oauth:2.0:oob')

  # auth_url, _ = flow.authorization_url(prompt='consent')

  # await ctx.respond(f"Please go to this URL: {auth_url}")

  # def check(m):
  #   return m.author == ctx.author
  
  # code = await bot.wait_for("message", check=check)
  
  # flow.fetch_token(code=code)
  # creds = flow.credentials

# @bot.slash_command()
# async def getwebsite(ctx):
#   #await ctx.respond("Is your grade above or below 65?")
#   #def check(m):
#     #return m.author == ctx.author and m.message == "below"
#   #bot.wait_for("below", check=check)
#   embed = discord.Embed(title="Website: ", description= "")
#   embed.add_field(name="https://TestTakingTips.presidentshrubb.repl.co", value=" ", inline=True)
#   await ctx.respond(f" Good luck {ctx.author.mention}")
#   await ctx.respond(embed = embed)

# @bot.slash_command()
# async def getscores(ctx):
#   embed = discord.Embed(title = "Test Scores")
#   await ctx.respond(embed=embed)

# #@bot.slash_command()
# #async def check(ctx):
#     #name = name or ctx.author.name
#     #await ctx.respond(f"{ctx.author.mention}, what would you like me to check for? Test Scores(1) or Missing Assignments(2)?")

#     #answer = input('Please choose either Scores(1) or Assignments(2): ')
#     #if answer == "1":
#         #print('This command is not online yet.')
#     #else:
#         #print('This command is not online yet. Wait 3 hours.')