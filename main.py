import asyncio
import os
import uvicorn
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from web.api_rutas import router, init_templates
from bot.discord_bot import bot

# Inicializar FastAPI
app = FastAPI(title="SSPC - Mazatlan RP Backend")

# Habilitar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Servir archivos estáticos (CSS, JS, Imágenes)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Inicializar sistema de templates
init_templates(app)

# Incluir las rutas web
app.include_router(router)

from dotenv import load_dotenv

# Cargar variables de entorno desde el archivo .env
load_dotenv()

from datetime import datetime, timedelta
from supabase import create_client, Client

async def run_bot():
    # Obtener el token de forma segura desde las variables de entorno
    token = os.getenv("DISCORD_TOKEN")
    
    if not token:
        print("❌ ERROR: No se encontró el DISCORD_TOKEN en el archivo .env")
        return
    
    await bot.start(token)

async def auto_reset_weekly_times():
    # Usar las mismas credenciales que en dashboard.html
    SUPABASE_URL = "https://cmunztvfhsfsysrrmveo.supabase.co"
    SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImNtdW56dHZmaHNmc3lzcnJtdmVvIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzY5MjEwMTEsImV4cCI6MjA5MjQ5NzAxMX0.bfKsQHPyrk9fkyyW9ekNYEDdpBDeyupFjlzgfirCXro"
    
    try:
        supabase_client: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
    except Exception as e:
        print(f"⚠️ No se pudo inicializar Supabase para reseteo automático: {e}")
        return

    while True:
        now = datetime.now()
        # Encontrar el próximo lunes a las 00:00
        days_ahead = 0 - now.weekday()
        if days_ahead <= 0: # Si ya es lunes o más tarde, buscar el próximo lunes
            days_ahead += 7
            
        next_monday = now + timedelta(days=days_ahead)
        target_time = next_monday.replace(hour=0, minute=0, second=0, microsecond=0)
        
        wait_seconds = (target_time - now).total_seconds()
        print(f"⏰ Siguiente reseteo automático de tiempos semanales en {wait_seconds / 3600:.2f} horas.")
        
        await asyncio.sleep(wait_seconds)
        
        print("🔄 Ejecutando reseteo automático de tiempos semanales...")
        try:
            response = supabase_client.table('actividad_oficiales').select('discord_name').execute()
            if response.data:
                for user in response.data:
                    supabase_client.table('actividad_oficiales').update({
                        'tiempo_semanal': 0,
                        'estado': 'off',
                        'message_id': None
                    }).eq('discord_name', user['discord_name']).execute()
            print("✅ Reseteo semanal completado con éxito.")
        except Exception as e:
            print(f"❌ Error al resetear tiempos: {e}")
            
        # Esperar un poco para no entrar en bucle si la hora coincide
        await asyncio.sleep(60)

@app.on_event("startup")
async def startup_event():
    print("🚀 Iniciando Servidor Web y Bot de Discord...")
    # Crear tareas en segundo plano
    asyncio.create_task(run_bot())
    asyncio.create_task(auto_reset_weekly_times())

if __name__ == "__main__":
    # Northflank/Heroku/Render usan la variable 'PORT'. OptikLink usa 'SERVER_PORT'.
    port = int(os.getenv("PORT", os.getenv("SERVER_PORT", 8000)))
    uvicorn.run("main:app", host="0.0.0.0", port=port)
