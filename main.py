from typing import Optional
from fastapi import FastAPI, Request, Form, UploadFile, File
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from data.database import database
from data.videojuego_repository import VideojuegoRepository
from data.usuario_repository import UsuarioRepository
from domain.model.videojuego import Videojuego
from domain.model.usuario import Usuario
from starlette.middleware.sessions import SessionMiddleware
from pathlib import Path
from datetime import datetime

# Obtener el directorio actual del script
BASE_DIR = Path(__file__).resolve().parent

# Crear la aplicación FastAPI
app = FastAPI(title="GameAtlas", description="Plataforma de Videojuegos")

# Añadir middleware de sesiones
app.add_middleware(SessionMiddleware, secret_key="tu-clave-secreta-super-segura-12345")

# Configurar las plantillas
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

# Configurar archivos estáticos (CSS, JS, imágenes)
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")

def get_db():
    return database


# ===== RUTAS DE AUTENTICACIÓN =====

@app.get("/login")
async def form_login(request: Request):
    """Muestra el formulario de login"""
    return templates.TemplateResponse("login.html", {"request": request})


@app.post("/login")
async def login(request: Request, correo: str = Form(...), contraseña: str = Form(...)):
    """Procesa el login"""
    repo = UsuarioRepository()
    db = get_db()
    
    usuario = repo.verificar_credenciales(db, correo, contraseña)
    
    if usuario:
        # Guardar usuario en sesión
        request.session["usuario_id"] = usuario["id"]
        request.session["usuario_nombre"] = usuario["nombre"]
        request.session["usuario_correo"] = usuario["correo"]
        request.session["es_admin"] = usuario.get("es_admin", 0)
        return RedirectResponse("/", status_code=303)
    else:
        return templates.TemplateResponse("login.html", {
            "request": request,
            "error": "Correo o contraseña incorrectos"
        })


@app.get("/registro")
async def form_registro(request: Request):
    """Muestra el formulario de registro"""
    return templates.TemplateResponse("registro.html", {"request": request})


@app.post("/registro")
async def registro(
    request: Request,
    nombre: str = Form(...),
    correo: str = Form(...),
    contraseña: str = Form(...),
    contraseña_confirmacion: str = Form(...)
):
    """Procesa el registro de nuevo usuario"""
    repo = UsuarioRepository()
    db = get_db()
    
    # Validar que las contraseñas coincidan
    if contraseña != contraseña_confirmacion:
        return templates.TemplateResponse("registro.html", {
            "request": request,
            "error": "Las contraseñas no coinciden"
        })
    
    # Validar que el correo no esté registrado
    usuario_existente = repo.get_por_correo(db, correo)
    if usuario_existente:
        return templates.TemplateResponse("registro.html", {
            "request": request,
            "error": "El correo ya está registrado"
        })
    
    # Crear nuevo usuario
    nuevo_usuario = Usuario(None, nombre, correo, contraseña)
    repo.insertar_usuario(db, nuevo_usuario)
    
    return RedirectResponse("/login?mensaje=Registro exitoso. Por favor inicia sesión", status_code=303)


@app.get("/logout")
async def logout(request: Request):
    """Cierra la sesión del usuario"""
    request.session.clear()
    return RedirectResponse("/", status_code=303)


@app.get("/")
async def inicio(request: Request):
    """Redirecciona a la página de videojuegos"""
    return RedirectResponse("/videojuegos", status_code=303)


@app.get("/videojuegos")
async def videojuegos(request: Request):
    """Página principal de videojuegos"""
    repo = VideojuegoRepository()
    juegos = repo.get_all(get_db())
    is_admin = request.session.get("es_admin") == 1
    return templates.TemplateResponse("videojuegos.html", {
        "request": request,
        "juegos": juegos,
        "is_admin": is_admin
    })


@app.get("/buscar")
async def buscar(request: Request, nombre: str = ""):
    """Busca videojuegos por nombre"""
    repo = VideojuegoRepository()
    juegos = repo.buscar_videojuegos(get_db(), nombre, "")
    is_admin = request.session.get("es_admin") == 1
    return templates.TemplateResponse("videojuegos.html", {
        "request": request,
        "juegos": juegos,
        "busqueda": True,
        "nombre_busqueda": nombre,
        "is_admin": is_admin
    })


