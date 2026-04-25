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

async def run_bot():
    # Obtener el token de forma segura desde las variables de entorno
    token = os.getenv("DISCORD_TOKEN")
    
    if not token:
        print("❌ ERROR: No se encontró el DISCORD_TOKEN en el archivo .env")
        return
    
    await bot.start(token)

@app.on_event("startup")
async def startup_event():
    print("🚀 Iniciando Servidor Web y Bot de Discord...")
    # Crear una tarea en segundo plano para el bot de Discord
    asyncio.create_task(run_bot())

if __name__ == "__main__":
    # OptikLink (Pterodactyl) usa puertos dinámicos. Leemos el puerto asignado automáticamente.
    port = int(os.getenv("SERVER_PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port)
