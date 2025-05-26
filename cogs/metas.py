from discord.ext import commands
import discord
import os

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
        g = ctx.guild
        membros_paga = [m.mention for m in g.get_role(self.cargo_meta_paga).members]
        membros_pendente = [m.mention for m in g.get_role(self.cargo_meta_pendente).members]
        membros_atrasada = [m.mention for m in g.get_role(self.cargo_meta_atrasada).members]

        await ctx.send(
            f"**Meta Paga:** {', '.join(membros_paga) or 'Nenhum'}\n"
            f"**Meta Pendente:** {', '.join(membros_pendente) or 'Nenhum'}\n"
            f"**Meta Atrasada:** {', '.join(membros_atrasada) or 'Nenhum'}"
        )

    @commands.command(name='relatorio')
    async def relatorio(self, ctx):
        canal = ctx.guild.get_channel(self.canal_metas_atrasadas)
        membros_atrasada = [m.mention for m in ctx.guild.get_role(self.cargo_meta_atrasada).members]
        await canal.send(f"**Usuários com meta atrasada:** {', '.join(membros_atrasada) or 'Nenhum'}")
        await ctx.send("Relatório enviado.")

async def setup(bot):
    await bot.add_cog(Metas(bot))
