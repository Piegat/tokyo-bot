import os
from discord.ext import commands
from discord import Embed, ButtonStyle, Interaction, ui, Color, Member, TextChannel, Message # Adicionado Message
import discord

# Constants
EMPTY_SLOT_TEXT = "`(Vaga disponível)`"
MAX_RESERVAS = 3
CARGOS_PERMITIDOS_ESCALACAO = ["gerente de ação", "supervisor", "vice-líder", "líder", "00"] # Definido globalmente no módulo ou como atributo da classe

class EscalacaoView(ui.View):
    def __init__(self, max_participantes: int, message_id: int):
        super().__init__(timeout=None) # View persistente até o reinício do bot
        self.max_participantes = max_participantes
        self.message_id = message_id # Guardamos para referência, se necessário
        self.participantes_slots = [EMPTY_SLOT_TEXT for _ in range(max_participantes)]
        self.reservas = []
        self.inscritos = set() # Guarda user.mention

    async def _internal_update_embed_content(self, original_embed: Embed) -> Embed:
        """Prepara o novo conteúdo do embed baseado no estado atual da view."""
        participantes_txt = "\n".join(f"{i+1}: {slot}" for i, slot in enumerate(self.participantes_slots))
        vagas_disponiveis = self.participantes_slots.count(EMPTY_SLOT_TEXT)
        
        texto_final = f"**Lista de Participantes:**\n{participantes_txt}"
        texto_final += f"\n\n**Vagas restantes:** {vagas_disponiveis}/{self.max_participantes}"
        
        if self.reservas:
            reservas_txt = "\n".join(f"Reserva {i+1}: {m}" for i, m in enumerate(self.reservas))
            texto_final += f"\n-----\n**Reservas (Máx: {MAX_RESERVAS}):**\n{reservas_txt}"
        else:
            texto_final += f"\n-----\n**Reservas (Máx: {MAX_RESERVAS}):**\n`(Nenhum reserva)`"
            
        new_embed = original_embed.copy()
        new_embed.description = texto_final
        return new_embed

    async def refresh_message_embed(self, message_to_edit: Message):
        """Atualiza a mensagem com o estado atual da view. Chamado pelo comando !remover."""
        if not message_to_edit.embeds:
            print(f"Error: Message {message_to_edit.id} has no embeds to update from command.")
            return False 

        original_embed = message_to_edit.embeds[0]
        new_embed = await self._internal_update_embed_content(original_embed)
        
        try:
            await message_to_edit.edit(embed=new_embed, view=self) # self é a instância da view
            return True
        except discord.HTTPException as e:
            print(f"Error editing message {message_to_edit.id} from command: {e}")
            return False

    async def _update_embed_from_interaction(self, interaction: Interaction):
        """Atualiza o embed a partir de uma interação de botão."""
        if not interaction.message or not interaction.message.embeds:
            return

        original_embed = interaction.message.embeds[0]
        new_embed = await self._internal_update_embed_content(original_embed)
        
        try:
            await interaction.message.edit(embed=new_embed, view=self)
        except discord.HTTPException as e: # discord.NotFound, discord.Forbidden são subclasses
            print(f"Error updating embed from interaction on message {interaction.message.id}: {e}")

    @ui.button(label="Participar", style=ButtonStyle.green, custom_id="escalacao_participar_v2") # custom_id opcional mas bom para depuração
    async def participar(self, interaction: Interaction, button: ui.Button):
        user = interaction.user
        user_mention = user.mention

        if user_mention in self.inscritos:
            await interaction.response.send_message("✔️ Você já está na lista!", ephemeral=True)
            return

        try:
            slot_index = self.participantes_slots.index(EMPTY_SLOT_TEXT)
            self.participantes_slots[slot_index] = user_mention
            self.inscritos.add(user_mention)
            await self._update_embed_from_interaction(interaction)
            await interaction.response.send_message("✅ Você foi adicionado à lista de participantes!", ephemeral=True)
        except ValueError: 
            if len(self.reservas) < MAX_RESERVAS:
                self.reservas.append(user_mention)
                self.inscritos.add(user_mention)
                await self._update_embed_from_interaction(interaction)
                await interaction.response.send_message("👍 Você foi adicionado à lista de reservas!", ephemeral=True)
            else:
                await interaction.response.send_message("🚫 Todas as vagas, incluindo reservas, estão preenchidas.", ephemeral=True)

    # O botão "Sair" foi removido.

