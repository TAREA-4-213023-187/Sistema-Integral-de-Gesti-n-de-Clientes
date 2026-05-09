import tkinter as tk
from tkinter import messagebox, ttk
from datetime import datetime
import re
from abc import ABC, abstractmethod

# ====== SOFTWARE FJ ======
# ====== EXCEPCIONES PERSONALIZADAS ======

class SistemaError(Exception):
    pass

class ClienteError(SistemaError):
    pass

class ReservaError(SistemaError):
    pass

# ====== LOGGER ======

def log_error(mensaje):
    with open("logs.txt", "a") as f:
        f.write(f"{datetime.now()} - ERROR: {mensaje}\n")

# ====== CLASE ABSTRACTA ======

class Entidad(ABC):
    def __init__(self, id):
        self.id = id

    @abstractmethod
    def mostrar_info(self):
        pass

# ====== CLIENTE ======

class Cliente(Entidad):
    def __init__(self, id, nombre, email):
        super().__init__(id)
        self.set_nombre(nombre)
        self.set_email(email)

    def set_nombre(self, nombre):
        if not nombre:
            raise ClienteError("El nombre del cliente no puede estar vacío")
        self._nombre = nombre

    def set_email(self, email):
        if "@" not in email:
            raise ClienteError("El email no tiene un formato válido")
        self._email = email

    def mostrar_info(self):
        return f"{self._nombre} - {self._email}"
    
class Servicio(ABC):
    def __init__(self, nombre, precio_base):
        self._nombre = nombre
        self._precio_base = precio_base

    @abstractmethod
    def calcular_costo(self, *args):
        pass

<<<<<<< HEAD
    @abstractmethod
    def descripcion(self):
        pass
=======
        @abstractmethod
        def descripcion(self):
            pass
# ====== aporte kevin camargo =====
# ====== SERVICIOS (POLIMORFISMO) ======

class Servicio(ABC):
    def __init__(self, nombre, precio_base):
        self.nombre = nombre
        self.precio_base = precio_base

    @abstractmethod
    def calcular_costo(self, cantidad):
        pass

    @abstractmethod
    def descripcion(self):
        pass

class ReservaSalas(Servicio):
    def calcular_costo(self, horas, limpieza=True):
        # Sobrecarga lógica: costo por horas + cargo de limpieza opcional
        adicional = 15.0 if limpieza else 0.0
        return (self.precio_base * horas) + adicional

    def descripcion(self):
        return f"Servicio: {self.nombre} (Reserva de Sala por hora)"

class AlquilerEquipos(Servicio):
    def calcular_costo(self, dias):
        # Descuento si alquila más de 5 días
        total = self.precio_base * dias
        if dias > 5:
            total *= 0.90  # 10% descuento
        return total

    def descripcion(self):
        return f"Servicio: {self.nombre} (Alquiler de equipo especializado)"

class AsesoriaEspecializada(Servicio):
    def calcular_costo(self, sesiones):
        return self.precio_base * sesiones

    def descripcion(self):
        return f"Servicio: {self.nombre} (Asesoría Técnica)"

# ====== CLASE RESERVA ======

class Reserva:
    def __init__(self, id_reserva, cliente, servicio, cantidad):
        self.id = id_reserva
        self.cliente = cliente
        self.servicio = servicio
        self.cantidad = cantidad
        self.estado = "Pendiente"

    def confirmar(self):
        try:
            if self.cantidad <= 0:
                raise ReservaError(f"Cantidad inválida ({self.cantidad}) para la reserva {self.id}")
            
            costo_final = self.servicio.calcular_costo(self.cantidad)
            self.estado = "Confirmada"
            log_evento(f"Reserva {self.id} CONFIRMADA. Cliente: {self.cliente.id}. Total: ${costo_final}")
            return costo_final
            
        except ReservaError as e:
            self.estado = "Fallida"
            log_evento(str(e), "ERROR")
            raise 
        except Exception as e:
            log_evento(f"Error inesperado en Reserva {self.id}: {e}", "CRITICAL")
            raise ReservaError("Error interno al procesar reserva.")
>>>>>>> 92191a151aebd80e2f9ca1b198157ddb203fbb53
