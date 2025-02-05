import sqlite3 
from tkinter import *
import tkinter as tk
from tkinter import ttk, messagebox
from container import Container
from PIL import Image, ImageTk


class Login(tk.Frame):
    db_name = "database.db"   # Nombre de la base de datos
    
    
    def __init__(self, padre, controlador):
        super().__init__(padre)
        self.pack()
        self.place(x=0, y=0, width=1100, height=650)
        self.controlador = controlador
        self.widgets()
        
    def validacion(self, user, pas):
        return len(user) > 0 and len(pas) > 0
        
    def login(self):              #desde aca el login comienza las validaciones
        user = self.username.get()
        pas = self.password.get()
        
        if self.validacion(user, pas):
            consulta ="Select * FROM usuarios WHERE username = ? AND password = ?"
            parametros = (user, pas)
            
            try:
                with sqlite3.connect(self.db_name) as conn:   #Nos conectamos a la base de datos para validar datos del login
                    cursor = conn.cursor()
                    cursor.execute(consulta, parametros)
                    result = cursor.fetchall()
                    
                    if result:
                        self.control1()
                    else:
                        self.username.delete(0, "end")   #Para limpiar campo del nombre de usuario y password despues de cambiar de pantalla
                        self.password.delete(0, "end")
                        messagebox.showerror(title= "Error", message= "Usuario y/o contraseña Incorrecta")  #MENSAJE DE ERROR SI TE EQUIVOCAS DE USUARIO O CONTRASEÑA
            except sqlite3.Error as e:
                messagebox.showerror(title="Error", message=f"No se pudo registrar el usuario: {e}")   # MENSAJE DE ERROR
        else:
            messagebox.showerror(title="Error", message="Llene todas las casillas")   #MENSAJE DE ERROR SI NO COMPLETA LOS DATOS
            
    def control1(self):
        self.controlador.show_frame(Container)
        
    def control2(self):
        self.controlador.show_frame(Registro)
        
        
        
        
        
    def widgets(self):
        fondo = tk.Frame(self, bg="#D3D3D3")
        fondo.pack()
        fondo.place(x=0, y=0, width=1100, height=650)
        
        self.bg_image = Image.open("imagenes/fondo.png.jpg")  #PARA COLOCAR LA FOTO DE FONDO EN NUESTRA GALERIA 
        self.bg_image = self.bg_image.resize((1100,650))      # REDIMENSIONAR LA IMAGEN
        self.bg_image = ImageTk.PhotoImage(self.bg_image)
        self.bg_label = ttk.Label(fondo, image = self.bg_image)
        self.bg_label.place(x=0, y=0, width=1100, height=650) # PARA LA UBICACION DE LA IMAGEN DE FONDO
        
        frame1 = tk.Frame(self, bg="#FFFFFF", highlightbackground="black", highlightthickness=1)
        frame1.place(x=350, y=70, width=400, height=560)
        
        self.logo_image = Image.open("imagenes/logo1.jpg")      # LOGO Y SUS CONFIGURACIONES
        self.logo_image = self.logo_image.resize((200, 200))
        self.logo_image = ImageTk.PhotoImage(self.logo_image)
        self.logo_label = ttk.Label(frame1, image = self.logo_image, background="#ffffff")
        self.logo_label.place(x=100, y=20)
        
        user = tk.Label(frame1, text="Nombre de Usuario", font="roboto 16 bold", background="#FFFFFF")
        user.place(x=100, y=250)
        self.username = ttk.Entry(frame1, font="arial 16 bold" )
        self.username.place(x=80, y=290, width=240, height=40)
        
        pas = tk.Label(frame1, text="Contraseña", font="roboto 16 bold", background="#FFFFFF")
        pas.place(x=100, y=340)
        self.password = ttk.Entry (frame1, show="*", font="arial 16 bold")
        self.password.place(x=80, y=380, width=240, height=40)
        
        btn1 = tk.Button(frame1, text="Iniciar", font="arial 16 bold", command=self.login)   #BOTON DE INICIO QUE LLAMA AL COMANDO LOGIN PARA INICIAR LAS VALIDACIONES DEL LOGIN
        btn1.place(x=80, y=440, width=240, height=40)
        
        btn2 = tk.Button(frame1, text="Registrar", font="arial 16 bold", command=self.control2)
        btn2.place(x=80, y=500, width=240, height=40)
        
        
        
        
        
        
        
    
