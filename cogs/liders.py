from discord.ext import commands
import discord
import os

class Liders(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

def verify_perm(membro: discord.Member):
    if membro.guild_permissions.administrator:
        return True
    if membro.roles:
        for cargo in membro.roles:
            if cargo.name.lower() in ['00', 'líder', 'vice-líder']:
                return True
            
@commands.command(name='hierarquia')
async def hierarquia(ctx):
    membro = ctx.author
    if not verify_perm(membro):
        await ctx.send("Você não tem permissão para usar este comando.")
        return

    embed = discord.Embed(
        title="Hierarquia do Servidor",
        description="Aqui está a hierarquia do servidor:",
        color=discord.Color.blue()
    )
    
    embed.add_field(name="Líder", value="@Líder", inline=False)
    embed.add_field(name="Vice-Líder", value="@Vice-Líder", inline=False)

    await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Liders(bot))
