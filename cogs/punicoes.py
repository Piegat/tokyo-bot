from discord.ext import commands
import discord
import os

class Advertencias(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.cargo_adv = int(os.getenv('CARGO_ADVERTENCIA'))
        self.cargo_adv_grave = int(os.getenv('CARGO_ADVERTENCIA_GRAVE'))
        self.cargo_extra_original = int(os.getenv('CARGO_MEMBRO'))
        self.cargo_extra_atualizado = int(os.getenv('CARGO_AVIAO'))
        self.canal_log = int(os.getenv('CANAL_LOG_PUNICOES'))
        self.canal_pd = int(os.getenv('CANAL_PD'))

    @commands.command(name='adv')
    async def advertencia(self, ctx, membro: discord.Member, *, motivo: str):
        g = ctx.guild
        canal = g.get_channel(self.canal_log)

        cargo_adv = g.get_role(self.cargo_adv)
        cargo_adv_grave = g.get_role(self.cargo_adv_grave)
        cargo_extra_original = g.get_role(self.cargo_extra_original)
        cargo_extra_atualizado = g.get_role(self.cargo_extra_atualizado)

        punicao = None
        cargo_final = None

        # Se já tem advertência leve, aplica grave
        if cargo_adv in membro.roles:
            await membro.remove_roles(cargo_adv)
            await membro.add_roles(cargo_adv_grave)
            punicao = cargo_adv_grave

            if cargo_extra_original in membro.roles:
                await membro.remove_roles(cargo_extra_original)
                await membro.add_roles(cargo_extra_atualizado)
                cargo_final = cargo_extra_atualizado
        else:
            # Aplica advertência leve
            await membro.add_roles(cargo_adv)
            punicao = cargo_adv

        # Embed de log
        embed = discord.Embed(
            title="📕 Advertência Aplicada",
            color=discord.Color.orange()
        )
        embed.add_field(name="👤 Membro", value=membro.mention, inline=False)
        embed.add_field(name="⚠️ Punição", value=punicao.mention, inline=False)
        embed.add_field(name="📄 Motivo", value=motivo, inline=False)
        embed.add_field(name="🛠 Cargo Extra", value=cargo_final.mention if cargo_final else "Nenhum cargo alterado", inline=False)
        embed.set_footer(text=f"Ação por {ctx.author}", icon_url=ctx.author.display_avatar.url)

        await canal.send(embed=embed)
        await ctx.send(f"✅ Advertência registrada para {membro.mention}.")


    @commands.command(name='up')
    async def up(self, ctx, membro: discord.Member, cargo: discord.Role):
        if cargo in membro.roles:
            await membro.remove_roles(cargo)
            await ctx.send(f"{cargo.name} removido de {membro.mention}.")
        else:
            await membro.add_roles(cargo)
            await ctx.send(f"{cargo.name} adicionado a {membro.mention}.")

    @commands.command(name="pd")
    async def pd(self, ctx, membro: discord.Member, *, motivo: str):
        cargos_permitidos = [
            "gerente de ação", 
            "gerente de recrutamento", 
            "supervisor", 
            "vice-líder", 
            "líder", 
            "00"
        ]

        if not any(role.name.lower() in cargos_permitidos for role in ctx.author.roles):
            await ctx.send("❌ Você não tem permissão para usar este comando.")
            return

        g = ctx.guild
        canal = g.get_channel(self.canal_pd)

        try:
            await membro.kick(reason=motivo)
        except discord.Forbidden:
            await ctx.send("❌ Não tenho permissão para expulsar esse membro.")
            return
        except Exception as e:
            await ctx.send(f"❌ Ocorreu um erro ao expulsar: {e}")
            return

        embed = discord.Embed(
            title="Remoção 💀",
            color=discord.Color.red()
        )
        embed.add_field(name="👤 Membro", value=membro.mention, inline=False)
        embed.add_field(name="📄 Motivo", value=motivo, inline=False)
        embed.add_field(name="👮‍♂️ Por", value=ctx.author.mention, inline=False)

        await canal.send(embed=embed)
        await ctx.send(f"Membro removido {membro.mention}.")



async def setup(bot):
    await bot.add_cog(Advertencias(bot))
