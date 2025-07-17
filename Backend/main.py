from fastapi import FastAPI, Depends, HTTPException, UploadFile, File
import os
from sqlalchemy.orm import Session
from database import SessionLocal, engine
import models, schemas
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from barcode import EAN13, Code128
from barcode.writer import ImageWriter
import random
from typing import Optional
from pydantic import BaseModel
from PIL import Image
import io
import pyzbar.pyzbar as pyzbar
import logging
import uuid

# Configuración de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Crear tablas (en desarrollo)
models.Base.metadata.create_all(bind=engine)
# Configura el puerto desde la variable de entorno o usa 8000 por defecto
port = int(os.environ.get("PORT", 8000))

app = FastAPI()

# CORS (opcional)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # cámbialo para producción
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dependencia DB
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
def root():
    return {"message": "API Punto de Venta (FastAPI + PostgreSQL)"}

# === MODELOS PARA CÓDIGOS DE BARRAS ===
class BarcodeRequest(BaseModel):
    barcode_type: Optional[str] = "ean13"  # o "code128"
    filename: Optional[str] = None

# === FUNCIONES PARA CÓDIGOS DE BARRAS ===
def generate_random_ean13_id():
    """Genera un ID válido para EAN13 (12 dígitos + checksum)"""
    random_digits = ''.join([str(random.randint(0, 9)) for _ in range(11)])
    first_digit = str(random.randint(1, 9))  # El primer dígito debe ser diferente de 0
    return first_digit + random_digits

def generate_random_code128_id():
    """Genera un ID alfanumérico aleatorio para Code128"""
    chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-"
    length = random.randint(8, 15)
    return ''.join(random.choice(chars) for _ in range(length))

def clean_temp_files():
    """Limpia archivos temporales de códigos de barras"""
    for filename in os.listdir():
        if filename.startswith("barcode_") and filename.endswith(".png"):
            try:
                os.remove(filename)
            except:
                pass

# === ENDPOINTS PARA CÓDIGOS DE BARRAS ===
@app.post("/generate-barcode")
async def generate_barcode(request: BarcodeRequest):
    try:
        # Generar ID aleatorio según el tipo
        if request.barcode_type.lower() == "ean13":
            product_id = generate_random_ean13_id()
            barcode_class = EAN13
        elif request.barcode_type.lower() == "code128":
            product_id = generate_random_code128_id()
            barcode_class = Code128
        else:
            raise HTTPException(status_code=400, detail="Tipo de código de barras no soportado")

        # Nombre del archivo
        filename = request.filename or f"barcode_{uuid.uuid4().hex}"
        
        # Generar el código de barras
        barcode = barcode_class(product_id, writer=ImageWriter())
        filepath = barcode.save(filename)
        
        # Devolver la imagen generada
        return FileResponse(
            path=filepath,
            media_type="image/png",
            filename=f"{filename}.png"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        clean_temp_files()

@app.post("/productos/escaneo/")
async def escanear_codigo_barras(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    Endpoint para escanear códigos de barras desde imágenes y obtener el producto correspondiente.
    Soporta formatos: PNG, JPEG, JPG, WEBP
    """
    try:
        # Validar el tipo de archivo
        content_type = file.content_type
        if content_type not in ["image/png", "image/jpeg", "image/jpg", "image/webp"]:
            raise HTTPException(
                status_code=400,
                detail="Formato de imagen no soportado. Use PNG, JPEG o WEBP"
            )

        # Leer y procesar la imagen
        image_data = await file.read()
        image = Image.open(io.BytesIO(image_data))

        # Convertir a escala de grises para mejor detección
        image = image.convert('L')

        # Decodificar códigos de barras
        decoded_objects = pyzbar.decode(image)
        if not decoded_objects:
            logger.warning("No se detectaron códigos de barras en la imagen")
            raise HTTPException(
                status_code=400,
                detail="No se detectó ningún código de barras en la imagen"
            )

        # Procesar todos los códigos encontrados
        productos = []
        for obj in decoded_objects:
            codigo = obj.data.decode('utf-8')
            producto = db.query(models.Producto).filter(
                models.Producto.codigo_barras == codigo
            ).first()
            
            if producto:
                productos.append(producto)
            else:
                logger.info(f"Código detectado pero no encontrado en BD: {codigo}")

        if not productos:
            raise HTTPException(
                status_code=404,
                detail="Los códigos detectados no corresponden a productos registrados"
            )

        return {
            "detectados": len(decoded_objects),
            "encontrados": len(productos),
            "productos": productos
        }

    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Error procesando imagen: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error al procesar la imagen: {str(e)}"
        )

# === ENDPOINTS EXISTENTES (MANTENIDOS) ===
# [Tus endpoints existentes para empleados, proveedores, categorías, etc.]
# ... (todo el código existente que no está relacionado con códigos de barras)

# === ENDPOINTS MEJORADOS PARA PRODUCTOS ===
@app.post("/productos/", response_model=schemas.Producto)
def crear_producto(prod: schemas.ProductoCreate, db: Session = Depends(get_db)):
    # Generar código de barras automáticamente si no se proporciona
    if not prod.codigo_barras:
        product_id = generate_random_ean13_id()
        prod.codigo_barras = product_id
    else:
        # Validar que el código no exista
        existente = db.query(models.Producto).filter(
            models.Producto.codigo_barras == prod.codigo_barras
        ).first()
        if existente:
            raise HTTPException(
                status_code=400,
                detail="El código de barras ya está en uso por otro producto"
            )
    
    db_obj = models.Producto(**prod.dict())
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj

@app.get("/productos/por-codigo/{codigo}")
def obtener_producto_por_codigo(codigo: str, db: Session = Depends(get_db)):
    producto = db.query(models.Producto).filter(
        models.Producto.codigo_barras == codigo
    ).first()
    
    if not producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    
    return producto

@app.get("/productos/{producto_id}/barcode")
def obtener_codigo_barras_producto(producto_id: int, db: Session = Depends(get_db)):
    producto = db.query(models.Producto).filter(models.Producto.id == producto_id).first()
    if not producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    
    if not producto.codigo_barras:
        raise HTTPException(status_code=400, detail="El producto no tiene código de barras asignado")
    
    try:
        # Generar la imagen del código de barras
        barcode = EAN13(producto.codigo_barras, writer=ImageWriter())
        filepath = barcode.save(f"product_barcode_{producto.id}")
        
        return FileResponse(
            path=filepath,
            media_type="image/png",
            filename=f"barcode_{producto.id}.png"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al generar código de barras: {str(e)}")
    finally:
        clean_temp_files()

# Inicia el servidor
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=port)