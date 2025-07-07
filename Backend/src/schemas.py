from pydantic import BaseModel
from datetime import date
from typing import List, Optional


# ----- EMPLEADOS -----
class EmpleadoBase(BaseModel):
    Nombre: str
    Puesto: str
    FechaIngreso: date

class EmpleadoCreate(EmpleadoBase):
    pass

class Empleado(EmpleadoBase):
    EmpleadoID: int
    class Config:
        orm_mode = True


# ----- PROVEEDORES -----
class ProveedorBase(BaseModel):
    Nombre: str
    Telefono: str
    Email: str
    Direccion: str

class ProveedorCreate(ProveedorBase):
    pass

class Proveedor(ProveedorBase):
    ProveedorID: int
    class Config:
        orm_mode = True


# ----- CATEGORÍAS -----
class CategoriaBase(BaseModel):
    Nombre: str
    Descripcion: str

class CategoriaCreate(CategoriaBase):
    pass

class Categoria(CategoriaBase):
    CategoriaID: int
    class Config:
        orm_mode = True


# ----- PRODUCTOS -----
class ProductoBase(BaseModel):
    Nombre: str
    CategoriaID: int
    Precio: float
    Stock: int
    Descripcion: str
    ProveedorID: int
    FechaIngreso: date

class ProductoCreate(ProductoBase):
    pass

class Producto(ProductoBase):
    ProductoID: int
    class Config:
        orm_mode = True


# ----- DETALLE VENTAS -----
class DetalleVentaBase(BaseModel):
    VentaID: int
    ProductoID: int
    Cantidad: int
    PrecioUnitario: float
    Subtotal: float

class DetalleVentaCreate(DetalleVentaBase):
    pass

class DetalleVenta(DetalleVentaBase):
    DetalleID: int
    class Config:
        orm_mode = True


# ----- VENTAS -----
class VentaBase(BaseModel):
    Fecha: date
    EmpleadoID: int
    Total: float

class VentaCreate(VentaBase):
    pass

class Venta(VentaBase):
    VentaID: int
    class Config:
        orm_mode = True
