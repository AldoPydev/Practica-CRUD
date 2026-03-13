from sqlmodel import Field, Session, create_engine,select, SQLModel
from sqlalchemy.orm import DeclarativeBase, sessionmaker


# Establecer conexion con la base de datos
mysql_url = f'mysql+pymysql://root:emperadores24@localhost:3306/crud'
#SQLALCHEMY_DATABASE_URL = url='mysql+pymysql://root:emperadores24@localhost:3306/crud'
# Establecer conexion con la base de datos
engine = create_engine(
    mysql_url
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

