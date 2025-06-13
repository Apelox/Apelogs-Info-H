from discord.ext import commands
from discord import app_commands
import discord
import requests

class Animais(commands.Cog):
    def __init__(self, client):
        self.client = client
        
    async def get_animal_data(self, endpoint):
        try:
            img_url = f"https://some-random-api.com/img{endpoint}"
            
            r_img = requests.get(img_url)
            r_img.raise_for_status()
            img_json = r_img.json()
            return img_json.get("link")

        except requests.RequestException as e:
            print(f"Erro ao buscar dados do endpoint {endpoint}: {e}")
            return None

    @app_commands.command(name="animal", description="Envia a foto de um animal fofo aleatório!")
    @app_commands.describe(tipo="Escolha o animal que você quer ver!")
    @app_commands.choices(tipo=[
        app_commands.Choice(name="Cachorro 🐶", value="/dog"),
        app_commands.Choice(name="Gato 🐱", value="/cat"),
        app_commands.Choice(name="Raposa 🦊", value="/fox"),
        app_commands.Choice(name="Panda 🐼", value="/panda"),
        app_commands.Choice(name="Panda Vermelho 🍁", value="/red_panda"),
        app_commands.Choice(name="Guaxinim 🦝", value="/racoon"),
        app_commands.Choice(name="Coala 🐨", value="/koala"),
        app_commands.Choice(name="Canguru 🦘", value="/kangaroo"),
        app_commands.Choice(name="Baleia 🐋", value="/whale"),
        app_commands.Choice(name="Pássaro 🐦", value="/bird"),
    ])
    async def animal(self, interaction: discord.Interaction, tipo: app_commands.Choice[str]):
        await interaction.response.defer(thinking=True)
        animal_name = tipo.name
        endpoint = tipo.value
        
        image_url = await self.get_animal_data(endpoint)
        
        if image_url:
            embed = discord.Embed(
                title=f"Um {animal_name} para você!",
                color=discord.Color.random()
            )
            embed.set_image(url=image_url)
            await interaction.followup.send(embed=embed)
        else:
            await interaction.followup.send(f"❌ Desculpe, não consegui encontrar uma imagem de **{animal_name}** no momento.")

async def setup(client):
    await client.add_cog(Animais(client))