@app.get("/playstation", response_class=HTMLResponse)
async def listar_playstation(request: Request):
    """Página de PlayStation"""
    repo = VideojuegoRepository()
    juegos = repo.get_por_consola(get_db(), "PlayStation")
    is_admin = request.session.get("es_admin") == 1
    return templates.TemplateResponse(
        "playstation.html",
        {"request": request, "juegos": juegos, "is_admin": is_admin}
    )


@app.get("/xbox")
async def form_insertar(request: Request):
    """Página de Xbox"""
    repo = VideojuegoRepository()
    juegos = repo.get_por_consola(get_db(), "Xbox")
    is_admin = request.session.get("es_admin") == 1
    return templates.TemplateResponse("xbox.html", {
        "request": request,
        "juegos": juegos,
        "is_admin": is_admin
    })


@app.post("/xbox")
async def insertar_videojuego(
    nombre: str = Form(...),
    precio: float = Form(...),
    genero: str = Form(...),
    consola: str = Form(...),
    valoracion: float = Form(...)
):
    """Inserta un nuevo videojuego"""
    repo = VideojuegoRepository()
    db = get_db()
    nuevo = Videojuego(None, nombre, precio, genero, valoracion)
    repo.insertar_videojuego(db, nuevo, consola)
    return RedirectResponse("/xbox")


# ===== RUTAS PARA AGREGAR JUEGOS (ADMIN) =====

@app.get("/agregar-juego")
async def form_agregar_juego(request: Request):
    """Formulario para agregar un nuevo videojuego (Solo Admin)"""
    if request.session.get("es_admin") != 1:
        return RedirectResponse("/login", status_code=303)
    
    return templates.TemplateResponse("añadirjuego.html", {"request": request})


@app.post("/agregar-juego")
async def agregar_juego(
    request: Request,
    nombre: str = Form(...),
    precio: float = Form(...),
    genero: str = Form(...),
    valoracion: float = Form(...),
    consolas: list = Form(...),
    portada: UploadFile = File(...)
):
    """Agrega un nuevo videojuego a la base de datos (Solo Admin)"""
    if request.session.get("es_admin") != 1:
        return RedirectResponse("/login", status_code=303)
    
    # Validar que haya seleccionado al menos una consola
    if not consolas:
        return RedirectResponse("/agregar-juego", status_code=303)
    
    # Validar que el archivo sea PNG
    if not portada.filename.lower().endswith('.png'):
        return RedirectResponse("/agregar-juego", status_code=303)
    
    # Validar que el nombre del archivo sea exactamente como el nombre del juego (incluyendo .PNG)
    nombre_esperado = f"{nombre}.PNG"
    if portada.filename != nombre_esperado:
        # Si no coincide exactamente, redirigir con error
        return RedirectResponse("/agregar-juego", status_code=303)
    
    # Guardar el archivo en la carpeta static
    try:
        file_path = BASE_DIR / "static" / portada.filename
        with open(file_path, "wb") as f:
            contenido = await portada.read()
            f.write(contenido)
    except Exception as e:
        print(f"Error al guardar archivo: {e}")
        return RedirectResponse("/agregar-juego", status_code=303)
    
    # Guardar el juego en la base de datos con todas las consolas
    repo = VideojuegoRepository()
    db = get_db()
    nuevo_juego = Videojuego(None, nombre, precio, genero, valoracion)
    repo.insertar_videojuego_multiples_consolas(db, nuevo_juego, consolas)
    
    return RedirectResponse("/videojuegos", status_code=303)    


# ===== RUTAS PARA BORRAR Y EDITAR JUEGOS (ADMIN) =====

@app.post("/borrar-juego")
async def borrar_juego(request: Request, videojuego_id: int = Form(...)):
    """Borra un videojuego (Solo Admin)"""
    if request.session.get("es_admin") != 1:
        return RedirectResponse("/login", status_code=303)
    
    repo = VideojuegoRepository()
    db = get_db()
    repo.borrar_videojuego(db, videojuego_id)
    
    return RedirectResponse("/videojuegos", status_code=303)


