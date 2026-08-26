"""
servidor_web.py
Servidor web con FastAPI que gestiona productos en memoria.
Endpoints:
- GET /api/v1/health
- GET /api/v1/productos
- POST /api/v1/productos
- Cualquier otra ruta -> 404
"""

from fastapi import FastAPI, HTTPException, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from datetime import datetime
from typing import List

# ============================================
# 1. Definición del modelo de datos para validación
# ============================================
class ProductoCreate(BaseModel):
    """Modelo para la creación de un producto (POST)"""
    nombre: str = Field(..., min_length=1, description="Nombre del producto")
    precio: float = Field(..., gt=0, description="Precio del producto (mayor a 0)")

class Producto(ProductoCreate):
    """Modelo completo de producto (id opcional si se desea)"""
    # Podríamos agregar un id, pero la consigna no lo pide

# ============================================
# 2. Almacenamiento en memoria
# ============================================
productos: List[Producto] = []  # Lista simple en memoria

# ============================================
# 3. Instancia de la aplicación FastAPI
# ============================================
app = FastAPI(title="API de Productos", description="Servidor local para gestión de productos")

# ============================================
# 4. Manejador de errores de validación -> 400 Bad Request
# ============================================
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    """Convierte los errores de validación de Pydantic en 400 Bad Request"""
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"error": "Datos inválidos", "detalles": exc.errors()}
    )

# ============================================
# 5. Endpoints
# ============================================

@app.get("/api/v1/health", status_code=status.HTTP_200_OK)
async def health_check():
    """
    Retorna el estado del servidor y timestamp actual.
    """
    return {
        "status": "online",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/api/v1/productos", response_model=List[Producto], status_code=status.HTTP_200_OK)
async def listar_productos():
    """
    Retorna la lista de todos los productos almacenados en memoria.
    """
    return productos

@app.post("/api/v1/productos", status_code=status.HTTP_201_CREATED)
async def crear_producto(producto: ProductoCreate):
    """
    Recibe un JSON con nombre y precio, lo valida, lo agrega a la lista en memoria
    y retorna el producto creado con código 201.
    Si falta algún campo o es inválido, responde 400 (gracias al manejador anterior).
    """
    # Convertimos el modelo validado a un objeto Producto (o simplemente lo guardamos)
    nuevo_producto = Producto(**producto.dict())
    productos.append(nuevo_producto)
    return {"mensaje": "Producto creado", "producto": nuevo_producto}

# ============================================
# 6. Manejo de rutas no encontradas (404) - opcional
# ============================================
# FastAPI ya devuelve 404 automáticamente para rutas no definidas.
# Si queremos personalizar el mensaje, podemos agregar un exception_handler para 404:
@app.exception_handler(404)
async def custom_404_handler(request, exc):
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={"error": "Not found"}
    )

# ============================================
# 7. (Opcional) Concurrencia - explicación
# ============================================
"""
FastAPI es asíncrono por naturaleza (basado en Starlette). Por defecto,
cuando ejecutamos con uvicorn, maneja múltiples peticiones concurrentes
usando asyncio. Cada endpoint async se ejecuta en el event loop.

Si quisiéramos escalar aún más (usar múltiples workers), podríamos ejecutar:
    uvicorn servidor_web:app --host 0.0.0.0 --port 8080 --workers 4

Pero en ese caso, el almacenamiento en memoria (lista productos) NO sería
compartido entre workers. Para compartir estado entre workers necesitaríamos
una base de datos externa (Redis, etc.).

Si solo usamos un worker (que es lo normal para desarrollo), el almacenamiento
en memoria es seguro porque FastAPI maneja las peticiones de forma asíncrona
y secuencial dentro del mismo proceso (no hay condiciones de carrera si
no usamos variables compartidas sin protección). Si hubiera operaciones
que requieran sincronización (ej. incrementar un contador), podríamos usar
un lock asíncrono (asyncio.Lock) o dependencias con estado.

Ejemplo de lock para evitar condiciones de carrera:
    from asyncio import Lock
    lock = Lock()
    async def modificar_recurso():
        async with lock:
            # operación crítica
            pass

Para este ejercicio simple, no es necesario.
"""

# ============================================
# 8. Punto de entrada si se ejecuta directamente
# ============================================
if __name__ == "__main__":
    import uvicorn
    # Ejecutar el servidor en el puerto 8080, con recarga automática (útil en desarrollo)
    uvicorn.run(
        "servidor_web:app",
        host="127.0.0.1",
        port=8080,
        reload=True,  # Reinicia ante cambios en el código (solo para desarrollo)
        log_level="info"
    )