
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