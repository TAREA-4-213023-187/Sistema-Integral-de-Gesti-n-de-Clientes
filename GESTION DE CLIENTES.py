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

