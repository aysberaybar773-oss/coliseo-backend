from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import database as db

# Inicializamos la base de datos al arrancar
db.inicializar_bd()

app = FastAPI(title="Coliseo Digital API")

# Habilitar CORS para que cualquier navegador pueda interactuar con la API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class VotoSchema(BaseModel):
    bando: str

class ComentarioSchema(BaseModel):
    bando: str
    contenido: str

@app.get("/")
def inicio():
    return {"status": "Online", "msg": "Servidor del Coliseo funcionando en la nube."}

@app.get("/peleas/{pelea_id}")
def ver_pelea(pelea_id: int):
    datos = db.obtener_pelea(pelea_id)
    if not datos:
        raise HTTPException(status_code=404, detail="La disputa no existe.")
    return datos

@app.post("/peleas/{pelea_id}/votar")
def votar_pelea(pelea_id: int, data: VotoSchema):
    bando = data.bando.upper()
    if bando not in ['A', 'B']:
        raise HTTPException(status_code=400, detail="Bando inválido. Elige A o B.")
    db.registrar_voto(pelea_id, bando)
    return {"status": "Voto procesado con éxito"}

@app.post("/peleas/{pelea_id}/comentar")
def comentar_pelea(pelea_id: int, data: ComentarioSchema):
    if not data.contenido.strip():
        raise HTTPException(status_code=400, detail="El comentario no puede estar vacío.")
    if data.bando.upper() not in ['A', 'B']:
        raise HTTPException(status_code=400, detail="Bando inválido.")
    db.agregar_comentario(pelea_id, data.contenido, data.bando.upper())
    return {"status": "Comentario publicado"}
