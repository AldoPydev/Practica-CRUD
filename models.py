# complemento para ser compatible alfunas funciones de Python 3.14 con
# versiones anteriores
from __future__ import annotations

# Importando la facha y hora, tomando la zona horaria 
from datetime import UTC, datetime

# Importando map colums de la base de datos
from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

# Importando la base de datos
from database import Base

# creando un modelo de usuario / tabla usuarios
class User(Base):
    # indicando el modelo de usuario es una tabla
    __tablename__ = "users"
    # Mapeando la ID en int indicando que es llave primaria y se genera automaticamente
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    # Nombre de usuario y correo con cadena y unicos, no se permite duplicados
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    email: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    # Mapeando la imagen de perfil indicando que solo guardara el nombre de la imagen
    image_file: Mapped[str | None] = mapped_column(
        String(200),
        nullable=True,
        default=None,
    )

    # Indicando - un mismo usuario puede tener multiples publicaciones
    # conviertiendolas en una lista o directorio / relacionando al autor con sus publicaciones
    posts: Mapped[list[Post]] = relationship(back_populates="author", cascade="all, delete-orphan")

    # Si el usuario a cargado una imagen de perfil  
    @property
    def image_path(self) -> str:
        if self.image_file:
            # Indicamos donde la va a guardar
            return f"/media/profile_pics/{self.image_file}"
        # de lo contrario le asigamos la imagen default
        return "/static/profile_pics/default.jpg"

# creando un modelo de publicaciones / tabla publicaciones
class Post(Base):
    __tablename__ = "posts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(100), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    # Indicamos que el usuario de be ser valido para poder crear publicaciones
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        nullable=False,
        # facilita busqueda el usuario que sea valido y coincida 
        index=True,
    )
     # estableciendo la zona horaria, para asiganarla a la publicacion creada
    date_posted: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
    )

    # vinculando el post creado con el autor / usuario
    author: Mapped[User] = relationship(back_populates="posts")