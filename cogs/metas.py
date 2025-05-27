from discord.ext import commands
import discord
from utils.metas_utils import atualizar_lista_metas_atrasadas

import os
META_PAGA = os.getenv('CARGO_META_PAGA')
ROLE_META_PENDENTE = os.getenv('CARGO_META_PENDENTE')
ROLE_META_ATRASADA = os.getenv('CARGO_META_ATRASADA')
CANAL_METAS_ATRASADAS = os.getenv('CANAL_METAS_ATRASADAS')
            
class Metas(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.cargo_meta_paga = int(os.getenv('CARGO_META_PAGA'))
        self.cargo_meta_pendente = int(os.getenv('CARGO_META_PENDENTE'))
        self.cargo_meta_atrasada = int(os.getenv('CARGO_META_ATRASADA'))
        self.canal_metas_atrasadas = int(os.getenv('CANAL_METAS_ATRASADAS'))

    @commands.command(name='meta')
    async def meta(self, ctx, membro: discord.Member):
        await membro.add_roles(ctx.guild.get_role(self.cargo_meta_paga))
        await membro.remove_roles(
            ctx.guild.get_role(self.cargo_meta_pendente),
            ctx.guild.get_role(self.cargo_meta_atrasada)
        )
        await ctx.send(f"{membro.mention} marcou a meta como paga.")

    @commands.command(name='pagarAtrasada')
    async def pagar_atrasada(self, ctx, membro: discord.Member):
        await membro.add_roles(ctx.guild.get_role(self.cargo_meta_pendente))
        await membro.remove_roles(ctx.guild.get_role(self.cargo_meta_atrasada))
        await ctx.send(f"{membro.mention} pagou a meta atrasada.")

    @commands.command(name='listar')
    async def listar(self, ctx):
        role_paga = ctx.guild.get_role(self.cargo_meta_paga)
        role_pendente = ctx.guild.get_role(self.cargo_meta_pendente)
        role_atrasada = ctx.guild.get_role(self.canal_metas_atrasadas)

        membros_pagos = [m.mention for m in ctx.guild.members if role_paga in m.roles]
        membros_pendentes = [m.mention for m in ctx.guild.members if role_pendente in m.roles]
        membros_atrasados = [m.mention for m in ctx.guild.members if role_atrasada in m.roles]

        embed = discord.Embed(title="Status das Metas Semanais", color=discord.Color.blue())
        embed.add_field(name="Meta Paga", value="\n".join(membros_pagos) if membros_pagos else "Nenhum", inline=False)
        embed.add_field(name="Meta Pendente", value="\n".join(membros_pendentes) if membros_pendentes else "Nenhum", inline=False)
        embed.add_field(name="Meta Atrasada", value="\n".join(membros_atrasados) if membros_atrasados else "Nenhum", inline=False)

        await ctx.send(embed=embed)


    @commands.command(name='relatorio')
    async def relatorio(self, ctx):
        await atualizar_lista_metas_atrasadas(ctx.guild, self.canal_metas_atrasadas, self.cargo_meta_atrasada)
        await ctx.send("Relatório atualizado no canal de metas.")
    

async def setup(bot):
    await bot.add_cog(Metas(bot))
