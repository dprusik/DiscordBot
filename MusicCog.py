# import datetime
from datetime import datetime
import logging
import asyncio

import discord
from discord.ext import commands
from discord.utils import get
# from youtube_dl import YoutubeDL
from yt_dlp import YoutubeDL
from collections import deque


class MusicCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.is_playing = False
        self.is_paused = False
        self.musicQueue = []
        self.ydl_op = {'format': 'bestaudio/best',
                       'noplaylist': 'True',
                       'postprocessors': [{
                           'key': 'FFmpegExtractAudio',
                           'preferredquality': '1024'}],
                       'playlist_items': '1'
                       }
        self.FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
                               'options': '-vn'}
        self.voice = None
        self.emptymessage = """```Kolejka jest pusta
        musisz polać ziomalu
        ```
        """
        self.audio = None
        self.timestampStart = datetime.now()
        self.currentOffest = None #variable holding current time offset - used in forwarding
        self.playingNow = ""
        self.empty = True

        # bot.loop.create_task(self.player_loop())

    def removeplaylist(self, url):  # helps dealing with &list and &radio when parsing links to videos
        newurl = ""
        tmp = url.find("https://www.youtube.com/watch?v=") != -1
        if tmp != -1:
            stringindex = url.find("&")
            if stringindex != -1:
                newurl = url[:stringindex]
            else:
                newurl = url
        return newurl

    def search_yt(self, item):
        with YoutubeDL(self.ydl_op) as ydl:
            try:
                info = ydl.extract_info("ytsearch:%s" % item, download=False)['entries'][0]
                print(info)
            except Exception:
                dmp = logging.exception("Fuckup")
                # dmp+= info
                return dmp

        return {'source': info['url'], 'title': info['title'], 'org':info['original_url']}

    async def queueEmpty(self, ctx):
        await ctx.send(self.emptymessage)
        self.empty = True

    def playNext(self, ctx):  # same s playMusic but doesn't check for connection
        if len(self.musicQueue) > 0:
            self.empty = False
            self.is_playing = True
            song = self.musicQueue[0][0]

            if not self.voice.is_playing():
                self.musicQueue.pop(0)
                self.currentOffest = None
                self.playingNow = "Teraz leci: " + song["title"] + " " + song['org']
                # asyncio.create_task(ctx.send(self.playingNow))
                self.bot.loop.create_task(ctx.send(self.playingNow))
                self.timestampStart = datetime.now()
                print(self.timestampStart)
                self.audio = song['source']
                self.voice.play(discord.FFmpegOpusAudio(song['source'], **self.FFMPEG_OPTIONS),
                                after=lambda e: self.playNext(ctx))
        else:
            self.is_playing = False
            if not self.empty:
                self.bot.loop.create_task(self.queueEmpty(ctx))

    # main loop control, initial setup of connection and first audio play
    # async def playMusic(self, ctx):
    #     if len(self.musicQueue) > 0:
    #         self.is_playing = True
    #         self.empty = False
    #         song = self.musicQueue[0][0]
    #         if self.voice and self.voice.is_connected:
    #             await self.voice.move_to(self.musicQueue[0][1])
    #         else:
    #             self.voice = await self.musicQueue[0][1].connect(reconnect=True, timeout=1.0, self_deaf=True)
    #             if self.voice is None:
    #                 await ctx.send("Ziomalu musisz być połączony z kanałem żebym mógł grać dla ciebie")
    #                 return
    #         print(f"finished connect to: {self.musicQueue[0][1].id}")
    #         if not self.voice.is_playing():
    #             self.musicQueue.pop(0)
    #             self.playingNow = "Teraz leci: " + song["title"] + " " + song['org']
    #             self.timestampStart = datetime.now()
    #             print(self.timestampStart)
    #             self.audio=song['source']
    #             self.voice.play(discord.FFmpegOpusAudio(song['source'], **self.FFMPEG_OPTIONS),
    #                             after=lambda e: self.playNext(ctx))
    #             await ctx.send(self.playingNow)
    #     else:
    #         self.is_playing = False
            # await self.queueEmpty(ctx)
    async def playMusic(self, ctx):
        if not self.musicQueue:
            self.is_playing = False
            return

        self.is_playing = True

        song, channel = self.musicQueue[0]
        self.musicQueue.pop(0)

        if self.voice and self.voice.is_connected:
            await self.voice.move_to(channel)
        else:
            try:
                self.voice = await channel.connect(reconnect=True, timeout=1.0, self_deaf=True)
            except Exception as e:
                await ctx.send("Ziomalu musisz być połączony z kanałem żebym mógł grać dla ciebie")
                return

        if not self.voice.is_playing():
            self.currentOffest=None
            self.playingNow = f"Teraz leci: {song['title']} {song['org']}"
            self.timestampStart = datetime.now()
            self.currentoffest = None
            print(self.timestampStart)
            self.audio = song['source']
            self.voice.play(discord.FFmpegOpusAudio(song['source'], **self.FFMPEG_OPTIONS),
                            after=lambda e: self.playNext(ctx))
            await ctx.send(self.playingNow)

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        if not member.id == self.bot.user.id:
            return
        elif before.channel is None:
            voice = after.channel.guild.voice_client
            time = 0
            while True:
                await asyncio.sleep(1)
                time = time + 1
                if voice.is_playing() and not voice.is_paused():
                    time = 0
                if time == 180:
                    await voice.disconnect()
                if not voice.is_connected():
                    break

    @commands.command(name="now")
    async def now(self, ctx):
        await ctx.send(self.playingNow)

    @commands.command(name="play", aliases=["p", "playing"], help="Odtwarza wybrany utwór z serwisu YouTube")
    async def play(self, ctx, *params):
        url = " ".join(params)
        try:
            channel = ctx.message.author.voice.channel
        except:
            channel = None
        if channel is None:
            await ctx.reply("Ziomalu musisz być połączony z kanałem żebym mógł grać dla ciebie")
        elif self.is_paused:
            self.voice.resume()
        else:
            self.voice = get(self.bot.voice_clients, guild=ctx.guild)
            yturl = self.removeplaylist(url)
            song = self.search_yt(yturl)
            if song is not None and yturl is not None:
                await ctx.send("Dodano do kolejki: " + song["title"])
                self.musicQueue.append([song, channel])
                if not self.is_playing:
                    await self.playMusic(ctx)
            else:
                await ctx.reply("Musisz dać mi link do YouTube albo hasło do znalezienia mordeczko")

    @commands.command(name='stop')
    async def stop(self, ctx):
        if self.voice and self.voice.is_connected:
            self.is_playing = False
            self.is_paused = False
            await self.voice.disconnect()
            self.musicQueue.clear()


    @commands.command(name='forward', aliases=["f"])
    async def forward(self, ctx, time_str):
        if not self.voice or not self.voice.is_playing():
            return
        # Convert time string to timedelta object
        try:
            forward_time = datetime.strptime(time_str, '%M:%S') - datetime(1900, 1, 1)
        except ValueError:
            await ctx.send("Niepoprawny format czasu! Użyj formatu MM:SS.")
            return
        # Pause the current audio playback and calculate the remaining time to skip to
        timestampend = datetime.now()
        self.voice.pause()
        remaining_time = forward_time + (timestampend - self.timestampStart)
        if self.currentOffest is not None:
            remaining_time += self.currentOffest
        # Create a new audio source with the remaining time skipped
        modified_options = self.FFMPEG_OPTIONS.copy()
        modified_options['before_options'] +=f' -ss {remaining_time.total_seconds()}'
        self.timestampStart=datetime.now()
        #self.audio = self.audio[round(remaining_time.total_seconds() * self.FFMPEG_OPTIONS['before_options'].count('-ss') / 2):]
        self.timestampStart=datetime.now()
        self.currentOffest=remaining_time
        self.voice.play(discord.FFmpegOpusAudio(self.audio, **modified_options), after=lambda e: self.playNext(ctx))

        await ctx.send(f"Przewinąłeś do {remaining_time}.")

    @commands.command(name='skip')
    async def skip(self, ctx):
        if self.voice and self.voice.is_connected:
            self.voice.stop()
            await self.playMusic(ctx)

    @commands.command(name='queue',aliases=["q"])
    async def queue(self, ctx):
        if len(self.musicQueue) == 0:
            await self.queueEmpty(ctx)
        else:
            queuelist = """```
            """
            queuelist += "Aktualna kolejka: \n"

            for i in range(0, len(self.musicQueue)):
                queuelist += str(i + 1) + ". " + self.musicQueue[i][0]['title'] + "\n"
            queuelist += """```
            """
            await ctx.send(queuelist)

    @commands.command(name='pause')
    async def pause(self, ctx):
        if self.is_playing:
            self.is_playing = False
            self.is_paused = True
            self.voice.pause()
        elif self.is_paused:
            self.is_paused = False
            self.is_playing = True
            self.voice.resume()

    # @commands.command(name='remove')
    # async def remove(self, ctx, *params):
    #     try:
    #         self.musicQueue.pop(int(params) - 1)
    #     except ValueError:
    #         await ctx.reply("brak takiego utworu w kolejce")


async def setup(bot):
    await bot.add_cog(MusicCog(bot))
