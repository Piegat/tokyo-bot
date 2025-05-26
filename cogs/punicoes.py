from discord.ext import commands
import discord
import os

class Advertencias(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.cargo_adv = int(os.getenv('CARGO_ADVERTENCIA'))
        self.cargo_adv_grave = int(os.getenv('CARGO_ADVERTENCIA_GRAVE'))
        self.cargo_extra_original = int(os.getenv('CARGO_EXTRA_ORIGINAL'))
        self.cargo_extra_atualizado = int(os.getenv('CARGO_EXTRA_ATUALIZADO'))
        self.canal_log = int(os.getenv('CANAL_LOG_PUNICOES'))

    @commands.command(name='adv')
    async def advertencia(self, ctx, membro: discord.Member, *, motivo: str):
        g = ctx.guild
        canal = g.get_channel(self.canal_log)
        punicao = None
        cargo_final = None

        if g.get_role(self.cargo_adv) in membro.roles:
            await membro.remove_roles(g.get_role(self.cargo_adv))
            await membro.add_roles(g.get_role(self.cargo_adv_grave))
            punicao = g.get_role(self.cargo_adv_grave)

            if g.get_role(self.cargo_extra_original) in membro.roles:
                await membro.remove_roles(g.get_role(self.cargo_extra_original))
                await membro.add_roles(g.get_role(self.cargo_extra_atualizado))
                cargo_final = g.get_role(self.cargo_extra_atualizado)
        else:
            await membro.add_roles(g.get_role(self.cargo_adv))
            punicao = g.get_role(self.cargo_adv)

        await canal.send(
            f"**MEMBRO:** {membro.mention}\n"
            f"**PUNIÇÃO:** {punicao.mention}\n"
            f"**MOTIVO:** {motivo}\n"
            f"**CARGO:** {cargo_final.mention if cargo_final else 'Nenhum cargo alterado'}"
        )

        await ctx.send(f"Advertência registrada para {membro.mention}.")

    @commands.command(name='up')
    async def up(self, ctx, membro: discord.Member, cargo: discord.Role):
        if cargo in membro.roles:
            await membro.remove_roles(cargo)
            await ctx.send(f"{cargo.name} removido de {membro.mention}.")
        else:
            await membro.add_roles(cargo)
            await ctx.send(f"{cargo.name} adicionado a {membro.mention}.")

async def setup(bot):
    await bot.add_cog(Advertencias(bot))
