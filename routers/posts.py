#Importacion modulo asincrono
import asyncio
from typing import Annotated
#Importar FastAPI
from fastapi import FastAPI, Request, APIRouter
#importar extension HTPP y status para respuestas de error / Dependencias 
from fastapi import HTTPException, status, Depends

#----------------------- Importar Schemas
from schemas import (
    PostCreate, 
    PostResponse, 
    PostUpdate,
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


#----------------------- Inicializar enrutador
router = APIRouter()

# ------------- RUTAS DE PUBLICACIONES ------------------



# Responder con lista de respuesta de publicaciones en la siguiente ruta
# Validar que cada publicacion coincida con el modelo de despuesta de publiacion
@router.get("", response_model=list[PostResponse])
async def get_posts(db: Annotated[Session, Depends(get_db)]):
    result = db.execute(select(models.Post))
    posts = result.scalars().all()
    return posts

# RUTA Crear Publicación
@router.post(
    "",
    response_model=PostResponse, #modelo de respuesta 
    status_code=status.HTTP_201_CREATED #indicando que el recurso se a creado
)

# ------------------ FUNCION CREACION DE PUBLICACION
# Utilizando schema de creacion, validando con nuestra esquema  
# Establecer sesion con BD y verificar primero si el usuario existe 
async def create_post(post: PostCreate, db: Annotated[Session, Depends(get_db)]):
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



#---------------- ACTUALIZAR PUBLICACION COMPLETA 
#Ruta de actualizacion de post - reutilizando postcreate por tener todo ya hecho
@router.put("/{post_id}", response_model=PostResponse)
async def update_post_full(request: Request, post_id: int, post_data: PostCreate,db: Annotated[Session, Depends(get_db)]):
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
@router.patch("/{post_id}", response_model=PostResponse)
async def update_post_partial(request: Request, post_id: int, post_data: PostUpdate, db: Annotated[Session, Depends(get_db)]):
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
@router.delete("/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(request: Request, post_id: int, db: Annotated[Session, Depends(get_db)]):
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