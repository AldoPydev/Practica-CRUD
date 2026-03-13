# importando libreria de Hora y Fecha
from datetime import datetime
# Importando libreria pydantic y modulos
from pydantic import BaseModel, ConfigDict, EmailStr,Field
# BaseModel - La clase base de la cual heredan todos los modelos
# ConfigDict - las 2 dorma de configurar modelos de pydantic
# EmailStr - Validacion de Email
# Field - Field le dice cómo debe comportarse, validarse y mostrarse.


""" Esquemas para Usuarios """
class UserBase(BaseModel):
    # datrtos proporciuonados por el usuario
    username: str = Field(min_length=1, max_length=50)
    email: str = Field(max_length=120)

# Esquema de creacion de publicaciones que hereda de la clase base
class UserCreate(UserBase):
    pass

# Esquema de respuesta para las publicaciones que hereda de la clase base
class UserResponse(UserBase):
        #indicar a Pydantic , puede leer clases con atributos además de diccionarios
    model_config = ConfigDict(from_attributes=True)
    
    # Campos de respuesta no dada por el usuario
    id: int 
    # para la ruta de la imagen de perfil
    image_file: str | None
    image_path: str

# Esqueme de actualización
class UserUpdate(BaseModel):
    # datrtos proporciuonados por el usuario
    username: str | None = Field(default=None, min_length=1, max_length=50)
    email: str | None = Field(default=None, max_length=120)
    image_file: str | None = Field(default=None, min_length=1, max_length=200)
    

""" Esquemas para publicaiones """
# Crear esquema base con campos compartidos  entre la devoluacion y creacion de publicaciones
# Determinando campos obligatorios al no colocar valores
# Etableciendo una longitud minima  y maxima
class PostBase(BaseModel):
    title: str = Field(min_length=1, max_length=100)
    content: str = Field(min_length=1)

# Esquema de creacion de publicaciones que hereda de la clase base
class PostCreate(PostBase):
    # Indicamos el ID del usuario, quien crea la publicacion
    user_id: int # TEMPORAL 



# Esquema de actualización
# El usuario podra actializar lo que necesite y no todos lo campos
class PostUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=100)
    content: str | None= Field(default=None, min_length=1)



# Esquema de respuesta para las publicaciones que hereda de la clase base
class PostResponse(PostBase):
    #indicar a Pydantic , puede leer clases con atributos además de diccionarios
    model_config = ConfigDict(from_attributes=True)
    
    # Campos de respuesta no dada por el usuario
    id: int 
    user_id: int
    date_posted: datetime # asignar hora y fecha a la publicación
    author: UserResponse # Opteniendo un JASON anidado con todos los datos del usuario