#Importacion modulo asincrono
import asyncio
from typing import Annotated
#Importar FastAPI
from fastapi import FastAPI, Request
#Importar respuesta HTML
from fastapi.responses import HTMLResponse
#Importar archivos estaticos para reconcoer estilos css
from fastapi.staticfiles import StaticFiles 
#importar plantillas Jinja2 (requieren el objeto Request importado arriba)
from fastapi.templating import Jinja2Templates
#importar extension HTPP y status para respuestas de error / Dependencias 
from fastapi import HTTPException, status, Depends

#--------controladores de Excepciones de error
#errores de validacion(si pide int y se recibe string)
from fastapi.exceptions import RequestValidationError 
# respuetas JSON para devolver espuestas desde el controlador de excepciones
from fastapi.responses import JSONResponse 
# manejo de errores desde la web frontend e indicar el error 
from starlette.exceptions import HTTPException as StarletteHTTPException

#----------------------- Importar Routers
from routers import users, posts

#----------------------- Importar Modelos
import models

#----------------------- Importar DB
# Motor de creacion de tablas, get_db - dependencia de sesiones en BD
from database import Base, engine, get_db, SessionLocal
from sqlalchemy import text

#----------------------- Importar BD
# select - consulatas en BD , Session - sesiones en BD
from sqlmodel import select, Session


#----------------------- Creacion de tables, si no existen
Base.metadata.create_all(bind=engine)



#inicializar app FastAPI
app =  FastAPI()

#""" -------------- CARPETAS ESTATICAS Y PLANTILLAS -------------- """

#Colocarl archivos media / staticos que provee el usuario
app.mount("/media", StaticFiles(directory="media"), name="media")

#Indicar a FastAPI donde encontrar los directorios estatucis (CSS, JS, IMG)
# (ruta de accesos de app / ruta de la carpeta en proyecto / nombre de referencia)
app.mount("/static", StaticFiles(directory="static"), name="static")


#Indicar a FastAPI donde encontrar las plantillas de Jinja2
templates = Jinja2Templates(directory="templates")

#""" ------------------------------------ """
# Implementar routers
# Agregas las rutas / agrega el prefijo y se complementa / encabezados para cada seccion
app.include_router(users.router, prefix="/api/users", tags=["users"])
app.include_router(posts.router, prefix="/api/posts", tags=["posts"])



#""" -------------- RUTA RAIZ (home / devolver plantilla) -------------- """
# ruta raiz / indicar que utilizara HTML / ruta raiz es igual home en name
@app.get("/", response_class=HTMLResponse, name="home")
# async - funcion asincrona para enviar y resivir datos

@app.get("/posts", include_in_schema=False, name="posts")

#Establecer una parametro de solicitud, Jinja2 requiere
async def home(request: Request, db: Annotated[Session, Depends(get_db)]): 
        result = db.execute(select(models.Post))
        posts = result.scalars().all()
        
        # Devolvemos la solicitud request con el archivo de platilla / diccionario de publicaciones / los titulos de cada pulicación
        # -----------------------------------------------------------solicitud request / posts de diccionario posts / titulos a home
        # return templates.TemplateResponse(request=request, name="index.html", {"request": request, "posts": "posts", "title": "Home"})
        return templates.TemplateResponse("index.html", {"request": request, "posts": posts, "title": "Home"},)

#""" --------------------------------------------------------------------- """

# ################# RUTAS ##################

#""" -------------- VERIFICAR LA CONEXION CON BD -------------- """
@app.get("/db-check")
async def check_db():
    try:
        # Intentamos obtener una sesión
        db = SessionLocal()
        db.execute(text("SELECT 1"))
        return {"status": "ok", "message": "Database is connected"}
    except Exception as e:
        return {"status": "error", "details": str(e)}
#""" ------------------------------------ """

# BUSQUEDA DE PUBLICACION POR ID 
## De encontrar el usuario devuelve el diccionario de publicaciones
@app.get("/users/{user_id}/posts", include_in_schema=False, name="user_posts")
async def user_posts_page(
    request: Request,
    user_id: int,
    db: Annotated[Session, Depends(get_db)],
):
    result = db.execute(select(models.User).where(models.User.id == user_id))
    user = result.scalars().first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    result = db.execute(select(models.Post).where(models.Post.user_id == user_id))
    posts = result.scalars().all()
    return templates.TemplateResponse(
        request,
        "user_posts.html",
        {"posts": posts, "user": user, "title": f"{user.username}'s Posts"},
    )
    
    # ---------------- RUTA DE PUBLICACION POR ID
#Ruta por ID o parametro de ruta
@app.get("/api/posts/{post_id}")
async def post_page(request: Request, post_id: int, db: Annotated[Session, Depends(get_db)]):
#se realiza la consulta de publicaciones en la BD por ID
    result = db.execute(select(models.Post).where(models.Post.id == post_id))
    post = result.scalars().first()
#si la publicacion es encontrada
    if post:
#establecer titulo de la publicacion / solo los primeros 50 caracteres del titulo
        title = post.title[:50]
        #retornara la publicacion buscada - plantilla / solicitud request / post de direccioanrio / titulo del post
        return templates.TemplateResponse("post.html", {"request": request, "post": post, "title": title},
        )
    #generar excepcyion http 404 indicando que no se encontro la busqueda
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Publicación no encontrada")

##""" -------------- VALIDACION Y ERRORES -------------- """

#""" CONTROLADOR DE EXCEPCIONES DE VALIDAACION RUTAS DEL NAVEGADOR """
#Capture el control de excepciones
@app.exception_handler(StarletteHTTPException)
# se guarda y recibe en request: Request,.... 
async def general_http_exception_handler(request: Request, exception: StarletteHTTPException):
    message = ( #configurar el mensaje
        exception.detail #mostrar detalles del error
        if exception.detail
        #de lo contrario establecemos un mensaje 
        else "Error. Por favor comprueba tu solicitud de nuevo."
    )
    # comprobar si la ruta empieza por /api 
    if request.url.path.startswith("/api"):
        return JSONResponse(# devolver una respuesta JSON
            status_code=exception.status_code, #Estableciendo el codigo de estatus, ya que no cuentan con un codigo de estado
            content={"detail": message}, #Devolvemos un mensaje 
        )
    #si no es una respueta de /API
    return templates.TemplateResponse(
        request, #se devuelve la respuesta de la plantilla error
        "error.html",
        {
            #establecemos el codigo del error
            "status_code": exception.status_code,
            #titulo de la pagina en el estatus
            "title": exception.status_code,
            #mensaje de la excepcion
            "message": message,
        },
        #pasamos el codigo del estado a la respuesta de la plantilla 
        #indicando al navegador obtener el codigo HTTP correcto
        status_code=exception.status_code,
    )

#""" ERRORES DE VALIDADCION  RUTAS DE FASTAPI"""
#Detectando error de validacion de solicitudes
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exception: RequestValidationError):
    #si la ruta de la aplicacion comienza con API
    if request.url.path.startswith("/api"):
        return JSONResponse(
            #se pasa el codigo del error HTTP en JSON
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            #Mostrar detalles de error de validacion
            content={"detail": exception.errors()},
        )
    return templates.TemplateResponse(
        request,
        #mostrando la pagina de error
        #con el codigo de estado, el titulo del error
        "error.html",
        {
            "status_code": status.HTTP_422_UNPROCESSABLE_CONTENT,
            "title": status.HTTP_422_UNPROCESSABLE_CONTENT,
            #estableciendo el mensaje del error de validacion 
            "message": "Validación no valida.",
        },
        status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
    )