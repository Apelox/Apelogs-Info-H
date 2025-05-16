from discord.ext import commands
import discord
import requests


class Animais(commands.Cog):
    def __init__(self, client):
        self.client = client
        
    async def animal_image(self, endpoint):
        try:
            url = f"https://some-random-api.com{endpoint}"
            r = requests.get(url)
            r.raise_for_status()
            res = r.json()
            return res.get("image") or res.get("link") or res.get("message") 
        except Exception as e:
            print(f"Erro ao buscar {endpoint}: {e}")
            return None

    @discord.app_commands.command(name="dog", description="Envia a foto de um cachorro fofo aleatório :D")
    async def slash_dog(self, interaction: discord.Interaction):
        await interaction.response.defer(thinking=True)
        url = await self.animal_image("/animal/dog")
        await interaction.followup.send(content=url or "Não consegui encontrar um doguinho :(")

    @discord.app_commands.command(name="cat", description="Envia a foto de um gato fofo aleatório :3")
    async def slash_cat(self, interaction: discord.Interaction):
        await interaction.response.defer(thinking=True)
        url = await self.animal_image("/animal/cat")
        await interaction.followup.send(content=url or "Não consegui encontrar um gatinho :(")

    @discord.app_commands.command(name="fox", description="Envia a imagem de uma raposa aleatória 🦊")
    async def slash_fox(self, interaction: discord.Interaction):
        await interaction.response.defer(thinking=True)
        url = await self.animal_image("/animal/fox")
        await interaction.followup.send(content=url or "Não consegui encontrar uma raposa :(")

    @discord.app_commands.command(name="panda", description="Envia a imagem de um panda fofo 🐼")
    async def slash_panda(self, interaction: discord.Interaction):
        await interaction.response.defer(thinking=True)
        url = await self.animal_image("/animal/panda")
        await interaction.followup.send(content=url or "Não consegui encontrar um panda :(")

    @discord.app_commands.command(name="redpanda", description="Envia a imagem de um panda vermelho 🍁")
    async def slash_red_panda(self, interaction: discord.Interaction):
        await interaction.response.defer(thinking=True)
        url = await self.animal_image("/animal/red_panda")
        await interaction.followup.send(content=url or "Não consegui encontrar um red panda :(")

    @discord.app_commands.command(name="guaxinim", description="Envia a imagem de um guaxinim 🦝")
    async def slash_racoon(self, interaction: discord.Interaction):
        await interaction.response.defer(thinking=True)
        url = await self.animal_image("/animal/racoon")
        await interaction.followup.send(content=url or "Não consegui encontrar um guaxinim :(")

    @discord.app_commands.command(name="coala", description="Envia a imagem de um coala 🐨")
    async def slash_koala(self, interaction: discord.Interaction):
        await interaction.response.defer(thinking=True)
        url = await self.animal_image("/animal/koala")
        await interaction.followup.send(content=url or "Não consegui encontrar um coala :(")

    @discord.app_commands.command(name="canguru", description="Envia a imagem de um canguru 🦘")
    async def slash_kangaroo(self, interaction: discord.Interaction):
        await interaction.response.defer(thinking=True)
        url = await self.animal_image("/animal/kangaroo")
        await interaction.followup.send(content=url or "Não consegui encontrar um canguru :(")

    @discord.app_commands.command(name="baleia", description="Envia a imagem de uma baleia 🐋")
    async def slash_whale(self, interaction: discord.Interaction):
        await interaction.response.defer(thinking=True)
        url = await self.animal_image("/animal/whale")
        await interaction.followup.send(content=url or "Não consegui encontrar uma baleia :(")

    @discord.app_commands.command(name="bird", description="Envia a imagem de um pássaro 🐤")
    async def slash_bird(self, interaction: discord.Interaction):
        await interaction.response.defer(thinking=True)
        url = await self.animal_image("/animal/bird")
        await interaction.followup.send(content=url or "Não consegui encontrar um pássaro :(")

async def setup(client):
    await client.add_cog(Animais(client))