class Registro(tk.Frame):
    db_name = "database.db" 
    
    def __init__(self, padre, controlador):
        super().__init__(padre)
        self.pack()
        self.place(x=0, y=0, width=1100, height=650)
        self.controlador = controlador
        self.widgets()
        
    def validacion(self, user, pas):
        return len(user) > 0 and len(pas) > 0   #NOS AYUDA A VALIDAR QUE EL USURARIO O PASSWORD NO ESTEN VACIOS
    
    def eje_consulta(self, consulta, parametros=()):
        try:
            with sqlite3.connect(self.db_name) as conn:
                cursor =conn.cursor()
                cursor.execute(consulta, parametros)
                conn.commit
        except sqlite3.Error as e:
            messagebox.showerror(title="Error", message=f"Error al ejecutar la consulta: {e}")
    
    def registro(self):
        user = self.username.get()
        pas = self.password.get()
        key = self.key.get()
        if self.validacion(user, pas):
            if len(pas) < 6:
                messagebox.showinfo(title="Error", message="Contraseña demasiado corta")
                self.username.delete(0, "end")
                self.password.delete(0, "end")
            else:
                if key =="1234":
                    consulta = "INSERT INTO usuarios VALUES (?,?,?)"
                    parametros = (None, user, pas )
                    self.eje_consulta(consulta, parametros)
                    self.control1()
                else:
                    messagebox.showerror( title= "Registro", message="Error al ingresar el codigo de registro")
        else:
            messagebox.showerror(title="Error", message="Llena tus datos")
            
    def control1(self):
        self.controlador.show_frame(Container)
        
    def control2(self):
        self.controlador.show_frame(Login)
        
        
    def widgets(self):
        fondo = tk.Frame(self, bg="#D3D3D3")
        fondo.pack()
        fondo.place(x=0, y=0, width=1100, height=650)
        
        self.bg_image = Image.open("imagenes/fondo.png.jpg")
        self.bg_image = self.bg_image.resize((1100,650))
        self.bg_image = ImageTk.PhotoImage(self.bg_image)
        self.bg_label = ttk.Label(fondo, image = self.bg_image)
        self.bg_label.place(x=0, y=0, width=1100, height=650)
        
        frame1 = tk.Frame(self, bg="#FFFFFF", highlightbackground="black", highlightthickness=1)
        frame1.place(x=350, y=10, width=400, height=630)
        
        self.logo_image = Image.open("imagenes/logo1.jpg")    # LOGO Y SUS CONFIGURACIONES
        self.logo_image = self.logo_image.resize((200, 200))
        self.logo_image = ImageTk.PhotoImage(self.logo_image)
        self.logo_label = ttk.Label(frame1, image = self.logo_image, background="#ffffff")
        self.logo_label.place(x=150, y=20)
        
        user = tk.Label(frame1, text="Nombre de Usuario", font="roboto 16 bold", background="#FFFFFF")
        user.place(x=100, y=250)
        self.username = ttk.Entry(frame1, font="arial 16 bold" )
        self.username.place(x=80, y=290, width=240, height=40)
        
        pas = tk.Label(frame1, text="Contraseña", font="roboto 16 bold", background="#FFFFFF")
        pas.place(x=100, y=340)
        self.password = ttk.Entry (frame1, show="*", font="arial 16 bold")
        self.password.place(x=80, y=380, width=240, height=40)
        
        key = ttk.Label(frame1, text="Codigo de registro", font="arial 16 bold", background="#FFFFFF")
        key.place(x=100, y=430)
        self.key = ttk.Entry(frame1, show="*", font="arial 16 bold" )
        self.key.place(x=80, y=470, width=240, height=40)
        
        
        
        
        
        btn3 = tk.Button(frame1, text="Registrarse", font="arial 16 bold", command=self.registro)
        btn3.place(x=80, y=520, width=240, height=40)
        
        btn4 = tk.Button(frame1, text="Regresar", font="arial 16 bold", command=self.control2)
        btn4.place(x=80, y=570, width=240, height=40)