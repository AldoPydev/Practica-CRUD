#Importacion modulo asincrono
import asyncio
from typing import Annotated
#Importar FastAPI
from fastapi import FastAPI, Request, APIRouter
#importar extension HTPP y status para respuestas de error / Dependencias 
from fastapi import HTTPException, status, Depends

#----------------------- Importar Schemas
from schemas import (
    UserCreate, 
    UserResponse, 
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


#----------------------- Inicializar enrutador
router = APIRouter()

#""" -------------- RUTAS DE USUARIO -------------- """
# Crear Usuarios
@router.post(
    "",
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
@router.get("/api/user", response_model=list[UserResponse])
async def get_users(db: Annotated[Session, Depends(get_db)]):
    result = db.execute(select(models.User))
    users = result.scalars().all()
    return users

# ------------- RUTA POR ID BUSQUEDA DE USUARIOS ------------------
@router.get("/{user_id}", response_model=UserResponse)
async def get_user(user_id: int, db: Annotated[Session, Depends(get_db)]): 
    
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
@router.patch("/{user_id}", response_model=UserResponse)
async def update_user(
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
@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(user_id: int, db: Annotated[Session, Depends(get_db)]):
    result = db.execute(select(models.User).where(models.User.id == user_id))
    user = result.scalars().first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    db.delete(user)
    db.commit()