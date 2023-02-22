import asyncio
import datetime
import discord
import os
from discord.ext import commands
import logging
from MusicCog import MusicCog
from HelpCog import HelpCog

TOKEN='MTA2MDkzMjU2MzgwOTU5OTQ5OA.GpnHld.qSYgPsurqM_IOaQM-nhCxbBQyKwBqCgI3zXInc'
#TOKEN = 'MTA3MDQzNDUwODc1MjU1NjEwMg.GlVgbA.wl3n4uGH1jERtCxIGzXTjJW1j4d7O4jaLsCBrU'
intents = discord.Intents.default()
intents.message_content = True

client = commands.Bot(command_prefix='y!', intents=intents)


# FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',  'options': '-vn'}
#
# music_queue = []


async def setup(client):
    client.remove_command('skip')
    await client.load_extension("MusicCog")
    client.remove_command('help')

    await client.load_extension("HelpCog")
    print('cogs ready')


async def main():
    async with client:
        await setup(client)
        await client.start(TOKEN)


@client.event
async def on_ready():
    print('bot ready')
    await client.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name='y!help'))
    #await setup(client)
    commands = MusicCog.get_commands(MusicCog)
    print([c.name for c in commands])


# @client.command()
# async def play(ctx, url):
#     global voice
#     channel = ctx.message.author.voice.channel
#     print(url)
#     voice = get(client.voice_clients, guild=ctx.guild)
#     if voice and voice.is_connected:
#         await voice.move_to(channel)
#     else:
#         voice = await channel.connect(reconnect=True, timeout=1.0, self_deaf=True)
#     print(f"finished connect to: {channel.id}")
#
#     ydl_op = {
#         'format': 'bestaudio/best',
#         'postprocessors': [{
#             'key': 'FFmpegExtractAudio',
#             'preferredcodec': 'm4a',
#             'preferredquality': '1024'
#         }]
#     }
#     ydl_op2 ={'format': 'bestaudio/best',
#               'noplaylist': 'True',
#               'postprocessors': [{
#                   'key': 'FFmpegExtractAudio',
#                   'preferredcodec': 'm4a',
#                   'preferredquality': '1024'
#               }]
#               }
#
#     song=search_yt(url, ydl_op2)
#     music_queue.append([song, channel])
#     voice.play(discord.FFmpegOpusAudio(song["source"], **FFMPEG_OPTIONS))
#     voice.source.volume = 0.7
#     await ctx.send("Teraz leci " + song["title"])


#


# @client.command(name='stop')
# async def stop(ctx):
#     if voice and voice.is_connected:
#         await voice.disconnect()


# @client.command(name='skip')
# async def skip(ctx):
#     if voice and voice.is_connected:
#         voice.stop()


@client.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandInvokeError):
        await ctx.reply(f"Wyjebało się xD")
        embed = discord.Embed(title=':x: Command Error', colour=0x992d22)  # Dark Red
        embed.add_field(name='Error', value=error)
        embed.add_field(name='Guild', value=ctx.guild)
        embed.add_field(name='Channel', value=ctx.channel)
        embed.add_field(name='User', value=ctx.author)
        embed.add_field(name='Message', value=ctx.message.clean_content)
        embed.timestamp = datetime.datetime.utcnow()
        try:
            print(embed.fields)
            print('logs send')
        except Exception:
            dmp = logging.exception("Fuckup")
            print(embed.error)
            pass
    else:
        raise error

asyncio.run(main())




