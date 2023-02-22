import discord
from discord.ext import commands


class HelpCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.help_message = """
```
Komendy dla bota:
!help - wyświetla dostępne komendy
!play <słowa kluczowe>/<link do utworu z yt>- przeszukuje YouTube, a następnie  odtwarza znaleźiony utwór na kanale
!queue - Wyświetla listę utworów w kolejce
!skip - Pomija aktualny utwór
!stop - Wyrzuca bota z kanału
!pause - pausuje aktualny utwór, ponowne użycie wznawia odtwarzanie
!now - wyświetla informacje o aktualnie odtwarzanym utwórze, 
```
"""

        self.text_channel_list = []

    #some debug info so that we know the bot has started
    @commands.Cog.listener()
    async def on_ready(self):
      print("helpCog ready")
        # for guild in self.bot.guilds:
        #     for channel in guild.text_channels:
        #         self.text_channel_list.append(channel)
        #
        # await self.send_to_all(self.help_message)

    @commands.command(name="help", help="Displays all the available commands")
    async def help(self, ctx):
        await ctx.send(self.help_message)

    async def send_to_all(self, msg):
        for text_channel in self.text_channel_list:
            await text_channel.send(msg)


async def setup(bot):
    await bot.add_cog(HelpCog(bot))
    #
