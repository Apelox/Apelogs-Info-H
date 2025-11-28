from discord.ext import commands
from discord import app_commands
import discord, requests, random
from PIL import Image, ImageDraw, ImageFont, ImageOps
import io
import textwrap

class Diversao(commands.Cog):
    def __init__(self, client):
        self.client = client
        
    @app_commands.command(name="biscoitinho", description="Receba uma frase inspiradora (ou não) do nosso biscoito da sorte!")
    async def biscoitinho(self, interaction: discord.Interaction):
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
        await interaction.followup.send(embed=embed)

    @app_commands.command(name="apergunta", description="Faça uma pergunta de sim ou não e o oráculo responderá!")
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

    @app_commands.command(name="citacao", description="Cria uma imagem de citação com o avatar e a frase de um usuário.")
    @app_commands.describe(
        usuario="O usuário que será o autor da citação.",
        frase="A frase que você quer eternizar."
    )
    async def citacao(self, interaction: discord.Interaction, usuario: discord.Member, frase: str):
        await interaction.response.defer()

        try:
 
            avatar_bytes = await usuario.display_avatar.read()
            avatar = Image.open(io.BytesIO(avatar_bytes)).convert("RGBA")
            
            img_size = (1024, 512)
            base = Image.new("RGBA", img_size, (0, 0, 0, 0))

            avatar_pb = ImageOps.grayscale(avatar).convert("RGBA")
            avatar_pb.putalpha(70) 
    
            ratio = img_size[1] / avatar_pb.height
            avatar_pb = avatar_pb.resize((int(avatar_pb.width * ratio), img_size[1]), Image.Resampling.LANCZOS)
            
            pos_x = (img_size[0] - avatar_pb.width) // 2
            base.paste(avatar_pb, (pos_x, 0))


            overlay = Image.new("RGBA", img_size, (0, 0, 0, 150))
            base = Image.alpha_composite(base, overlay)

            draw = ImageDraw.Draw(base)

            try:
                quote_font = ImageFont.truetype("utils/Anton-Regular.ttf", size=60)
                author_font = ImageFont.truetype("utils/Anton-Regular.ttf", size=40)
            except IOError:
                quote_font = ImageFont.load_default(size=60)
                author_font = ImageFont.load_default(size=40)

            wrapped_text = textwrap.fill(f"\"{frase}\"", width=30)
            author_text = f"- {usuario.display_name}"

            draw.text((img_size[0]/2, img_size[1]/2), wrapped_text, font=quote_font, anchor="mm", fill=(255, 255, 255), align="center")
            draw.text((img_size[0]/2, img_size[1] - 80), author_text, font=author_font, anchor="ms", fill=(220, 220, 220))
            
            # Salva a imagem em um buffer de memória
            buffer = io.BytesIO()
            base.save(buffer, format="PNG")
            buffer.seek(0)
            
            await interaction.followup.send(file=discord.File(buffer, "citacao.png"))

        except Exception as e:
            print(f"Erro ao criar citação: {e}")
            await interaction.followup.send("❌ Ocorreu um erro ao tentar criar a imagem da citação.")
            
async def setup(client):
    await client.add_cog(Diversao(client))