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

#----------------------- Importar Schemas
from schemas import (
    PostCreate, 
    PostResponse, 
    UserCreate, 
    UserResponse, 
    PostUpdate,
    UserUpdate
    )

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



"""# directorio de ejemplo para publicaciones
posts: list[dict] = [
    {
        "id": 1,
        "author": "Corey Schafer",
        "title": "FastAPI is Awesome",
        "content": "This framework is really easy to use and super fast.",
        "date_posted": "April 20, 2025",
    },
    {
        "id": 2,
        "author": "Jane Doe",
        "title": "Python is Great for Web Development",
        "content": "Python is a great language for web development, and FastAPI makes it even better.",
        "date_posted": "April 21, 2025",
    },
]
"""

#""" -------------- Extras -------------- """
#Devolver en formato JSON
"""
@app.get("/")
async - funcion asincrona para enviar y resivir datos
async def root():
    return {"message":"Hello FastAPI"}"""

#Devolver en formato HTML
"""incluinclude_in_schema=False, no incluira en la documentacion la ruta
@app.get("/", response_class=HTMLResponse, include_in_schema=False)"""

#""" ------------------------------------ """

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
def check_db():
    try:
        # Intentamos obtener una sesión
        db = SessionLocal()
        db.execute(text("SELECT 1"))
        return {"status": "ok", "message": "Database is connected"}
    except Exception as e:
        return {"status": "error", "details": str(e)}
#""" ------------------------------------ """
#""" -------------- RUTAS DE USUARIO -------------- """
# Crear Usuarios
@app.post(
    "/api/users",
    response_model=UserResponse, #modelo de respuesta 
    status_code=status.HTTP_201_CREATED, #indicando que el recurso se a creado
)

#""" --------------------------------------------------------------------- """

# -------------- FUNCION VERIFICAR SI USUARIO / EMAIL YA EXISTE --------------

# Indicamos que la BD depende de una sesion creada o iniciada
def create_user(user: UserCreate, db: Annotated[Session, Depends(get_db)]): 
    # 1 - Verificar si ya existe el usuario
    # ejecutando una consulta , verificando si el modelo username es igual al username proporcionado
    result = db.execute(select(models.User).where(models.User.username == user.username))
    
    # excepxion su el usuario ya existe
    existing_user = result.scalars().first()
    
    # Respuesta si el usuario ya existe
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail= "El usuario ya existe"
        )
        
    result = db.execute(select(models.User).where(models.User.email == user.email))
    
    # excepxion su el usuario ya existe
    existing_email = result.scalars().first()
    
    # Respuesta si el usuario ya existe
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail= "El email ya existe"
        )

#""" --------------------------------------------------------------------- """

# -------------- CREAR USUARIO --------------
# Creando Usuario nuevo
    new_user = models.User(
        username = user.username,
        email=user.email,
    )
# Crear usuario en la base de datos
    db.add(new_user)
    db.commit() #confirmar en la BD
    db.refresh(new_user) #refrescar y crar el nuevo usuario
    return new_user

# ------------- RUTA MOSTRAR USUARIOS ------------------
@app.get("/api/users", response_model=list[UserResponse])
def get_users(db: Annotated[Session, Depends(get_db)]):
    result = db.execute(select(models.User))
    users = result.scalars().all()
    return users

# ------------- RUTA POR ID BUSQUEDA DE USUARIOS ------------------
@app.get("/users/{user_id}", response_model=UserResponse)
def get_user(user_id: int, db: Annotated[Session, Depends(get_db)]): 
    
    # ejecutando una consulta , verificando si el modelo username es igual al username proporcionado
    result = db.execute(select(models.User).where(models.User.id == user_id))
    
    # excepxion si el usuario ya existe
    user = result.scalars().first()
    
    # Si el usuario existe
    if user:
        return user
    # Si el usuario NO existe
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail= "Usuario no encontrado")


# ------------- RUTA DE ACTUALIZACION DE USUARIO
# Actualizar usuario por ID
@app.patch("/api/users/{user_id}", response_model=UserResponse)
def update_user(
    user_id: int,
    user_update: UserUpdate,
    db: Annotated[Session, Depends(get_db)],
):
    # Verificar que el usuario a modificar existe 
    result = db.execute(select(models.User).where(models.User.id == user_id))
    user = result.scalars().first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Uasuario no existente",
        )
    # ----- VERIFICAR QUE NO CAMBIEN NOMBRE O EMAIL POR UNO QUE YA EXISTE 
    if user_update.username is not None and user_update.username != user.username:
        result = db.execute(
            select(models.User).where(models.User.username == user_update.username),
        )
        existing_user = result.scalars().first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El nombre de usuario ya existe",
            )

    if user_update.email is not None and user_update.email != user.email:
        result = db.execute(
            select(models.User).where(models.User.email == user_update.email),
        )
        existing_email = result.scalars().first()
        if existing_email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email ya existe",
            )
            
    # Verificar campo por cambio si fue actualizado o no para cambiar solo los actualizados
    if user_update.username is not None:
        user.username = user_update.username
    if user_update.email is not None:
        user.email = user_update.email
    if user_update.image_file is not None:
        user.image_file = user_update.image_file

    # Confirmar actualización en base de datos, refrescar y devolver usuraio 
    db.commit()
    db.refresh(user)
    return user

