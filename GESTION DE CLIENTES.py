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

class ReservaSala(Servicio):
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

# ==========================================================
# ====== APORTE ESTUDIANTE: MANEJO CENTRAL DEL SISTEMA =====
# ==========================================================
# Autor: HARMINSOND ALONSO ALVAREZ GUERRERO
#
# Este módulo se encarga de:
#  Administrar clientes
#  Administrar servicios
#  Gestionar reservas
#  Controlar excepciones
#  Registrar eventos y errores
#  Mantener listas internas del sistema
#  Mostrar estadísticas
# ==========================================================

# Función encargada de registrar eventos y errores
# dentro del archivo logs.txt

def log_evento(mensaje, tipo="INFO"):

    with open("logs.txt", "a", encoding="utf-8") as archivo:

        archivo.write(
            f"{datetime.now()} [{tipo}] {mensaje}\n"
        )


# Clase principal encargada de administrar
# el funcionamiento general del sistema

class SistemaGestion:


    # Constructor de la clase
    # Inicializa las listas principales del sistema

    def __init__(self):

        self.clientes = []
        self.servicios = []
        self.reservas = []

        log_evento("Sistema de gestión iniciado")


    # Método para registrar clientes
    # Valida que no existan IDs duplicados

    def agregar_cliente(self, cliente):

        try:

            # Verifica que el objeto sea de tipo Cliente
            if not isinstance(cliente, Cliente):

                raise ClienteError(
                    "El objeto enviado no corresponde a un cliente válido"
                )

            # Validación de IDs repetidos
            for c in self.clientes:

                if c.id == cliente.id:

                    raise ClienteError(
                        f"Ya existe un cliente con ID {cliente.id}"
                    )

            # Agrega el cliente a la lista
            self.clientes.append(cliente)

        except ClienteError as e:

            log_evento(str(e), "ERROR")

            print("ERROR:", e)

        else:

            log_evento(
                f"Cliente agregado correctamente: {cliente.id}"
            )

            print("Cliente registrado correctamente")

        finally:

            print("Proceso de registro de cliente finalizado\n")


    # Método para agregar servicios al sistema

    def agregar_servicio(self, servicio):

        try:

            # Verifica que el objeto pertenezca
            # a la clase Servicio
            if not isinstance(servicio, Servicio):

                raise SistemaError(
                    "El objeto enviado no es un servicio válido"
                )

            self.servicios.append(servicio)

        except SistemaError as e:

            log_evento(str(e), "ERROR")

            print("ERROR:", e)

        else:

            log_evento(
                f"Servicio agregado: {servicio.nombre}"
            )

            print("Servicio registrado correctamente")


    # Método encargado de crear reservas
    # y validar clientes y servicios registrados

    def crear_reserva(self, reserva):

        try:

            # Verifica que sea una reserva válida
            if not isinstance(reserva, Reserva):

                raise ReservaError(
                    "La reserva enviada no es válida"
                )

            # Comprueba que el cliente exista
            if reserva.cliente not in self.clientes:

                raise ReservaError(
                    "El cliente no está registrado en el sistema"
                )

            # Comprueba que el servicio exista
            if reserva.servicio not in self.servicios:

                raise ReservaError(
                    "El servicio no está registrado"
                )

            # Procesa la reserva
            costo = reserva.confirmar()

            # Guarda la reserva
            self.reservas.append(reserva)

        except ReservaError as e:

            log_evento(str(e), "ERROR")

            print("ERROR:", e)

        except Exception as e:

            # Encadenamiento de excepciones
            log_evento(
                f"Error inesperado creando reserva: {e}",
                "CRITICAL"
            )

            raise ReservaError(
                "Error interno procesando la reserva"
            ) from e

        else:

            log_evento(
                f"Reserva {reserva.id} creada correctamente"
            )

            print(
                f"Reserva confirmada exitosamente. "
                f"Total: ${costo}"
            )

        finally:

            print("Proceso de reserva finalizado\n")


    # Método para cancelar reservas existentes

    def cancelar_reserva(self, id_reserva):

        try:

            reserva_encontrada = False

            # Recorre la lista de reservas
            for reserva in self.reservas:

                if reserva.id == id_reserva:

                    reserva_encontrada = True

                    # Verifica si ya fue cancelada
                    if reserva.estado == "Cancelada":

                        raise ReservaError(
                            "La reserva ya fue cancelada"
                        )

                    # Cambia el estado
                    reserva.estado = "Cancelada"

                    log_evento(
                        f"Reserva {id_reserva} cancelada correctamente"
                    )

                    print("Reserva cancelada correctamente")

            # Si no existe la reserva
            if not reserva_encontrada:

                raise ReservaError(
                    f"No existe la reserva con ID {id_reserva}"
                )

        except ReservaError as e:

            log_evento(str(e), "ERROR")

            print("ERROR:", e)


    # Método para buscar clientes por ID

    def buscar_cliente(self, id_cliente):

        try:

            for cliente in self.clientes:

                if cliente.id == id_cliente:

                    return cliente

            raise ClienteError(
                f"No existe el cliente con ID {id_cliente}"
            )

        except ClienteError as e:

            log_evento(str(e), "ERROR")

            print("ERROR:", e)


    # Método para mostrar todos los clientes

    def mostrar_clientes(self):

        print("\n========== CLIENTES ==========")

        if len(self.clientes) == 0:

            print("No existen clientes registrados")

        else:

            for cliente in self.clientes:

                print(cliente.mostrar_info())


    # Método para mostrar los servicios registrados

    def mostrar_servicios(self):

        print("\n========== SERVICIOS ==========")

        if len(self.servicios) == 0:

            print("No existen servicios registrados")

        else:

            for servicio in self.servicios:

                print(servicio.descripcion())


    # Método para visualizar todas las reservas

    def mostrar_reservas(self):

        print("\n========== RESERVAS ==========")

        if len(self.reservas) == 0:

            print("No existen reservas registradas")

        else:

            for reserva in self.reservas:

                print(
                    f"Reserva ID: {reserva.id} | "
                    f"Cliente: {reserva.cliente._nombre} | "
                    f"Servicio: {reserva.servicio.nombre} | "
                    f"Estado: {reserva.estado}"
                )


    # Método encargado de mostrar estadísticas
    # generales del sistema

    def estadisticas(self):

        confirmadas = 0
        canceladas = 0
        pendientes = 0

        # Recorre las reservas para contar estados
        for reserva in self.reservas:

            if reserva.estado == "Confirmada":

                confirmadas += 1

            elif reserva.estado == "Cancelada":

                canceladas += 1

            else:

                pendientes += 1

        print("\n========== ESTADÍSTICAS ==========")

        print(f"Clientes registrados: {len(self.clientes)}")
        print(f"Servicios registrados: {len(self.servicios)}")
        print(f"Reservas registradas: {len(self.reservas)}")

        print(f"Reservas confirmadas: {confirmadas}")
        print(f"Reservas canceladas: {canceladas}")
        print(f"Reservas pendientes: {pendientes}")
