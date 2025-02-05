import sqlite3
from tkinter import *
import tkinter as tk
from tkinter import ttk, messagebox

class Clientes(tk.Frame):
    db_name = "database.db"
    
    def __init__(self, padre):
        super().__init__(padre)
        self.widgets()
        self.cargar_registro()
        
    def validar_campos(self):
        if not self.nombre.get() or not self.cedula.get() or not self.celular.get() or not self.direccion.get() or not self.correo.get():
            messagebox.showerror("Error", "Todos los campos son requeridos")
            return False
        
        # Validar que el DNI y el celular sean numéricos
        if not self.cedula.get().isdigit() or not self.celular.get().isdigit():
            messagebox.showerror("Error", "El DNI y el celular deben ser numéricos")
            return False
    
        # Validar que el correo tenga un formato válido
        if "@" not in self.correo.get():
            messagebox.showerror("Error", "El correo debe ser válido")
            return False
        return True
    
    def registrar(self):
        if not self.validar_campos():
            return
        
        nombre = self.nombre.get()
        cedula = self.cedula.get()
        celular = self.celular.get()
        direccion = self.direccion.get()
        correo = self.correo.get()
        
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            cursor.execute("INSERT INTO clientes (Nombre, DNI, celular, Dirección, Correo) VALUES (?,?,?,?,?)",
                        (nombre, cedula, celular, direccion, correo))
            conn.commit()
            conn.close()
            messagebox.showinfo("Exito", "Cliente registrado correctamente")
            self.limpiar_treeview()
            self.cargar_registro()
            self.limpiar_campos()
        except sqlite3.Error as e:
            messagebox.showerror("Error", f"No se pudo registrar el cliente: {e}")
            
    def cargar_registro(self):
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM clientes")
            rows = cursor.fetchall()
            for row in rows:
                self.tre.insert("", "end",  values=row)
            conn.close()
        except sqlite3.Error as e:
            messagebox.showerror("Error", f"No se pudo cargara los registros: {e}")         
    
    def limpiar_treeview(self):
        for item in self.tre.get_children():
            self.tre.delete(item)
            
    def limpiar_campos(self):
        self.nombre.delete(0, END)
        self.cedula.delete(0, END)
        self.celular.delete(0, END)
        self.direccion.delete(0, END)
        self.correo.delete(0, END)
        
    def modificar(self):
        if not self.tre.selection():
            messagebox.showerror("Error", "porfavor seleccione un cliente para modificar")
            return
        
        item = self.tre.selection()[0]
        id_cliente = self.tre.item(item, "values")[0]
        
        nombre_acual     =    self.tre.item(item, "values")[1]
        cedula_acual     =    self.tre.item(item, "values")[2]
        celular_acual    =    self.tre.item(item, "values")[3]
        direccion_acual  =    self.tre.item(item, "values")[4]
        correo_acual     =    self.tre.item(item, "values")[5]
        
        top_modificar = Toplevel(self)
        top_modificar.title("Modificar cliente")
        top_modificar.geometry("400x400+400+50")
        top_modificar.config(bg="#87CEEB")
        top_modificar.resizable(False, False)
        top_modificar.transient(self.master)
        top_modificar.grab_set()
        top_modificar.focus_set()
        top_modificar.lift()
        
        tk.Label(top_modificar, text="Nombre", font="sans 14 bold", bg="#87CEEB").grid(row=0, column=0, padx=10, pady=5)
        nombre_nuevo = tk.Entry(top_modificar, font="sans 14 bold")
        nombre_nuevo.insert(0, nombre_acual)
        nombre_nuevo.grid(row=0, column=1, padx=10, pady=5)
        
        tk.Label(top_modificar, text="Dni", font="sans 14 bold", bg="#87CEEB").grid(row=1, column=0, padx=10, pady=5)
        cedula_nuevo = tk.Entry(top_modificar, font="sans 14 bold")
        cedula_nuevo.insert(0, cedula_acual)
        cedula_nuevo.grid(row=1, column=1, padx=10, pady=5)
        
        tk.Label(top_modificar, text="Celular", font="sans 14 bold", bg="#87CEEB").grid(row=2, column=0, padx=10, pady=5)
        celular_nuevo = tk.Entry(top_modificar, font="sans 14 bold")
        celular_nuevo.insert(0, celular_acual)
        celular_nuevo.grid(row=2, column=1, padx=10, pady=5)
        
        tk.Label(top_modificar, text="Dirección", font="sans 14 bold", bg="#87CEEB").grid(row=3, column=0, padx=10, pady=5)
        direccion_nuevo = tk.Entry(top_modificar, font="sans 14 bold")
        direccion_nuevo.insert(0, direccion_acual)
        direccion_nuevo.grid(row=3, column=1, padx=10, pady=5)
        
        tk.Label(top_modificar, text="Correo", font="sans 14 bold", bg="#87CEEB").grid(row=4, column=0, padx=10, pady=5)
        correo_nuevo = tk.Entry(top_modificar, font="sans 14 bold")
        correo_nuevo.insert(0, correo_acual)
        correo_nuevo.grid(row=4, column=1, padx=10, pady=5)
        
        def guardar_modificaciones():
            nuevo_nombre    =   nombre_nuevo.get()
            nuevo_cedula    =   cedula_nuevo.get()
            nuevo_celular   =   celular_nuevo.get()
            nuevo_direccion =   direccion_nuevo.get()
            nuevo_correo    =   correo_nuevo.get()
            
            try:
                conn = sqlite3.connect(self.db_name)
                cursor = conn.cursor()
                cursor.execute("""UPDATE clientes SET Nombre = ?, DNI = ?, celular = ?, dirección =?, correo = ? WHERE ID = ?""",
                                (nuevo_nombre, nuevo_cedula, nuevo_celular, nuevo_direccion, nuevo_correo, id_cliente))
                conn.commit()
                conn.close()
                messagebox.showinfo("Exito", "Cliente modificado correctamente")
                self.limpiar_treeview()
                self.cargar_registro()
                top_modificar.destroy()
                
            except sqlite3.Error as e:
                messagebox.showerror("Error", f"No se pudo modificara el cliente: {e}")
        btn_guardar = tk.Button(top_modificar, text="guardar cambios", command=guardar_modificaciones, font="sans 14 bold") 
        btn_guardar.grid(row=5, column=0, columnspan=2, pady=20)       
            
        
        
        
        
        
        
        
        
        
        
            
    def widgets(self):
        self.labelframe = tk.LabelFrame(self, text="Clientes", font="sans 20 bold", bg="#87CEEB")
        self.labelframe.place(x=20, y=20, width=250, height=570)
        
        lblnombre = tk.Label(self.labelframe, text= "Nombre: ", font= "sans 14 bold", bg="#87CEEB")
        lblnombre.place(x=10, y=20)
        self.nombre = ttk.Entry(self.labelframe, font="sans 14 bold")
        self.nombre.place(x=10, y=50, width=220, height=40)
        
        lblcedula = tk.Label(self.labelframe, text= "Dni: ", font= "sans 14 bold", bg="#87CEEB")
        lblcedula.place(x=10, y=100)
        self.cedula = ttk.Entry(self.labelframe, font="sans 14 bold")
        self.cedula.place(x=10, y=130, width=220, height=40)
        
        lblcelular = tk.Label(self.labelframe, text= "Celular: ", font= "sans 14 bold", bg="#87CEEB")
        lblcelular.place(x=10, y=180)
        self.celular = ttk.Entry(self.labelframe, font="sans 14 bold")
        self.celular.place(x=10, y=210, width=220, height=40)
        
        lbldireccion = tk.Label(self.labelframe, text= "Dirección: ", font= "sans 14 bold", bg="#87CEEB")
        lbldireccion.place(x=10, y=260)
        self.direccion = ttk.Entry(self.labelframe, font="sans 14 bold")
        self.direccion.place(x=10, y=290, width=220, height=40)
        
        lblcorreo = tk.Label(self.labelframe, text= "Correo: ", font= "sans 14 bold", bg="#87CEEB")
        lblcorreo.place(x=10, y=340)
        self.correo = ttk.Entry(self.labelframe, font="sans 14 bold")
        self.correo.place(x=10, y=370, width=220, height=40)
        
        
        btn1 = Button(self.labelframe, fg="Black", text="Ingresar", font="sans 16 bold", command=self.registrar)
        btn1.place(x=10, y=430, width=220, height=40)
        
        btn2 = Button(self.labelframe, fg="black", text= "Modificar", font="sans 16 bold", command=self.modificar)
        btn2.place(x=10, y=480, width=220, height=40)
        
        treFrame = Frame(self, bg="White")
        treFrame.place(x=280, y=20, width=800, height=570)
        
        #barras  espaciadoras
        scrol_y = ttk.Scrollbar(treFrame)
        scrol_y.pack(side=RIGHT, fill=Y)
        
        scrol_x = ttk.Scrollbar(treFrame, orient=HORIZONTAL)
        scrol_x.pack(side= BOTTOM, fill=X)
        
        self.tre = ttk.Treeview(treFrame, yscrollcommand=scrol_y.set, xscrollcommand=scrol_x.set, height=40,
                                columns=("ID", "Nombre", "Dni", "Celular", "Dirección", "Correo"), show="headings")
        self.tre.pack(expand=True, fill=BOTH)
        
        scrol_y.config(command=self.tre.yview)
        scrol_x.config(command=self.tre.xview)
                                
        self.tre.heading("ID", text="ID")
        self.tre.heading("Nombre", text="Nombre")
        self.tre.heading("Dni", text="Dni")
        self.tre.heading("Celular", text="Celular")
        self.tre.heading("Dirección", text="Dirección")
        self.tre.heading("Correo", text="Correo")
        
        self.tre.column("ID",        width=50,   anchor="center")
        self.tre.column("Nombre",    width=150,  anchor="center")
        self.tre.column("Dni",       width=120,  anchor="center")
        self.tre.column("Celular",   width=120,  anchor="center")
        self.tre.column("Dirección", width=200,  anchor="center")
        self.tre.column("Correo",    width=200,  anchor="center")
        
        
        
        
        