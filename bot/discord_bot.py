import discord
from discord.ext import commands, tasks

# Configurar Intenciones (Permisos) del Bot
intents = discord.Intents.default()
intents.message_content = True
intents.members = True # NECESARIO para cambiar apodos y contar miembros

bot = commands.Bot(command_prefix="!", intents=intents)

# Variables globales para evitar abusar del API de Discord (Rate Limits)
last_members_count = -1
last_duty_count = -1
active_duty_count = 0

@tasks.loop(minutes=10)
async def update_stats_channels():
    global last_members_count, last_duty_count
    
    if not bot.guilds: return
    guild = bot.guilds[0]
    
    # 1. Actualizar Canal de Miembros Totales (Sin contar bots)
    miembros_reales = sum(1 for m in guild.members if not m.bot)
    if miembros_reales != last_members_count:
        canal_miembros = guild.get_channel(1496724468725186671)
        if canal_miembros:
            try:
                await canal_miembros.edit(name=f"🎖│SSPC: {miembros_reales}")
                last_members_count = miembros_reales
            except Exception as e:
                print("⚠️ Error actualizando canal miembros (Posible Rate Limit):", e)

    # 2. Actualizar Canal de Oficiales en Servicio
    if active_duty_count != last_duty_count:
        canal_duty = guild.get_channel(1496936848642015282)
        if canal_duty:
            try:
                await canal_duty.edit(name=f"🎖│En Servicio: {active_duty_count}")
                last_duty_count = active_duty_count
            except Exception as e:
                print("⚠️ Error actualizando canal servicio (Posible Rate Limit):", e)

@bot.event
async def on_ready():
    print(f"✅ Bot Conectado en Discord como {bot.user}")
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="Base de Datos SSPC"))
    # Iniciar el loop de actualización de estadísticas
    if not update_stats_channels.is_running():
        update_stats_channels.start()

@bot.event
async def on_member_join(member):
    # Forzar actualización en la próxima vuelta del loop
    global last_members_count
    last_members_count = -1

@bot.event
async def on_member_remove(member):
    # Forzar actualización en la próxima vuelta del loop
    global last_members_count
    last_members_count = -1

# Función que será llamada desde la web para cambiar el apodo
async def cambiar_apodo_oficial(discord_name: str, nuevo_apodo: str):
    if not bot.guilds:
        return False, "El bot no está en ningún servidor."
    
    # Tomamos el primer servidor donde está el bot
    guild = bot.guilds[0]
    
    # Buscar al miembro por nombre (Ej: oficial#0000 o solo oficial)
    member = discord.utils.find(lambda m: str(m) == discord_name or m.name == discord_name, guild.members)
    
    if not member:
        return False, f"Usuario '{discord_name}' no encontrado en el servidor de Discord."

    try:
        await member.edit(nick=nuevo_apodo)
        return True, "Apodo cambiado exitosamente."
    except discord.Forbidden:
        return False, "⚠️ El bot no tiene permisos suficientes o el rol del usuario es mayor al del bot."
    except Exception as e:
        return False, str(e)

# Función para enviar mensaje directo al aprobar/rechazar ausencia
async def enviar_dm_ausencia(discord_name: str, accion: str, razon_rechazo: str = ""):
    if not bot.guilds:
        return False, "El bot no está en ningún servidor."
    
    guild = bot.guilds[0]
    member = discord.utils.find(lambda m: str(m) == discord_name or m.name == discord_name, guild.members)
    
    if not member:
        return False, f"Usuario '{discord_name}' no encontrado en el servidor."

    embed = discord.Embed(
        title="🔔 Notificación de Ausencia - SSPC",
        color=0x2ecc71 if accion == "aceptar" else 0xe74c3c
    )
    
    if accion == "aceptar":
        embed.description = "Tu solicitud de ausencia ha sido **APROBADA**. Estás autorizado para ausentarte el tiempo estipulado."
    else:
        embed.description = f"Tu solicitud de ausencia ha sido **RECHAZADA**.\n\n**Razón:** {razon_rechazo}"
        
    try:
        await member.send(embed=embed)
        return True, "Mensaje Directo enviado al oficial."
    except discord.Forbidden:
        return False, "No se pudo enviar el DM (El usuario tiene los mensajes directos desactivados)."
    except Exception as e:
        return False, str(e)
