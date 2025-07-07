# models.py
from sqlalchemy import Column, Integer, String, Date, ForeignKey, Float
from sqlalchemy.orm import relationship
from database import Base

class Empleado(Base):
    __tablename__ = "Empleados"
    EmpleadoID = Column(Integer, primary_key=True, index=True)
    Nombre = Column(String)
    Puesto = Column(String)
    FechaIngreso = Column(Date)
    ventas = relationship("Venta", back_populates="empleado")

class Venta(Base):
    __tablename__ = "Ventas"
    VentaID = Column(Integer, primary_key=True, index=True)
    Fecha = Column(Date)
    EmpleadoID = Column(Integer, ForeignKey("Empleados.EmpleadoID"))
    Total = Column(Float)

    empleado = relationship("Empleado", back_populates="ventas")
    detalles = relationship("DetalleVenta", back_populates="venta")

class DetalleVenta(Base):
    __tablename__ = "DetalleVentas"
    DetalleID = Column(Integer, primary_key=True, index=True)
    VentaID = Column(Integer, ForeignKey("Ventas.VentaID"))
    ProductoID = Column(Integer, ForeignKey("Productos.ProductoID"))
    Cantidad = Column(Integer)
    PrecioUnitario = Column(Float)
    Subtotal = Column(Float)

    venta = relationship("Venta", back_populates="detalles")
    producto = relationship("Producto", back_populates="detalles")

class Producto(Base):
    __tablename__ = "Productos"
    ProductoID = Column(Integer, primary_key=True, index=True)
    Nombre = Column(String)
    CategoriaID = Column(Integer, ForeignKey("Categorias.CategoriaID"))
    Precio = Column(Float)
    Stock = Column(Integer)
    Descripcion = Column(String)
    ProveedorID = Column(Integer, ForeignKey("Proveedores.ProveedorID"))
    FechaIngreso = Column(Date)

    detalles = relationship("DetalleVenta", back_populates="producto")

class Categoria(Base):
    __tablename__ = "Categorias"
    CategoriaID = Column(Integer, primary_key=True, index=True)
    Nombre = Column(String)
    Descripcion = Column(String)

class Proveedor(Base):
    __tablename__ = "Proveedores"
    ProveedorID = Column(Integer, primary_key=True, index=True)
    Nombre = Column(String)
    Telefono = Column(String)
    Email = Column(String)
    Direccion = Column(String)
