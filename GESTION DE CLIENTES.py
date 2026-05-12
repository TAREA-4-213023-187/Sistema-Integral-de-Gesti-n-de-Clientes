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

# ===== VALIDACIONES CLIENTE =====
# Validación de ID, Nombre y Correo electrónico

        if id <= 0:
            raise ClienteError(
                "El ID del cliente debe ser mayor a cero"
            )
        
        self.set_nombre(nombre)
        self.set_email(email)

    def set_nombre(self, nombre):

        if not nombre.strip():
            raise ClienteError(
                "El nombre del cliente no puede estar vacío"
            )
        
    # Validación que solo permita letras y espacios
        if not re.match(r"^[A-Za-zÁÉÍÓÚáéíóúñÑ ]+$", nombre):
            raise ClienteError(
                "El nombre solo debe contener letras"
            )
        self._nombre = nombre

    def set_email(self, email):

        # EXPRESIÓN REGULAR PARA VALIDAR FORMATO DE CORREO ELECTRÓNICO
        patron = r'^[\w\.-]+@[\w\.-]+\.\w+$'

        if not re.match(patron, email):
            raise ClienteError(
                "El email no tiene un formato válido"
            )
        self._email = email

    def mostrar_info(self):
        return f"{self._nombre} - {self._email}"


# ====== aporte kevin camargo =====
# ====== SERVICIOS (POLIMORFISMO) ======

class Servicio(ABC):
    def __init__(self, nombre, precio_base):

# ===== VALIDACIONES SERVICIO =====
# Verifica nombre y precio base válidos

        if not nombre.strip():
            raise SistemaError("El nombre del servicio no puede estar vacío")
        
        # Validar que el precio base sea positivo
        if precio_base <= 0:
            raise SistemaError("El precio base debe ser mayor a cero")
        
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
        return (self.precio_base * horas + adicional)

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

# ===== VALIDACIONES RESERVA =====
# Control de Cliente, Servicio y CantidadSS

        if id_reserva <= 0:
            raise ReservaError("El ID de la reserva debe ser mayor a cero")
        if not isinstance(cliente, Cliente):
            raise ReservaError("El cliente proporcionado no es válido")
        if not isinstance(servicio, Servicio):
            raise ReservaError("El servicio proporcionado no es válido")
        if cantidad <= 0:
            raise ReservaError("La cantidad debe ser mayor a cero")

        self.id = id_reserva
        self.cliente = cliente
        self.servicio = servicio
        self.cantidad = cantidad
        self.estado = "Pendiente"

    def confirmar(self):
        try:
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

    def cancelar(self):
        try:
            if self.estado == "Cancelada":
                raise ReservaError(
                    f"La reserva {self.id} ya fue cancelada"
                )
            
            if self.estado == "Finalizada":
                raise ReservaError(
                    f"La reserva {self.id} ya fue finalizada"
                )

            self.estado = "Cancelada"
            log_evento(f"Reserva {self.id} cancelada correctamente")
            print("Reserva cancelada correctamente")
        except ReservaError as e:
            log_evento(str(e), "ERROR")
            print("ERROR:", e)
            
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

            raise

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

            raise

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

            raise

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


# ==========================================================
# ====== INTERFAZ GRÁFICA DEL SISTEMA ======
# ==========================================================
# Autor: Ludy Marcela Monroy

class SistemaGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("SOFTWARE FJ - Sistema de Gestión de Clientes")
        self.root.geometry("1200x800")

        # Estilo para pestañas

        style = ttk.Style()

        style.configure("TNotebook.Tab", font=("Arial", 12, "bold"), padding=[20, 10])

        # Instancia del sistema de gestión
        self.sistema = SistemaGestion()

        # ===== VARIABLES DE CONTROL =====
        self.id_cliente_var = tk.StringVar()
        self.nombre_cliente_var = tk.StringVar()
        self.email_cliente_var = tk.StringVar()

        # ===== VARIABLES SERVICIOS =====
        self.nombre_servicio_var = tk.StringVar()
        self.precio_servicio_var = tk.StringVar()
        self.tipo_servicio_var = tk.StringVar()

        # ===== VARIABLES RESERVAS =====
        self.id_reserva_var = tk.StringVar()
        self.cantidad_reserva_var = tk.StringVar()

        self.cliente_reserva_var = tk.StringVar()
        self.servicio_reserva_var = tk.StringVar()

        # ===== TITULO PRINCIPAL =====
        titulo = tk.Label(
            root,
            text="SOFTWARE FJ - SISTEMA DE GESTIÓN",
            font=("Arial", 16, "bold"),
            fg="#333"
        )
        titulo.pack(pady=10)

        # ===========================================
        # ==== NOTEBOOK PARA SEPARAR SECCIONES ======
        # ===========================================

        notebook = ttk.Notebook(root)
        notebook.pack(padx=10, pady=10, fill="both", expand=True)

        # Pestañas
        tab_clientes = tk.Frame(notebook)
        tab_servicios =  tk.Frame(notebook)
        tab_reservas = tk.Frame(notebook)
        tab_estadisticas = tk.Frame(notebook)

        # Agregar Pestañas
        notebook.add(tab_clientes, text="Clientes")
        notebook.add(tab_servicios, text="Servicios")
        notebook.add(tab_reservas, text="Reservas")
        notebook.add(tab_estadisticas, text="Estadísticas")

        # Botón para mostrar estadísticas
        tk.Button(
            tab_estadisticas,
            text="Mostrar Estadísticas",
            command=self.mostrar_estadisticas,
            bg="lightgray",
            font=("Arial", 12, "bold"),
            width=20,
            height=2
        ).pack(pady=30)


        # ===== FRAME DE REGISTRO DE CLIENTES =====

        frame_clientes = tk.LabelFrame(
            tab_clientes,
            text="Registro de Clientes",
            padx=10,
            pady=10
        )

        frame_clientes.pack(padx=10, pady=10, fill="x")

        # ID del cliente
        tk.Label(frame_clientes, text="ID:").grid(row=0, column=0)

        tk.Entry(frame_clientes, textvariable=self.id_cliente_var).grid(row=0, column=1)

        # Nombre del cliente
        tk.Label(frame_clientes, text="Nombre:").grid(row=1, column=0)
        tk.Entry(frame_clientes, textvariable=self.nombre_cliente_var).grid(row=1, column=1)

        # Email del cliente
        tk.Label(frame_clientes, text="Email:").grid(row=2, column=0)
        tk.Entry(frame_clientes, textvariable=self.email_cliente_var).grid(row=2, column=1)

        # Botón para registrar cliente
        tk.Button(
            frame_clientes,
            text="Registrar Cliente",
            command=self.registrar_cliente, 
            bg="lightblue"
        ).grid(row=3, column=0, columnspan=2, pady=10)

        # ===========================================
        # ====== TABLA DE CLIENTES REGISTRADOS ======
        # ===========================================

        self.tabla_clientes = ttk.Treeview(
            tab_clientes,
            columns=("ID", "Nombre", "Email"),
            show="headings",
            height=8
        )

        self.tabla_clientes.heading("ID", text="ID")
        self.tabla_clientes.heading("Nombre", text="Nombre")
        self.tabla_clientes.heading("Email", text="Email")

        self.tabla_clientes.column("ID", anchor="center", width=100)
        self.tabla_clientes.column("Nombre", anchor="center", width=250)
        self.tabla_clientes.column("Email", anchor="center", width=300)

        self.tabla_clientes.pack(padx=10, pady=10, fill="both")

        # ====== FRAME REGISTRO DE SERVICIOS ======

        frame_servicios = tk.LabelFrame(
            tab_servicios,
            text="Registro de Servicios",
            padx=10,
            pady=10
        )

        frame_servicios.pack(padx=10, pady=10, fill="x")

        # Nombre del servicio
        tk.Label(frame_servicios, text="Nombre del Servicio:").grid(row=0, column=0)
        tk.Entry(frame_servicios, textvariable=self.nombre_servicio_var).grid(row=0, column=1)

        # Precio del servicio
        tk.Label(frame_servicios, text="Precio Base:").grid(row=1, column=0)
        tk.Entry(frame_servicios, textvariable=self.precio_servicio_var).grid(row=1, column=1)

        # Tipo de servicio
        tk.Label(frame_servicios, text="Tipo de Servicio:").grid(row=2, column=0)
        combo_tipo = ttk.Combobox(
            frame_servicios,
            textvariable=self.tipo_servicio_var,
            state="readonly"
        )
        combo_tipo['values'] = ("Reserva de Sala", "Alquiler de Equipos", "Asesoría Especializada")
        combo_tipo.grid(row=2, column=1)

        # Botón para registrar servicio
        tk.Button(
            frame_servicios,
            text="Registrar Servicio",
            command=self.registrar_servicio,
            bg="lightgreen"
        ).grid(row=3, column=0, columnspan=2, pady=10)

        # ===========================================
        # ====== TABLA DE SERVICIOS REGISTRADOS ======
        # ===========================================

        self.tabla_servicios = ttk.Treeview(
            tab_servicios,
            columns=("Nombre", "Precio", "Tipo"),
            show="headings",
            height=6
        )    

        self.tabla_servicios.heading("Nombre", text="Nombre del Servicio")
        self.tabla_servicios.heading("Precio", text="Precio")
        self.tabla_servicios.heading("Tipo", text="Tipo de Servicio")

        self.tabla_servicios.column("Nombre", anchor="center", width=250)
        self.tabla_servicios.column("Precio", anchor="center", width=150)
        self.tabla_servicios.column("Tipo", anchor="center", width=250)

        self.tabla_servicios.pack(padx=10, pady=10, fill="both")
        # ===========================================
        # ====== FRAME RESERVAS ======
        # ===========================================

        frame_reservas = tk.LabelFrame(
            tab_reservas,
            text="Gestión de Reservas",
            padx=10,
            pady=10
        )

        frame_reservas.pack(padx=10, pady=10, fill="x")

        # ID de la reserva
        tk.Label(frame_reservas, text="ID de Reserva:").grid(row=0, column=0)
        tk.Entry(frame_reservas, textvariable=self.id_reserva_var).grid(row=0, column=1)

        # Cliente para la reserva
        tk.Label(frame_reservas, text="Cliente:").grid(row=1, column=0)
        self.combo_clientes = ttk.Combobox(
            frame_reservas,
            textvariable=self.cliente_reserva_var,
            state="readonly"
        )

        self.combo_clientes.grid(row=1, column=1)

        # Servicio para la reserva
        tk.Label(frame_reservas, text="Servicio:").grid(row=2, column=0)

        self.combo_servicios = ttk.Combobox(
            frame_reservas,
            textvariable=self.servicio_reserva_var,
            state="readonly"
        )

        self.combo_servicios.grid(row=2, column=1)

        # Cantidad para la reserva
        tk.Label(frame_reservas, text="Cantidad (horas/días/sesiones):").grid(row=3, column=0)
        tk.Entry(frame_reservas, textvariable=self.cantidad_reserva_var).grid(row=3, column=1)

        # Botón para crear reserva
        tk.Button(
            frame_reservas,
            text="Crear Reserva",
            command=self.crear_reserva_gui,
            bg="orange"
        ).grid(row=4, column=0, columnspan=2, pady=10)

        # ===========================================
        # ====== TABLA DE RESERVAS ======
        # ===========================================

        self.tabla_reservas = ttk.Treeview(
            tab_reservas,
            columns=("ID", "Cliente", "Servicio", "Cantidad", "Estado"),
            show="headings",
            height=6
        )

        self.tabla_reservas.heading("ID", text="ID de Reserva")
        self.tabla_reservas.heading("Cliente", text="Cliente")
        self.tabla_reservas.heading("Servicio", text="Servicio")
        self.tabla_reservas.heading("Cantidad", text="Cantidad")
        self.tabla_reservas.heading("Estado", text="Estado")

        # Centrar columnas 
        self.tabla_reservas.column("ID", anchor="center", width=100)
        self.tabla_reservas.column("Cliente", anchor="center", width=200)
        self.tabla_reservas.column("Servicio", anchor="center", width=200)
        self.tabla_reservas.column("Cantidad", anchor="center", width=100)
        self.tabla_reservas.column("Estado", anchor="center", width=150)

        self.tabla_reservas.pack(padx=10, pady=10, fill="both")

       # ===========================================
       # ====== BOTONES EXTRA DEL SISTEMA ======
       # ===========================================
        frame_botones = tk.Frame(tab_reservas)
        frame_botones.pack(pady=10)
   
    # Boton para cancelar reserva
        tk.Button(
            frame_botones,
            text="Cancelar Reserva",
            command=self.cancelar_reserva_gui,
            bg="red",
            fg="white"
        ).grid(row=0, column=1, padx=10)

    # ===========================================
    # ====== REGISTRAR CLIENTE ======
    # ===========================================

    def registrar_cliente(self):
        try:
            cliente = Cliente(
                int(self.id_cliente_var.get()),
                self.nombre_cliente_var.get(),
                self.email_cliente_var.get()
            )

            self.sistema.agregar_cliente(cliente)

            # Agregar cliente a la tabla
            self.tabla_clientes.insert(
                "",
                tk.END,
                values=(
                    cliente.id,
                    cliente._nombre,
                    cliente._email
                )
            )

            messagebox.showinfo(
                "Éxito",
                "Cliente registrado correctamente"
            )

            # Limpiar campos
            self.id_cliente_var.set("")
            self.nombre_cliente_var.set("")
            self.email_cliente_var.set("")

        # Actualizar combo de clientes para reservas
            clientes = [c._nombre for c in self.sistema.clientes]
            self.combo_clientes['values'] = clientes

        except Exception as e:
            log_evento(str(e), "ERROR")

            messagebox.showerror(
                "Error",
                f"No se pudo registrar el cliente: {e}"
            )

    # ===========================================
    # ====== REGISTRAR SERVICIO ======
    # ===========================================
    def registrar_servicio(self):
        try:
            nombre = self.nombre_servicio_var.get()
            precio = float(self.precio_servicio_var.get())
            tipo = self.tipo_servicio_var.get()

            # Crear Servicio según el tipo seleccionado
            if tipo == "Reserva de Sala":
                servicio = ReservaSala(nombre, precio)
            elif tipo == "Alquiler de Equipos":
                servicio = AlquilerEquipos(nombre, precio)
            elif tipo == "Asesoría Especializada":
                servicio = AsesoriaEspecializada(nombre, precio)
            else:
                raise SistemaError("Debe seleccionar un tipo de servicio válido")

            # Agregar servicio al sistema
            self.sistema.agregar_servicio(servicio)

            # Agregar servicio a la tabla
            self.tabla_servicios.insert(
                "",
                tk.END,
                values=(
                    servicio.nombre,
                    servicio.precio_base,
                    tipo
                )
            )

            messagebox.showinfo(
                "Éxito",
                "Servicio registrado correctamente"
            )

            # Limpiar campos
            self.nombre_servicio_var.set("")
            self.precio_servicio_var.set("")
            self.tipo_servicio_var.set("")

        # Actualizar lista de servicios para reservas
            servicios = [s.nombre for s in self.sistema.servicios]
            self.combo_servicios['values'] = servicios

        except Exception as e:
            log_evento(str(e), "ERROR")

            messagebox.showerror(
                "Error",
                f"No se pudo registrar el servicio: {e}"
            )
    # ===========================================
    # ====== CREAR RESERVA DESDE GUI ======
    # ===========================================

    def crear_reserva_gui(self):
        try:
            id_reserva = int(self.id_reserva_var.get())
            cantidad = int(self.cantidad_reserva_var.get())

            nombre_cliente = self.cliente_reserva_var.get()
            nombre_servicio = self.servicio_reserva_var.get()

            # Buscar cliente y servicio por nombre
            cliente = None
            for c in self.sistema.clientes:
                if c._nombre == nombre_cliente:
                    cliente = c
                    break

            # Buscar servicio por nombre
            servicio = None
            for s in self.sistema.servicios:
                if s.nombre == nombre_servicio:
                    servicio = s
                    break

            if cliente is None:
                raise ReservaError("Cliente no encontrado")
            if servicio is None:
                raise ReservaError("Servicio no encontrado")

            # Crear reserva y agregar al sistema
            reserva = Reserva(id_reserva, cliente, servicio, cantidad)
            self.sistema.crear_reserva(reserva)

            # Calcular total 

            total = servicio.calcular_costo(cantidad)

            # Agregar reserva a la tabla
            self.tabla_reservas.insert(
                "",
                tk.END,
                values=(
                    reserva.id,
                    cliente._nombre,
                    servicio.nombre,
                    reserva.cantidad,
                    reserva.estado
                )
            )

            messagebox.showinfo(
                "Éxito",
                f"Reserva creada correctamente \n\nTotal a pagar: ${total}"
            )

            # Limpiar campos
            self.id_reserva_var.set("")
            self.cantidad_reserva_var.set("")
            self.cliente_reserva_var.set("")
            self.servicio_reserva_var.set("")

        except Exception as e:
            log_evento(str(e), "ERROR")
            messagebox.showerror(
                "Error",
                f"No se pudo crear la reserva: {e}"
            )
    # ===========================================
    # ====== MOSTRAR ESTADÍSTICAS ======
    # ===========================================  
    
    def mostrar_estadisticas(self):
        total_clientes = len(self.sistema.clientes)
        total_servicios = len(self.sistema.servicios)
        total_reservas = len(self.sistema.reservas)

        confirmadas = 0
        canceladas = 0

        for reserva in self.sistema.reservas:
            if reserva.estado == "Confirmada":
                confirmadas += 1
            elif reserva.estado == "Cancelada":
                canceladas += 1
        
        mensaje = (
            f"Total de Clientes: {total_clientes}\n"
            f"Total de Servicios: {total_servicios}\n"
            f"Total de Reservas: {total_reservas}\n"
            f"Reservas Confirmadas: {confirmadas}\n"
            f"Reservas Canceladas: {canceladas}\n"
        )

        messagebox.showinfo("Estadísticas", mensaje)

        # ===========================================
        # ====== CANCELAR RESERVA DESDE GUI ======
        # ===========================================

    def cancelar_reserva_gui(self):
        try:
            seleccion = self.tabla_reservas.selection()
            if not seleccion:
                raise ReservaError("Debe seleccionar una reserva para cancelar")
            item = self.tabla_reservas.item(seleccion[0])
            datos = item['values']
            id_reserva = datos[0]

            # Cancelar reserva en el sistema
            for reserva in self.sistema.reservas:
                if reserva.id == id_reserva:
                    reserva.cancelar()

                    # Actualizar estado en la tabla
                    self.tabla_reservas.item(
                        seleccion,
                        values=(
                            reserva.id,
                            reserva.cliente._nombre,
                            reserva.servicio.nombre,
                            reserva.cantidad,
                            reserva.estado
                        )
                    )
                    messagebox.showinfo(
                        "Éxito",
                        f"Reserva {id_reserva} cancelada correctamente"
                    )
                    return
        except Exception as e:
            log_evento(str(e), "ERROR")
            messagebox.showerror(
                "Error",
                f"No se pudo cancelar la reserva: {e}"
            )
