#Importar FastAPI
from fastapi import FastAPI, Request
#Importar respuesta HTML
from fastapi.responses import HTMLResponse
#Importar archivos estaticos para reconcoer estilos css
from fastapi.staticfiles import StaticFiles 
#importar plantillas Jinja2 (requieren el objeto Request importado arriba)
from fastapi.templating import Jinja2Templates
#importar extension HTPP y status para respuestas de error
from fastapi import HTTPException, status

#--------controladores de Excepciones de error
#errores de validacion(si pide int y se recibe string)
from fastapi.exceptions import RequestValidationError 
# respuetas JSON para devolver espuestas desde el controlador de excepciones
from fastapi.responses import JSONResponse 
# manejo de errores desde la web frontend e indicar el error 
from starlette.exceptions import HTTPException as StarletteHTTPException


#inicializar app FastAPI
app =  FastAPI()

#Indicar a FastAPI donde encontrar los directorios estatucis (CSS, JS, IMG)
# (ruta de accesos de app / ruta de la carpeta en proyecto / nombre de referencia)
app.mount("/static", StaticFiles(directory="crud/static"), name="static")


#Indicar a FastAPI donde encontrar las plantillas de Jinja2
templates = Jinja2Templates(directory="crud/templates")

# directorio de ejemplo para publicaciones
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


#Devolver en formato JSON
"""
@app.get("/")
async - funcion asincrona para enviar y resivir datos
async def root():
    return {"message":"Hello FastAPI"}"""

#Devolver en formato HTML
"""incluinclude_in_schema=False, no incluira en la documentacion la ruta
@app.get("/", response_class=HTMLResponse, include_in_schema=False)"""





# ruta raiz / indicar que utilizara HTML / ruta raiz es igual home en name
@app.get("/", response_class=HTMLResponse, name="home")
#async - funcion asincrona para enviar y resivir datos

#Establecer una parametro de solicitud, Jinja2 requiere
async def home(request: Request): 
    
        #Devolvemos la solicitud request con el archivo de platilla / diccionario de publicaciones / los titulos de cada pulicación
                                                        #solicitud request / posts de diccionario posts / titulos a home
        #return templates.TemplateResponse(request=request, name="index.html", {"request": request, "posts": "posts", "title": "Home"})
        return templates.TemplateResponse("index.html", {"request": request, "posts": posts, "title": "Home"},)




#Ruta por ID o parametro de ruta
@app.get("/posts/{post_id}", include_in_schema=False)
def post_page(request: Request, post_id: int): #buscar publicacion especifica por id / entero
    #recorer publicaciones, buscando la solicitada
    for post in posts:
        #si la publicacion es encontrada
        if post.get("id") == post_id:
            #establecer titulo de la publicacion / solo los primeros 50 caracteres del titulo
            title = post["title"][:50]
            #retornara la publicacion buscada - plantilla / solicitud request / post de direccioanrio / titulo del post
            return templates.TemplateResponse("post.html", {"request": request, "post": post, "title": title},)
        #generar excepcyion http 404 indicando que no se encontro la busqueda
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post no encontrado")


""" CONTROLADOR DE EXCEPCIONES DE VALIDAACION RUTAS DEL NAVEGADOR """
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

""" ERRORES DE VALIDADCION  RUTAS DE FASTAPI"""
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