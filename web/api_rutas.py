from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

router = APIRouter()
templates = None

def init_templates(app):
    global templates
    templates = Jinja2Templates(directory="templates")

# --- Rutas de Páginas HTML ---

@router.get("/", response_class=HTMLResponse)
async def index_root(request: Request):
    return templates.TemplateResponse(request=request, name="index.html")

@router.get("/index.html", response_class=HTMLResponse)
async def index_page(request: Request):
    return templates.TemplateResponse(request=request, name="index.html")

@router.get("/dashboard.html", response_class=HTMLResponse)
async def dashboard(request: Request):
    return templates.TemplateResponse(request=request, name="dashboard.html")

@router.get("/normativa.html", response_class=HTMLResponse)
async def normativa(request: Request):
    return templates.TemplateResponse(request=request, name="normativa.html")

@router.get("/manual.html", response_class=HTMLResponse)
async def manual(request: Request):
    return templates.TemplateResponse(request=request, name="manual.html")

@router.get("/codigo-penal.html", response_class=HTMLResponse)
async def codigo_penal(request: Request):
    return templates.TemplateResponse(request=request, name="codigo-penal.html")

@router.get("/verificacion.html", response_class=HTMLResponse)
async def verificacion(request: Request):
    return templates.TemplateResponse(request=request, name="verificacion.html")

# --- API Endpoints para conectar la Web con el Bot ---
from bot.discord_bot import cambiar_apodo_oficial

@router.post("/api/bot/cambiar_apodo")
async def cambiar_apodo(data: dict):
    discord_name = data.get("discord_name")
    nuevo_apodo = data.get("nuevo_apodo")
    
    if not discord_name or not nuevo_apodo:
        return {"status": "error", "message": "Faltan datos (discord_name o nuevo_apodo)"}
    
    exito, mensaje = await cambiar_apodo_oficial(discord_name, nuevo_apodo)
    
    if exito:
        return {"status": "success", "message": mensaje}
    else:
        return {"status": "error", "message": mensaje}

@router.post("/api/bot/dm_ausencia")
async def dm_ausencia(data: dict):
    discord_name = data.get("discord_name")
    accion = data.get("accion")
    razon = data.get("razon_rechazo", "")
    
    if not discord_name or not accion:
        return {"status": "error", "message": "Faltan datos (discord_name o accion)"}
    
    from bot.discord_bot import enviar_dm_ausencia
    exito, mensaje = await enviar_dm_ausencia(discord_name, accion, razon)
    
    if exito:
        return {"status": "success", "message": mensaje}
    else:
        return {"status": "error", "message": mensaje}

@router.post("/api/bot/set_duty_count")
async def set_duty_count(data: dict):
    count = data.get("count", 0)
    import bot.discord_bot as dbot
    dbot.active_duty_count = count
    return {"status": "success"}
