from discord.ext import commands
import discord

def verify_perm(membro: discord.Member):
    if membro.guild_permissions.administrator:
        return True
    if membro.roles:
        for cargo in membro.roles:
            if cargo.name.lower() in ['00', 'líder', 'vice-líder']:
                return True
    return False

class Liders(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='hierarquia')
    async def hierarquia(self, ctx):
        membro = ctx.author
        if not verify_perm(membro):
            await ctx.send("Você não tem permissão para usar este comando.")
            return

        embed = discord.Embed(
            title="🌟 Hierarquia do Servidor 🌟",
            description="Confira a hierarquia da Tokyo!",
            color=discord.Color.purple()
        )

        ignorar_roles = ["bot", "amigos", "blacklist", "aguardando recrutamento", "nekotina", "musica", "loritta", "tokyo", "testing"]
        cargo_dict = {}

        for member in ctx.guild.members:
            top_roles = [role for role in member.roles if role.name.lower() != "@everyone" and role.name.lower() not in ignorar_roles]
            if not top_roles:
                continue
            top_role = max(top_roles, key=lambda r: r.position)
            cargo_dict.setdefault(top_role, []).append(member.mention)

        sorted_roles = sorted(cargo_dict.items(), key=lambda x: x[0].position, reverse=True)

        for role, members in sorted_roles:
            membros_formatados = "\n".join(members)
            embed.add_field(
                name=f"🛡️ {role.name}",
                value=f"{membros_formatados}",
                inline=False
            )

        await ctx.send(embed=embed)

    @commands.command(name='ping')
    async def test(self, ctx):
        await ctx.reply("pong!")

async def setup(bot):
    await bot.add_cog(Liders(bot))
