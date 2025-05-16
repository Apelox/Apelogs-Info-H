from discord.ext import commands
from config.settings import API_WEATHER, API_FILME
import discord
import requests


class Utilidades(commands.Cog):
    def __init__(self, client):
        self.client = client
     
     
    
    #clima    
    @discord.app_commands.command(name="clima", description="Mostra a previsão do tempo de uma cidade.")
    @discord.app_commands.describe(cidade="Nome da cidade para consultar o clima")
    async def slash_clima(self, interaction: discord.Interaction, cidade: str):
        await interaction.response.defer(thinking=True)
        try:
            url = f'http://api.openweathermap.org/data/2.5/weather?q={cidade}&appid={API_WEATHER}&units=metric&lang=pt'
            resposta = requests.get(url).json()

            if resposta['cod'] != 200:
                await interaction.followup.send("❌ Cidade não encontrada.")
                return

            else:
                temp = resposta['main']['temp']
                descricao = resposta['weather'][0]['description']
                umidade = resposta['main']['humidity']
                vento = resposta['wind']['speed']
                cidade_nome = resposta['name']

                embed = discord.Embed(title=f'🌡️ Clima em {cidade_nome}', color=0x1E90FF)
                embed.add_field(name='Temperatura', value=f'{temp}°C', inline=True)
                embed.add_field(name='Condição', value=descricao.capitalize(), inline=True)
                embed.add_field(name='Umidade', value=f'{umidade}%', inline=True)
                embed.add_field(name='Velocidade do vento', value=f'{vento} m/s', inline=True)
                
                await interaction.followup.send(embed=embed)
                
        except Exception as e:
            print(e) 
            await interaction.followup.send("Houve um erro ao tentar obter o clima. Tente novamente mais tarde.")
        
    #filme
    @discord.app_commands.command(name="filme", description="Trás informações sobre algum filme específico. (Também funciona com séries.)")
    @discord.app_commands.describe(titulo="Nome do Filme/Serie")
    async def slash_filme(self, interaction: discord.Interaction, titulo: str):
        await interaction.response.defer(thinking=True)
        try:
            url = f'http://www.omdbapi.com/?t={titulo}&apikey={API_FILME}'
            response = requests.get(url)
            data = response.json()
                
            if data['Response'] == 'True':
                titulo = data.get('Title', 'N/A')
                ano = data.get('Year', 'N/A')
                genero = data.get('Genre', 'N/A')
                sinopse = data.get('Plot', 'N/A')
                imagem = data.get('Poster', None)
                duracao = data.get('Runtime', 'N/A')
                atores = data.get('Actors', 'N/A')
                avaliacoes = data.get('Ratings', [])
                
                embed = discord.Embed(
                    title=titulo,
                    description=sinopse,
                    color=discord.Color.blue()
                )
                
                notas = ""
                for r in avaliacoes:
                    notas += f"**{r['Source']}**: {r['Value']}\n"
                
    
                embed.add_field(name="Duração", value=duracao, inline=True)
                embed.add_field(name="Ano", value=ano, inline=True)
                embed.add_field(name="Gênero", value=genero, inline=False)
                embed.add_field(name="Atores", value=atores, inline=False)
                if notas:
                    embed.add_field(name="📊 Avaliações", value=notas, inline=False)

                if imagem and imagem != "N/A":
                    embed.set_image(url=imagem)
                    
            await interaction.followup.send(embed=embed)
                    
        except Exception as e:
            print(e) 
            await interaction.followup.send("Houve um erro ao tentar obter o filme. Tente novamente mais tarde.")
        
        
        
        

async def setup(client):
    await client.add_cog(Utilidades(client))