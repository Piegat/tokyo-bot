import discord
mensagem_metas_atrasadas_id = None

async def atualizar_lista_metas_atrasadas(guild, canal_id, role_id):
    global mensagem_metas_atrasadas_id

    canal = guild.get_channel(canal_id)
    if canal is None:
        return

    membros = [m.mention for m in guild.members if discord.utils.get(m.roles, id=role_id)]
    embed = discord.Embed(title="Metas pendentes!", color=discord.Color.blue())
    embed.add_field(name="Membros:", value="\n".join(membros) if membros else "Nenhum", inline=False)

    try:
        if mensagem_metas_atrasadas_id:
            msg = await canal.fetch_message(mensagem_metas_atrasadas_id)
            await msg.edit(embed=embed)
        else:
            msg = await canal.send(embed=embed)
            mensagem_metas_atrasadas_id = msg.id
    except discord.NotFound:
        msg = await canal.send(embed=embed)
        mensagem_metas_atrasadas_id = msg.id
