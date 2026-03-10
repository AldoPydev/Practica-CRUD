# Importando librerias para la conexion con base de datos 
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

# Establecer conexion con la base de datos
SQLALCHEMY_DATABASE_URL = " mysql+pymysql://root:emperadores24localhost:3306/crud"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
)

# Establecemos una sesion abierta por cada petición 
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Clase de declaracion de base de datos
class Base(DeclarativeBase):
    pass

# Funcion que declara las sesisiones para las rutas 
# Cada ruta necesita un sesion abeirta de BD para funcionar
def get_db():
    with SessionLocal() as db:
        yield db


