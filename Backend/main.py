from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from database import SessionLocal, engine
import models, schemas
from fastapi.middleware.cors import CORSMiddleware

# Crear tablas (en desarrollo)
models.Base.metadata.create_all(bind=engine)

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


# === EMPLEADOS ===
@app.post("/empleados/", response_model=schemas.Empleado)
def crear_empleado(empleado: schemas.EmpleadoCreate, db: Session = Depends(get_db)):
    db_empleado = models.Empleado(**empleado.dict())
    db.add(db_empleado)
    db.commit()
    db.refresh(db_empleado)
    return db_empleado

@app.get("/empleados/", response_model=list[schemas.Empleado])
def listar_empleados(db: Session = Depends(get_db)):
    return db.query(models.Empleado).all()


# === PROVEEDORES ===
@app.post("/proveedores/", response_model=schemas.Proveedor)
def crear_proveedor(proveedor: schemas.ProveedorCreate, db: Session = Depends(get_db)):
    db_obj = models.Proveedor(**proveedor.dict())
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj

@app.get("/proveedores/", response_model=list[schemas.Proveedor])
def listar_proveedores(db: Session = Depends(get_db)):
    return db.query(models.Proveedor).all()


# === CATEGORÍAS ===
@app.post("/categorias/", response_model=schemas.Categoria)
def crear_categoria(cat: schemas.CategoriaCreate, db: Session = Depends(get_db)):
    db_obj = models.Categoria(**cat.dict())
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj

@app.get("/categorias/", response_model=list[schemas.Categoria])
def listar_categorias(db: Session = Depends(get_db)):
    return db.query(models.Categoria).all()


# === PRODUCTOS ===
@app.post("/productos/", response_model=schemas.Producto)
def crear_producto(prod: schemas.ProductoCreate, db: Session = Depends(get_db)):
    db_obj = models.Producto(**prod.dict())
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj

@app.get("/productos/", response_model=list[schemas.Producto])
def listar_productos(db: Session = Depends(get_db)):
    return db.query(models.Producto).all()


# === VENTAS ===
@app.post("/ventas/", response_model=schemas.Venta)
def crear_venta(venta: schemas.VentaCreate, db: Session = Depends(get_db)):
    db_obj = models.Venta(**venta.dict())
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj

@app.get("/ventas/", response_model=list[schemas.Venta])
def listar_ventas(db: Session = Depends(get_db)):
    return db.query(models.Venta).all()


# === DETALLE DE VENTAS ===
@app.post("/detalleventas/", response_model=schemas.DetalleVenta)
def crear_detalle_venta(detalle: schemas.DetalleVentaCreate, db: Session = Depends(get_db)):
    db_obj = models.DetalleVenta(**detalle.dict())
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj

@app.get("/detalleventas/", response_model=list[schemas.DetalleVenta])
def listar_detalles_venta(db: Session = Depends(get_db)):
    return db.query(models.DetalleVenta).all()