class Escalacao(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot = bot
        # Guarda as views ativas para que o comando !remover possa encontrá-las
        # A chave é o ID da mensagem da escalação, o valor é a instância da EscalacaoView
        self.active_views = {} 

    @commands.command(name="escalacao")
    async def cmd_escalacao(self, ctx: commands.Context): # Renomeado para evitar conflito de nome com a classe
        if not any(role.name.lower() in CARGOS_PERMITIDOS_ESCALACAO for role in ctx.author.roles):
            await ctx.send("❌ Você não tem permissão para usar este comando.")
            return

        target_channel = None
        canal_escalacao_id_str = os.getenv("CANAL_ESCALACAO")

        if not canal_escalacao_id_str:
            await ctx.send("⚠️ A variável de ambiente `CANAL_ESCALACAO` não está configurada. A escalação será postada neste canal.")
            target_channel = ctx.channel
        else:
            try:
                target_channel_id = int(canal_escalacao_id_str)
                _channel = self.bot.get_channel(target_channel_id) or await self.bot.fetch_channel(target_channel_id)
                
                if not isinstance(_channel, TextChannel):
                    await ctx.send(f"❌ O canal configurado (ID: {target_channel_id}) não é um canal de texto.")
                    return
                target_channel = _channel

                if target_channel.guild is None:
                     await ctx.send(f"❌ O canal de destino (ID: {target_channel_id}) não parece estar em um servidor.")
                     return
                permissions = target_channel.permissions_for(target_channel.guild.me)
                if not all([permissions.view_channel, permissions.send_messages, permissions.embed_links]):
                    await ctx.send(f"❌ Eu não tenho as permissões necessárias (ver, enviar mensagens, enviar embeds) no canal {target_channel.mention}.")
                    return
            except (ValueError, discord.NotFound, discord.Forbidden) as e:
                await ctx.send(f"❌ Erro ao acessar o canal de escalação (ID: {canal_escalacao_id_str}): {e}")
                return
            except Exception as e:
                await ctx.send(f"❌ Ocorreu um erro inesperado ao tentar acessar o canal de escalação: {e}")
                return
        
        if target_channel is None:
            await ctx.send("❌ Não foi possível determinar o canal de destino para a escalação.")
            return

        def check(m: discord.Message):
            return m.author == ctx.author and m.channel == ctx.channel

        try:
            await ctx.send("📝 Qual o **nome** da operação?")
            nome = (await self.bot.wait_for("message", check=check, timeout=120.0)).content
            await ctx.send("🕒 Qual o **horário**? (ex: 22:00)")
            hora = (await self.bot.wait_for("message", check=check, timeout=60.0)).content
            await ctx.send(f"👥 Qual o **número máximo de participantes** para '{nome}' às {hora}?")
            max_membros = int((await self.bot.wait_for("message", check=check, timeout=60.0)).content)
            if not (0 < max_membros <= 50): 
                await ctx.send("❌ Número de participantes deve ser entre 1 e 50.")
                return
        except ValueError:
            await ctx.send("❌ Número inválido. Por favor, insira um número.")
            return
        except TimeoutError:
            await ctx.send("⏰ Tempo esgotado para resposta. Comando cancelado.")
            return

        initial_description_embed = Embed(title=f"📢 Operação: {nome} às {hora}", color=Color.blue())
        # O conteúdo da descrição será gerado pela view ao ser atualizada/enviada.
        # Para o envio inicial, podemos simular o estado inicial:
        temp_view_for_initial_embed = EscalacaoView(max_membros, 0) # message_id temporário
        initial_embed = await temp_view_for_initial_embed._internal_update_embed_content(initial_description_embed)
        initial_embed.set_footer(text=f"Responsável pela ação: {ctx.author.display_name}", icon_url=ctx.author.display_avatar.url if ctx.author.display_avatar else None)
        
        try:
            sent_message = await target_channel.send(embed=initial_embed)
        except discord.HTTPException as e:
            await ctx.send(f"❌ Falha ao enviar a escalação para {target_channel.mention}: {e}")
            return
            
        # Cria a view real e a armazena
        view_instance = EscalacaoView(max_participantes=max_membros, message_id=sent_message.id) 
        self.active_views[sent_message.id] = view_instance # Armazena a view ativa
        
        try:
            # Edita a mensagem para atachar a view real e garantir que o embed está 100% correto com a view
            final_embed_with_view = await view_instance._internal_update_embed_content(initial_description_embed) # Usa a view real
            final_embed_with_view.set_footer(text=f"Responsável pela ação: {ctx.author.display_name}", icon_url=ctx.author.display_avatar.url if ctx.author.display_avatar else None)
            await sent_message.edit(embed=final_embed_with_view, view=view_instance)
        except discord.HTTPException as e:
            await ctx.send(f"⚠️ A escalação foi postada em {target_channel.mention}, mas ocorreu um erro ao adicionar os botões interativos: {e}")

        if target_channel.id != ctx.channel.id:
            await ctx.send(f"✅ Escalacão para **{nome}** postada com sucesso no canal {target_channel.mention}!")

    @commands.command(name="remover")
    async def cmd_remover(self, ctx: commands.Context, usuario_a_remover: Member):
        if not any(role.name.lower() in CARGOS_PERMITIDOS_ESCALACAO for role in ctx.author.roles):
            await ctx.send("❌ Você não tem permissão para usar este comando.")
            return

        if not ctx.message.reference or not ctx.message.reference.message_id:
            await ctx.send("❌ Por favor, use este comando respondendo à mensagem da escalação que você deseja modificar.")
            return
        
        target_message_id = ctx.message.reference.message_id
        view_instance = self.active_views.get(target_message_id)

        if not view_instance:
            await ctx.send("❌ Não encontrei uma escalação ativa associada a essa mensagem (ela pode ser antiga ou o bot reiniciou).")
            return

        # Obtém a mensagem original da escalação para editá-la
        target_message_obj = None
        try:
            # O canal da mensagem referenciada
            channel_of_escalacao = self.bot.get_channel(ctx.message.reference.channel_id)
            if not channel_of_escalacao: # Se não estiver no cache
                channel_of_escalacao = await self.bot.fetch_channel(ctx.message.reference.channel_id)
            
            if not channel_of_escalacao :
                 await ctx.send(f"❌ Não foi possível encontrar o canal da mensagem de escalação (ID: {ctx.message.reference.channel_id}).")
                 return

            target_message_obj = await channel_of_escalacao.fetch_message(target_message_id)
        except discord.NotFound:
            await ctx.send("❌ A mensagem da escalação original não foi encontrada.")
            return
        except discord.Forbidden:
            await ctx.send("❌ Não tenho permissão para buscar a mensagem da escalação original.")
            return
        except Exception as e:
            await ctx.send(f"❌ Erro ao buscar mensagem da escalação: {e}")
            return

        user_mention_to_remove = usuario_a_remover.mention
        removed = False
        promoted_feedback = ""

        # Tenta remover dos participantes principais
        if user_mention_to_remove in view_instance.participantes_slots:
            try:
                slot_index = view_instance.participantes_slots.index(user_mention_to_remove)
                view_instance.participantes_slots[slot_index] = EMPTY_SLOT_TEXT
                view_instance.inscritos.discard(user_mention_to_remove) # Usa discard para não dar erro se não existir
                removed = True

                if view_instance.reservas:
                    promovido_mention = view_instance.reservas.pop(0)
                    view_instance.participantes_slots[slot_index] = promovido_mention
                    # O promovido já está em 'inscritos', então não precisa readicionar.
                    # Para obter o nome do promovido de forma mais amigável:
                    try:
                        promoted_user_id = int(promovido_mention.strip('<@!>'))
                        promoted_member = ctx.guild.get_member(promoted_user_id) if ctx.guild else None # ctx.guild pode não existir em DMs
                        promoted_name = promoted_member.display_name if promoted_member else promovido_mention
                        promoted_feedback = f" {promoted_name} foi promovido(a) da reserva."
                    except: # Falha em obter nome amigável
                        promoted_feedback = f" Um reserva ({promovido_mention}) foi promovido."

            except ValueError: # Não deveria acontecer se o 'in' for verdadeiro, mas por segurança
                pass 
        
        # Se não foi removido dos principais, tenta remover dos reservas
        if not removed and user_mention_to_remove in view_instance.reservas:
            view_instance.reservas.remove(user_mention_to_remove)
            view_instance.inscritos.discard(user_mention_to_remove)
            removed = True

        if not removed:
            await ctx.send(f"🤷 {usuario_a_remover.display_name} não foi encontrado(a) na lista desta escalação.")
            return

        # Atualiza o embed da mensagem original
        if await view_instance.refresh_message_embed(target_message_obj):
            await ctx.send(f"✅ {usuario_a_remover.display_name} foi removido(a) da escalação.{promoted_feedback} A lista foi atualizada.")
        else:
            await ctx.send(f"⚠️ {usuario_a_remover.display_name} foi removido(a) dos dados, mas houve um erro ao atualizar a mensagem da escalação no Discord.")


async def setup(bot):
    await bot.add_cog(Escalacao(bot))