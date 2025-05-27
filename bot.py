import discord
from discord.ext import commands
from dotenv import load_dotenv
import os
import asyncio

load_dotenv()

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'Bot conectado como {bot.user}')

initial_extensions = [
    'cogs.metas',
    'cogs.punicoes',
    'cogs.sistema',
    'cogs.liders',
]
from discord.ext import commands

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        await ctx.send("⚠️ Comando não encontrado.")
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("⚠️ Você esqueceu de algum argumento obrigatório.")
    elif isinstance(error, commands.CheckFailure):
        await ctx.send("❌ Você não tem permissão para usar esse comando.")
    else:
        await ctx.send(f"❌ Ocorreu um erro inesperado:\n```{error}```")
        print(f"Erro no comando {ctx.command}: {error}")

async def main():
    for extension in initial_extensions:
        try:
            await bot.load_extension(extension)
            print(f"[OK] Cog carregado: {extension}")
        except Exception as e:
            print(f"[ERRO] Falha ao carregar {extension}: {e}")

    await bot.start(os.getenv('BOT_TOKEN'))

if __name__ == '__main__':
    asyncio.run(main())