# ==========================================================
# ====== PUNTO DE ENTRADA DEL PROGRAMA ======
# ==========================================================

if __name__ == "__main__":
    ventana = tk.Tk()
    app = SistemaGUI(ventana)
   
    # ===== PRUEBAS DEL SISTEMA =====

    sistema = app.sistema

    # ===== CLIENTES =====

    cliente1 = Cliente(1, "Laura Jimenez", "LauJz@gmail.com")
    cliente2 = Cliente(2, "Camilo Alvarez", "camiloalvarez@gmail.com")
    cliente3 = Cliente(3, "Sofia Ramirez", "sofiaramirez@gmail.com")

    sistema.agregar_cliente(cliente1)
    sistema.agregar_cliente(cliente2)
    sistema.agregar_cliente(cliente3)
    
    # Cliente Invalido
    try:
        cliente_error = Cliente(3, "", "correo_invalido")
        sistema.agregar_cliente(cliente_error)
    except Exception as e:
        print("Error detectado:", e)

    # ===== SERVICIOS =====

    servicio1 = ReservaSala("Sala VIP", 50)
    servicio2 = AlquilerEquipos("Proyector HD", 30)
    servicio3 = AsesoriaEspecializada("Asesoría Técnica", 80)

    sistema.agregar_servicio(servicio1)
    sistema.agregar_servicio(servicio2)
    sistema.agregar_servicio(servicio3)

    # Actualizar listas desplegables de clientes y servicios en la interfaz
    app.combo_clientes['values'] = [c._nombre for c in sistema.clientes]
    app.combo_servicios['values'] = [s.nombre for s in sistema.servicios]

    # ===== RESERVAS =====

    reserva1 = Reserva(1, cliente1, servicio1, 2)
    sistema.crear_reserva(reserva1)

    reserva2 = Reserva(2, cliente2, servicio2, 6)
    sistema.crear_reserva(reserva2)
    
    reserva3 = Reserva(3, cliente3, servicio3, 4)
    sistema.crear_reserva(reserva3)

    reserva4 = Reserva(4, cliente1, servicio3, 3)
    sistema.crear_reserva(reserva4)

    # Reserva Invalida
    try:
        reserva_error = Reserva(5, cliente1, servicio1, -5)
        sistema.crear_reserva(reserva_error)

    except Exception as e:
        print("El sistema generó un error:", e)

    print("El programa continúa ejecutándose normalmente después del error")

    # Cancelar reserva
    reserva1.cancelar()

    # Cancelar reserva ya cancelada (genera error)
    reserva1.cancelar()

    # Mostrar información
    sistema.mostrar_clientes()
    sistema.mostrar_servicios()
    sistema.mostrar_reservas()

    # Mostrar estadísticas
    sistema.estadisticas()

    # Iniciar la interfaz gráfica
    ventana.mainloop()