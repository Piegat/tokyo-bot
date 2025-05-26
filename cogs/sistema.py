from discord.ext import commands
from datetime import datetime, timedelta

class Sistema(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='proximaMeta')
    async def proxima_reset(self, ctx):
        agora = datetime.now()
        dias_ate_domingo = (6 - agora.weekday()) % 7
        proximo = agora + timedelta(days=dias_ate_domingo)
        reset = proximo.replace(hour=23, minute=59, second=0, microsecond=0)
        tempo = reset - agora
        dias = tempo.days
        horas, resto = divmod(tempo.seconds, 3600)
        minutos = resto // 60

        await ctx.send(f"Próximo reset em {dias} dias, {horas} horas e {minutos} minutos.")

    @commands.command(name='comandos')
    async def comandos(self, ctx):
        await ctx.send("""
            **Lista de Comandos**

            `!meta @user` – Marca a meta como paga  
            `!pagarAtrasada @user` – Marca que pagou a meta da semana passada  
            `!listar` – Lista quem pagou, não pagou ou está atrasado  
            `!relatorio` – Atualiza a lista de atrasados no canal de metas  
            `!proximaMeta` – Tempo até o próximo reset  
            `!adv @user "motivo"` – Aplica advertência ao usuário  
            `!up @user @cargo` – Adiciona ou remove cargo de alguém  
            `!comandos` – Lista todos os comandos
            """)

async def setup(bot):
    await bot.add_cog(Sistema(bot))