@app.get("/editar-juego/{videojuego_id}")
async def form_editar_juego(request: Request, videojuego_id: int):
    """Formulario para editar un videojuego (Solo Admin)"""
    if request.session.get("es_admin") != 1:
        return RedirectResponse("/login", status_code=303)
    
    repo = VideojuegoRepository()
    db = get_db()
    juego = repo.get_por_id(db, videojuego_id)
    
    if not juego:
        return RedirectResponse("/videojuegos", status_code=303)
    
    # Obtener las consolas actuales del juego
    consolas_actuales = repo.get_consolas_por_videojuego(db, videojuego_id)
    
    return templates.TemplateResponse("editarjuego.html", {
        "request": request,
        "juego": {
            "id": juego[0],
            "nombre": juego[1],
            "precio": juego[2],
            "genero": juego[3],
            "valoracion": juego[4]
        },
        "consolas_actuales": consolas_actuales
    })


@app.post("/editar-juego")
async def editar_juego(
    request: Request,
    videojuego_id: int = Form(...),
    nombre: str = Form(...),
    precio: float = Form(...),
    genero: str = Form(...),
    valoracion: float = Form(...),
    consolas: list = Form(None),
    portada: UploadFile = File(None)
):
    """Actualiza un videojuego en la base de datos (Solo Admin)"""
    if request.session.get("es_admin") != 1:
        return RedirectResponse("/login", status_code=303)
    
    # Si se proporciona un archivo de portada, validar y guardar
    if portada and portada.filename:
        # Validar que el archivo sea PNG
        if not portada.filename.lower().endswith('.png'):
            return RedirectResponse(f"/editar-juego/{videojuego_id}", status_code=303)
        
        # Validar que el nombre del archivo sea exactamente como el nombre del juego (incluyendo .PNG)
        nombre_esperado = f"{nombre}.PNG"
        if portada.filename != nombre_esperado:
            return RedirectResponse(f"/editar-juego/{videojuego_id}", status_code=303)
        
        # Guardar el archivo en la carpeta static
        try:
            file_path = BASE_DIR / "static" / portada.filename
            with open(file_path, "wb") as f:
                contenido = await portada.read()
                f.write(contenido)
        except Exception as e:
            print(f"Error al guardar archivo: {e}")
            return RedirectResponse(f"/editar-juego/{videojuego_id}", status_code=303)
    
    # Actualizar el juego en la base de datos
    repo = VideojuegoRepository()
    db = get_db()
    juego_actualizado = Videojuego(videojuego_id, nombre, precio, genero, valoracion)
    repo.actualizar_videojuego(db, juego_actualizado)
    
    # Actualizar las consolas si se proporcionaron
    if consolas:
        repo.actualizar_consolas_videojuego(db, videojuego_id, consolas)
    
    return RedirectResponse("/videojuegos", status_code=303)


@app.get("/steam")
async def form_borrar(request: Request):
    """Página para Steam"""
    repo = VideojuegoRepository()
    db = get_db()
    juegos = repo.get_por_consola(db, "Steam")
    is_admin = request.session.get("es_admin") == 1
    return templates.TemplateResponse("steam.html", {
        "request": request,
        "juegos": juegos,
        "is_admin": is_admin
    })


@app.post("/steam")
async def borrar_videojuego(id: int = Form(...)):
    """Borra un videojuego"""
    repo = VideojuegoRepository()
    db = get_db()
    repo.borrar_videojuego(db, id)
    return RedirectResponse("/steam", status_code=303)



@app.get("/switch")
async def actualizar_videojuego_form(request: Request):
    """Página de Switch"""
    repo = VideojuegoRepository()
    db = get_db()
    juegos = repo.get_por_consola(db, "Switch")
    is_admin = request.session.get("es_admin") == 1
    return templates.TemplateResponse("switch.html", {
        "request": request,
        "juegos": juegos,
        "is_admin": is_admin
    })

@app.post("/switch")
async def actualizar_videojuego(
    id: int = Form(...),
    nombre: str = Form(...),
    precio: float = Form(...),
    genero: str = Form(...),
    valoracion: float = Form(...)
):
    """Actualiza un videojuego"""
    repo = VideojuegoRepository()
    db = get_db()
    actualizado = Videojuego(id, nombre, precio, genero, valoracion)
    repo.actualizar_videojuego(db, actualizado)
    return RedirectResponse("/switch", status_code=303)