# Ruta de aliminación de usuarios
@app.delete("/api/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: int, db: Annotated[Session, Depends(get_db)]):
    result = db.execute(select(models.User).where(models.User.id == user_id))
    user = result.scalars().first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    db.delete(user)
    db.commit()

# ------------- RUTAS DE PUBLICACIONES ------------------
# BUSQUEDA DE PUBLICACION POR ID 
## De encontrar el usuario devuelve el diccionario de publicaciones
@app.get("/users/{user_id}/posts", include_in_schema=False, name="user_posts")
def user_posts_page(
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


# Responder con lista de respuesta de publicaciones en la siguiente ruta
# Validar que cada publicacion coincida con el modelo de despuesta de publiacion
@app.get("/api/posts", response_model=list[PostResponse])
def get_posts(db: Annotated[Session, Depends(get_db)]):
    result = db.execute(select(models.Post))
    posts = result.scalars().all()
    return posts

# RUTA Crear Publicación
@app.post(
    "/api/posts",
    response_model=PostResponse, #modelo de respuesta 
    status_code=status.HTTP_201_CREATED #indicando que el recurso se a creado
)

# ------------------ FUNCION CREACION DE PUBLICACION
# Utilizando schema de creacion, validando con nuestra esquema  
# Establecer sesion con BD y verificar primero si el usuario existe 
def create_post(post: PostCreate, db: Annotated[Session, Depends(get_db)]):
    result = db.execute(select(models.User).where(models.User.id == post.user_id))
    user = result.scalars().first()
    if not user:
        # Devolviendo un error, si usuario no es valido
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    # Crear publicacion de acuerdo a sus atributos de clase
    new_post = models.Post(
        title=post.title,
        content=post.content,
        user_id=post.user_id,
    )
    # Agregar a la base de datos la nueva publicación
    db.add(new_post)
    # Confirmar 
    db.commit()
    # Regrescar la BD
    db.refresh(new_post)
    # Devolver la nueva publicaión
    return new_post


# ---------------- RUTA DE PUBLICACION POR ID
#Ruta por ID o parametro de ruta
@app.get("/api/posts/{post_id}")
def post_page(request: Request, post_id: int, db: Annotated[Session, Depends(get_db)]):
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

#---------------- ACTUALIZAR PUBLICACION COMPLETA 
#Ruta de actualizacion de post - reutilizando postcreate por tener todo ya hecho
@app.put("/api/posts/{post_id}", response_model=PostResponse)
def update_post_full(request: Request, post_id: int, post_data: PostCreate,db: Annotated[Session, Depends(get_db)]):
#se realiza la consulta de publicaciones en la BD por ID
    result = db.execute(select(models.Post).where(models.Post.id == post_id))
    post = result.scalars().first()
    # 1° Verificar si la publicacion ya existe 
    if not post:

        #generar excepcyion http 404 indicando que no se encontro la busqueda
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Publicación no encontrada")
#Verificar el usuario que hace la modificacion es el mismo autor y existe
    if post_data.user_id != post.user_id:
        result = db.execute(select(models.User).where(models.User.id == post_data.user_id))
        user = result.scalars().first()
        if not user:
            # Devolviendo un error, si usuario no es valido
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )
            
    # Realizar actualización de publicación en BD
    post.title = post_data.title 
    post.content = post_data.content 
    post.user_id = post_data.user_id 
    # Verificar actualizacion en BD
    db.commit()
    # Actualizar BD
    db.refresh(post)
    # Devolver publicacion
    return post

#---------------- ACTUALIZAR PUBLICACION PARCIAL
#Ruta de actualizacion de post solo campos deseados
@app.patch("/api/posts/{post_id}", response_model=PostResponse)
def update_post_partial(request: Request, post_id: int, post_data: PostUpdate, db: Annotated[Session, Depends(get_db)]):
#se realiza la consulta de publicaciones en la BD por ID
    result = db.execute(select(models.Post).where(models.Post.id == post_id))
    post = result.scalars().first()
    # 1° Verificar si la publicacion ya existe 
    if not post:

        #generar excepcyion http 404 indicando que no se encontro la busqueda
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Publicación no encontrada")

    # Actualizar solo los campos deseados / Solo optener lo que se cambio con model_dump(exclude_unset=True)
    update_data = post_data.model_dump(exclude_unset=True)
    # Nos devuelve un dicionario al cual recorremos para obtener el campo y el valor modificados
    for field, value in update_data.items():
        # Devolviendo una publicación solo con los valores modificados
        setattr(post, field, value)

    # Verificar actualizacion en BD
    db.commit()
    # Actualizar BD
    db.refresh(post)
    # Devolver publicacion
    return post

#---------------- ELIMINACIÓN DE PUBLICACION 
# Determinando un codigo de estado para confirmar eliminación
@app.delete("/api/posts/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(request: Request, post_id: int, db: Annotated[Session, Depends(get_db)]):
#se realiza la consulta de publicaciones en la BD por ID
    result = db.execute(select(models.Post).where(models.Post.id == post_id))
    post = result.scalars().first()
#si la publicacion no existe
    if not post:
        #generar excepcyion http 404 indicando que no se encontro la busqueda
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Publicación no encontrada")
    
    # Eliminando publicacion de la BD
    db.delete(post)
    db.commit()
    
##""" -------------- VALIDACION Y ERRORES -------------- """

#""" CONTROLADOR DE EXCEPCIONES DE VALIDAACION RUTAS DEL NAVEGADOR """
#Capture el control de excepciones
@app.exception_handler(StarletteHTTPException)
# se guarda y recibe en request: Request,.... 
def general_http_exception_handler(request: Request, exception: StarletteHTTPException):
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
def validation_exception_handler(request: Request, exception: RequestValidationError):
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