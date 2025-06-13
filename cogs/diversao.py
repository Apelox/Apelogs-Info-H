from discord.ext import commands
import discord, requests, random

class Diversao(commands.Cog):
    def __init__(self, client):
        self.client = client
        
    @discord.app_commands.command(name="biscoitinho", description="Receba uma frase inspiradora (ou não) do nosso biscoito da sorte!")
    async def biscoito_da_sorte(self, interaction: discord.Interaction):
        await interaction.response.defer()
        with open("data/frases.txt", "r", encoding="utf-8") as f:
                frases = f.read().splitlines()
        if not frases:
            await interaction.followup.send("Meu oráculo está silencioso... O arquivo de frases está vazio.")
            return
        
        escolha = random.choice(frases)
        embed = discord.Embed(
            title="🥠 Biscoito da Sorte",
            description=f"**Sua sorte de hoje é:**\n\n> {escolha}",
            color=discord.Color.random()
        )
        await interaction.response.send_message(embed=embed)

    @discord.app_commands.command(name="apergunta", description="Faça uma pergunta de sim ou não e o oráculo responderá!")
    async def apergunta(self, interaction: discord.Interaction, duvida: str):

        await interaction.response.defer()
        with open("data/respostas.txt", "r", encoding="utf-8") as f:
                respostas = f.read().splitlines()
        if not respostas:
            await interaction.followup.send("Meu oráculo está silencioso... O arquivo de respostas está vazio.")
            return

        resposta_escolhida = random.choice(respostas)
        mensagem_final = (
            f"🔮{resposta_escolhida}"
            )
        await interaction.followup.send(mensagem_final)
        
            
async def setup(client):
    await client.add_cog(Diversao(client))