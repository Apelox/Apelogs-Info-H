import discord
from discord.ext import commands
import yt_dlp as youtube_dl
import asyncio

youtube_dl.utils.bug_reports_message = lambda *args, **kwargs: ''
ytdl_format_options = {
    'format': 'bestaudio/best',
    'noplaylist': False,
    'quiet': True,
}

ffmpeg_options = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
    'options': '-vn',
}

ytdl = youtube_dl.YoutubeDL(ytdl_format_options)

class MusicControlPanel(discord.ui.View):
    def __init__(self, music_cog, ctx):
        super().__init__(timeout=None)
        self.music_cog = music_cog
        self.ctx = ctx

    @discord.ui.button(label="⏸️ Pausar", style=discord.ButtonStyle.primary)
    async def pause_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        vc = self.ctx.voice_client
        if not vc or not vc.is_playing():
            await interaction.response.send_message("n tem nada tocando burro", ephemeral=True)
            return
        vc.pause()
        await interaction.response.send_message("ta pausado")

    @discord.ui.button(label="▶️ Retomar", style=discord.ButtonStyle.success)
    async def resume_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        vc = self.ctx.voice_client
        if not vc or not vc.is_paused():
            await interaction.response.send_message("n tem nada parado burro", ephemeral=True)
            return
        vc.resume()
        await interaction.response.send_message("voltamo")

    @discord.ui.button(label="⏩ Pular", style=discord.ButtonStyle.secondary)
    async def skip_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        vc = self.ctx.voice_client
        if not vc or not vc.is_playing():
            await interaction.response.send_message("n ta tocando nada burro", ephemeral=True)
            return
        vc.stop()
        await interaction.response.send_message("pulei essa bosta")

    @discord.ui.button(label="⏹️ Parar", style=discord.ButtonStyle.danger)
    async def stop_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        vc = self.ctx.voice_client
        if not vc:
            await interaction.response.send_message("n to em call burro", ephemeral=True)
            return
        queue = self.music_cog.get_queue(self.ctx)
        queue.clear()
        vc.stop()
        await interaction.response.send_message("parei essa porra")

class musica(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.queues = {}

    def get_queue(self, ctx):
        if ctx.guild.id not in self.queues:
            self.queues[ctx.guild.id] = []
        return self.queues[ctx.guild.id]

    async def play_music(self, ctx, vc):
        queue = self.get_queue(ctx)
        if len(queue) == 0:
            await ctx.send("acabou as musica")
            await vc.disconnect()
            return

        url = queue.pop(0)
        async with ctx.typing():
            info = await asyncio.get_event_loop().run_in_executor(None, lambda: ytdl.extract_info(url, download=False))
            audio_url = info['url']
            title = info.get('title', 'Música desconhecida')

        def after_playing(error):
            if error:
                print(f"[ERRO] ao tocar música: {error}")
            fut = asyncio.run_coroutine_threadsafe(self.play_music(ctx, vc), self.client.loop)
            try:
                fut.result()
            except Exception as e:
                print(f"[ERRO] ao tocar próxima música: {e}")

        vc.play(discord.FFmpegPCMAudio(audio_url, **ffmpeg_options), after=after_playing)
        await ctx.send(f"Tocando agora: **{title}**")

    @commands.command()
    async def play(self, ctx, *, query: str):
        if not ctx.author.voice:
            await ctx.send("entra na call burro")
            return

        voice_channel = ctx.author.voice.channel
        vc = ctx.voice_client or await voice_channel.connect()

        queue = self.get_queue(ctx)

        if not query.startswith("http://") and not query.startswith("https://"):
            await ctx.send(f"procurando por: **{query}**...")
            try:
                search_result = await asyncio.get_event_loop().run_in_executor(
                    None, lambda: ytdl.extract_info(f"ytsearch:{query}", download=False)
                )
                query = search_result["entries"][0]["webpage_url"]
            except Exception:
                await ctx.send("deu bosta dog, n achei nada")
                return

        queue.append(query)
        view = MusicControlPanel(self, ctx)
        await ctx.send(f"🎶 Adicionado à fila: **{query}**")
        await ctx.send(view=view)

        if not vc.is_playing():
            await self.play_music(ctx, vc)

    @commands.command()
    async def skip(self, ctx):
        vc = ctx.voice_client
        if not vc or not vc.is_playing():
            await ctx.send("Não há nenhuma música tocando para pular.")
            return
        vc.stop()
        await ctx.send("Pulei essa porra ruim")

    @commands.command()
    async def pause(self, ctx):
        vc = ctx.voice_client
        if not vc or not vc.is_playing():
            await ctx.send("Nenhuma música está tocando para pausar.")
            return
        vc.pause()
        await ctx.send("ta pausado")

    @commands.command()
    async def resume(self, ctx):
        vc = ctx.voice_client
        if not vc or not vc.is_paused():
            await ctx.send("Não há música pausada para retomar.")
            return
        vc.resume()
        await ctx.send("voltamo")

    @commands.command()
    async def stop(self, ctx):
        vc = ctx.voice_client
        if not vc:
            await ctx.send("O bot não está conectado a um canal de voz.")
            return
        queue = self.get_queue(ctx)
        queue.clear()
        vc.stop()
        await ctx.send("parei tudo")

    @commands.command()
    async def queue(self, ctx):
        queue = self.get_queue(ctx)
        if len(queue) == 0:
            await ctx.send("A fila está vazia! Adicione músicas com `!play`.")
        else:
            queue_text = "\n".join([f"{i+1}. {url}" for i, url in enumerate(queue)])
            await ctx.send(f"**Fila de músicas:**\n{queue_text}")

    @commands.command()
    async def clearq(self, ctx):
        queue = self.get_queue(ctx)
        queue.clear()
        await ctx.send("❌ A fila de músicas foi limpa.")

async def setup(client):
    await client.add_cog(musica(client))