# ===== RUTAS DEL CARRITO =====

@app.post("/agregar-carrito")
async def agregar_carrito(request: Request, videojuego_id: int = Form(...)):
    """Agrega un videojuego al carrito"""
    # Verificar que esté logueado
    if not request.session.get("usuario_id"):
        return RedirectResponse("/login", status_code=303)
    
    # Obtener datos del videojuego
    repo = VideojuegoRepository()
    juego = repo.get_por_id(get_db(), videojuego_id)
    
    if not juego:
        return RedirectResponse("/videojuegos", status_code=303)
    
    # Inicializar carrito si no existe
    if "carrito" not in request.session:
        request.session["carrito"] = []
    
    # Agregar al carrito
    request.session["carrito"].append({
        "id": juego[0],
        "nombre": juego[1],
        "precio": float(juego[2]),
        "genero": juego[3],
        "valoracion": float(juego[4])
    })
    
    # Actualizar contador
    request.session["carrito_count"] = len(request.session["carrito"])
    
    return RedirectResponse("/videojuegos", status_code=303)


@app.get("/carrito")
async def ver_carrito(request: Request):
    """Muestra el carrito de compras"""
    # Verificar que esté logueado
    if not request.session.get("usuario_id"):
        return RedirectResponse("/login", status_code=303)
    
    carrito = request.session.get("carrito", [])
    total = sum(item["precio"] for item in carrito)
    
    return templates.TemplateResponse("carrito.html", {
        "request": request,
        "carrito": carrito,
        "total": total
    })


@app.post("/eliminar-carrito")
async def eliminar_carrito(request: Request, indice: int = Form(...)):
    """Elimina un item del carrito"""
    if not request.session.get("usuario_id"):
        return RedirectResponse("/login", status_code=303)
    
    carrito = request.session.get("carrito", [])
    
    if 0 <= indice < len(carrito):
        carrito.pop(indice)
        request.session["carrito"] = carrito
        request.session["carrito_count"] = len(carrito)
    
    return RedirectResponse("/carrito", status_code=303)


@app.get("/limpiar-carrito")
async def limpiar_carrito(request: Request):
    """Limpia todo el carrito"""
    if not request.session.get("usuario_id"):
        return RedirectResponse("/login", status_code=303)
    
    request.session["carrito"] = []
    request.session["carrito_count"] = 0
    
    return RedirectResponse("/carrito", status_code=303)


@app.get("/pago")
async def formulario_pago(request: Request):
    """Muestra el formulario de pago"""
    # Verificar que esté logueado
    if not request.session.get("usuario_id"):
        return RedirectResponse("/login", status_code=303)
    
    carrito = request.session.get("carrito", [])
    
    # Verificar que haya items en el carrito
    if not carrito:
        return RedirectResponse("/carrito", status_code=303)
    
    total = sum(item["precio"] for item in carrito)
    
    return templates.TemplateResponse("pago.html", {
        "request": request,
        "carrito": carrito,
        "total": total
    })


@app.post("/procesar-pago")
async def procesar_pago(
    request: Request,
    metodo_pago: str = Form(...),
    nombre_titular: str = Form(None),
    numero_tarjeta: str = Form(None),
    fecha_expiracion: str = Form(None),
    cvv: str = Form(None)
):
    """Procesa el pago"""
    # Verificar que esté logueado
    if not request.session.get("usuario_id"):
        return RedirectResponse("/login", status_code=303)
    
    carrito = request.session.get("carrito", [])
    
    # Verificar que haya items en el carrito
    if not carrito:
        return RedirectResponse("/carrito", status_code=303)
    
    # Limpiar el carrito después del pago exitoso
    request.session["carrito"] = []
    request.session["carrito_count"] = 0
    
    return templates.TemplateResponse("pago_exitoso.html", {
        "request": request,
        "metodo_pago": metodo_pago,
        "usuario_nombre": request.session.get("usuario_nombre"),
        "fecha_pago": datetime.now().strftime("%d/%m/%Y %H:%M")
    })


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
