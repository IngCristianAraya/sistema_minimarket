import sqlite3 
from tkinter import *
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from datetime import datetime
import datetime
import threading
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from PIL import Image, ImageTk
import sys
import os


class Ventas(Frame):
    db_name = "database.db"
    
    def __init__(self, padre):
        super().__init__(padre)
        self.tree = None
        
        self.numero_factura = self.obtener_numero_factura_actual()
        self.productos_seleccionados = []
        self.widgets()
        self.cargar_productos()
        self.cargar_clientes()
        self.timer_prodcuto = None
        self.timer_clientes = None

        
    # funcion para obtener numero de factura actual    
    def obtener_numero_factura_actual(self):
        try:
            conn = sqlite3.connect(self.db_name)                                            #accede a la bd
            c = conn.cursor()                                                               #permite realizar las consultas con execute
            c.execute("SELECT MAX(factura) FROM ventas")                                    #selecciona el numero maximo de las facturas de venta
            last_invoice_number = c.fetchone()[0]                                           #Ejecuta una consulta SQL y obtiene una única fila del resultado. La consulta debe haber sido previamente ejecutada en el cursor c, Después de obtener la fila, fetchone() devuelve una tupla. Al hacer fetchone()[0], se está accediendo al primer (y probablemente único) valor de esa tupla, que en este caso se supone que es el número de la última factura.
            conn.close()                                                                    #Cierra la conexión a la base de datos SQLite. Es una buena práctica cerrar la conexión cuando ya no se necesita.
            return last_invoice_number + 1 if last_invoice_number is not None else 1
        except sqlite3.Error as e:                                                          #Si ocurre un error durante la ejecución de la consulta o cualquier otro problema con la base de datos, se captura el error y se imprime el mensaje de error.
            print("Error obteniendo el numero de factura actual:", e)
            return 1                                                                        #Si ocurre un error, la función devuelve 1 como el número de factura por defecto. Esto evita que la función falle si hay problemas con la base de datos.
    
    def cargar_clientes(self):
        try:
            conn = sqlite3.connect(self.db_name)
            c = conn.cursor()
            c.execute("SELECT nombre FROM clientes")
            clientes = c.fetchall()
            self.clientes = [cliente[0] for cliente in clientes]
            self.entry_cliente["values"] = self.clientes  # Asignamos valores al combobox
            conn.close()
        except sqlite3.Error as e:
            print("Error al cargar clientes:", e)
            
    def filtrar_clientes(self, event):
        if self.timer_clientes:
            self.timer_clientes.cancel()
        self.timer_clientes = threading.Timer(0.5, self.filter_clientes)
        self.timer_clientes.start()
        
    def filter_clientes(self):
        typed = self.entry_cliente.get()
        
        if typed ==  "":
            data = self.clientes
        else:
            data = [item for item in self.clientes if typed.lower() in item.lower()]
            
        if data:
            self.entry_cliente["values"] = data
            self.entry_cliente.event_generate("<Down>")
            
        else:
            self.entry_cliente ["values"] = ["no se encontraron resultados"]
            self.entry_cliente.event_generate("<Down>")
            self.entry_cliente.delete(0, "end")
        
        
    def cargar_productos(self):
        try:
            conn = sqlite3.connect(self.db_name)
            c = conn.cursor()
            c.execute("SELECT articulo FROM articulos")
            self.products = [product[0] for product in c.fetchall()]
            self.entry_producto["values"] = self.products  # Asignamos valores al combobox
            conn.close()
        except sqlite3.Error as e:
            print("Error cargando productos:", e)
            
    def filtrar_productos(self, event):
        if self.timer_prodcuto:
            self.timer_prodcuto.cancel()
        self.timer_prodcuto = threading.Timer(0.5, self.filter_products)
        self.timer_prodcuto.start()
        
    def filter_products(self):
        typed = self.entry_producto.get()
        
        if typed ==  "":
            data = self.products
        else:
            data = [item for item in self.products if typed.lower() in item.lower()]
            
        if data:
            self.entry_producto["values"] = data
            self.entry_producto.event_generate("<Down>")
            
        else:
            self.entry_producto ["values"] = ["no se encontraron resultados"]
            self.entry_producto.event_generate("<Down>")
            self.entry_producto.delete(0, "end")
        
            
            
    def agregar_articulos(self):
        cliente  = self.entry_cliente.get()
        producto = self.entry_producto.get()
        cantidad = self.entry_cantidad.get()   
        
        if not cliente:
            messagebox.showerror("Error", " Por favor seleccione cliente")  
        
        if not producto:
            messagebox.showerror("Error", " Por favor seleccione Producto") 
            
        if not cantidad.isdigit() or int(cantidad) <= 0:
            messagebox.showerror("Error", " Por favor ingrese una cantidad valida")
            return
        
        cantidad = int(cantidad)   
        cliente = self.entry_cliente.get()
        
        try:
            conn = sqlite3.connect(self.db_name)
            c = conn.cursor()
            c.execute("SELECT precio, costo, stock FROM articulos WHERE articulo=?",(producto,))
            resultado = c.fetchone()
            
            if resultado is None:
                messagebox.showerror("Error", "Producto no encontrado.")
                
            precio, costo, stock = resultado
            
            if cantidad > stock:
                messagebox.showerror("Error", f"Stock insuficiente. Solo hay {stock} unidades disponibles.")

            total = precio * cantidad
            total_cop = "{:,.2f}".format(total)

            self.tre.insert("", "end", values=(self.numero_factura, cliente, producto, "{:,.2f}".format(precio), cantidad, total_cop))
            self.productos_seleccionados.append((self.numero_factura, cliente, producto, precio, cantidad, total_cop, costo))          
            
            conn.close()
            
            self.entry_producto.set("")
            self.entry_cantidad.delete(0, "end")
            
        except sqlite3.Error as e:
            print("Error al agregar el articulo") 
            
        self.calcular_precio_total()
        
    def calcular_precio_total(self):
        total_pagar = sum(float(self.tre.item(item)["values"][-1].replace(" ", "").replace(",", "")) for item in self.tre.get_children())   
        total_pagar_cop = "{:,.2f}".format(total_pagar)
        self.label_precio_total.config(text=f"Precio a pagar: S/ {total_pagar_cop}")
        
    def actualizar_stock(self, event=None):
        producto_seleccionado = self.entry_producto.get()
        
        try:
            conn = sqlite3.connect(self.db_name)
            c  = conn.cursor()
            c.execute("SELECT stock FROM articulos WHERE articulo=?", (producto_seleccionado,))
            stock = c.fetchone()[0]
            conn.close()
            
            self.label_stock.config(text=f"Stock: {stock}")
        except sqlite3.Error as e:
            print("Error al obtener el stock del producto: ", e)
            
    def Realizar_pago(self):
        if not self.tre.get_children():
            messagebox.showerror("Error", "No hay productos seleccionados para realizara pago.")
            
        total_venta = sum(float(item[5].replace(" ","").replace(",","")) for item in self.productos_seleccionados)
        
        total_formateado = "{:,.2f}".format(total_venta)
        
        #Ventana de pago
        ventana_pago = tk.Toplevel(self)
        ventana_pago.title("Realizar pago")
        ventana_pago.geometry("400x400+450+80")
        ventana_pago.config(bg="#A0DFF5")
        ventana_pago.resizable(False, False)
        ventana_pago.transient(self.master)
        ventana_pago.grab_set()
        ventana_pago.focus_set()
        ventana_pago.lift()
        
        label_titulo = tk.Label(ventana_pago, text="Realizar Pago", font="sans 30 bold", bg="#A0DFF5") 
        label_titulo.place(x=70, y=10)  
        
        label_total = tk.Label(ventana_pago, text=f"Total a pagar: {total_formateado}", font="sans 14 bold", bg="#A0DFF5", justify="center") 
        label_total.place(x=80, y=100)
        
        label_monto = tk.Label(ventana_pago, text="Ingrese el monto pagado: ", font="sans 14 bold", bg="#A0DFF5") 
        label_monto.place(x=80, y=160) 
        
        entry_monto = ttk.Entry(ventana_pago, font="sans 14 bold")
        entry_monto.place(x=80, y=210, width=240, height=40)
        
        button_confimar_pago = tk.Button(ventana_pago,  text="Confirmar pago", font="sans 14 bold", command=lambda: self.procesar_pago(entry_monto.get(), ventana_pago, total_venta))
        button_confimar_pago.place(x=80, y=260, width=240, height=40)
        
    def procesar_pago(self, cantidad_pagada, ventana_pago, total_venta):
        cantidad_pagada = float(cantidad_pagada)
        cliente = self.entry_cliente.get()
        
        if cantidad_pagada < total_venta:
            messagebox.showerror("Error", "La cantidad pagada es insuficiente.")
            return
        
        cambio = cantidad_pagada - total_venta
        
        total_formateado = "{:,.2f}".format(total_venta)
        
        mensaje = f" Total {total_formateado} \nCantidad pagada: {cantidad_pagada:,.2f} \nCambio {cambio:,.2f}"        
        messagebox.showinfo("Pago realizado", mensaje)
        
        try:
            conn = sqlite3.connect(self.db_name)
            c = conn.cursor()
            
            fecha_actual = datetime.datetime.now().strftime("%Y-%m-%d")
            hora_actual = datetime.datetime.now().strftime("%H-%M-%S")
            
            for item in self.productos_seleccionados:
                factura, cliente, producto, precio, cantidad, total, costo = item
                c.execute("INSERT INTO ventas (factura, cliente, articulo, precio, cantidad, total, costo, fecha, hora) VALUES (?,?,?,?,?,?,?,?,?)",
                          (factura,cliente,producto,precio,cantidad, total.replace(" ", "").replace(",",""), costo * cantidad,fecha_actual, hora_actual))
                c.execute("UPDATE articulos SET stock = stock - ? WHERE articulo = ?",(cantidad, producto))  
                
            conn.commit()
            
            self.generar_factura_pdf(total_venta, cliente)
            
        except sqlite3.Error as e:
            messagebox.showerror("Error", f"Error al registrar la venta {e}")    
                
        self.numero_factura  += 1
        self.label_numero_factura.config(text=str(self.numero_factura))
        
        self.productos_seleccionados = []
        self.limpiar_campos()
        
        ventana_pago.destroy()
        
    def limpiar_campos(self):
        for item in self.tre.get_children():
            self.tre.delete(item)
        self.label_precio_total.config(text="Precio a pagar: S/ 0") 
        
        self.entry_producto.set("")
        self.entry_cantidad.delete(0, "end")  
        
    def limpiar_lista(self):
        self.tre.delete(*self.tre.get_children())
        self.productos_seleccionados.clear()
        self.calcular_precio_total()
        
    def eliminar_articulo(self):
        item_seleccionado = self.tre.selection()  
        if not item_seleccionado:
            messagebox.showerror("Error", "No hay ningun articulo seleccionado")
            return
        
        item_id = item_seleccionado[0]
        valores_item = self.tre.item(item_id)["values"]
        factura, cliente, articulo, precio, cantidad, total = valores_item
        
        self.tre.delete(item_id)
        
        self.productos_seleccionados = [producto for producto in self.productos_seleccionados if producto[2] !=articulo]
        
        self.calcular_precio_total()
        
    def editar_articulo(self):
        selected_item = self.tre.selection()
        if not selected_item:
            messagebox.showerror("Error", "Por favor seleccione un articulo para editar")
            return
        
        item_value = self.tre.item(selected_item[0], "values")
        if not item_value:
            return
        
        current_producto = item_value[2]
        current_cantidad = int(item_value[4])
        
        new_cantidad = simpledialog.askinteger("Editar articulo", "Ingrese la nueva cantidad: ", initialvalue=current_cantidad)
        
        if new_cantidad is not None:
            try:
                conn = sqlite3.connect(self.db_name)
                c = conn.cursor()
                c.execute("SELECT precio, costo, stock FROM articulos WHERE articulo=?", (current_producto,))
                resultado = c.fetchone()
                
                if resultado is None:
                    messagebox.showerror("Error", "Producto no encontrado")
                    
                precio, costo, stock = resultado
                
                if new_cantidad > stock:
                    messagebox.showerror("Error", f"Stock insuficiente. Solo hay {stock} unidades disponibles")
                    
                total     = precio * new_cantidad 
                total_cop = "{:,.2f}".format(total)
                
                self.tre.item(selected_item[0], values=(self.numero_factura, self.entry_cliente.get(), current_producto, "{:,.2f}".format(precio), new_cantidad, total_cop))
                
                for idx, producto in enumerate(self.productos_seleccionados):
                    if producto[2] == current_producto:
                        self.productos_seleccionados[idx] = (
                            self.numero_factura,
                            self.entry_cliente.get(),
                            current_producto,
                            precio, 
                            new_cantidad, 
                            total_cop, 
                            costo
                        )
                        break
                        
                conn.close()
                
                self.calcular_precio_total()
            except sqlite3.Error as e:
                print("Error",f"Error al editar el articulo:  {e}")
                
    def ver_ventas_realizadas(self):
        try:
            conn = sqlite3.connect(self.db_name)
            c = conn.cursor()
            c.execute("SELECT * FROM ventas")
            ventas = c.fetchall()
            conn.close()
            
            # Crear una nueva ventana
            ventana_ventas = tk.Toplevel(self)
            ventana_ventas.title("Ventas Realizadas")
            ventana_ventas.geometry("1100x650+120+20")
            ventana_ventas.configure(bg="#A0DFF5")
            ventana_ventas.resizable(False, False)
            ventana_ventas.transient(self.master)
            ventana_ventas.grab_set()
            ventana_ventas.focus_set()
            ventana_ventas.lift()
            
            
            
            def filtrar_ventas():

                    factura_a_buscar = entry_factura.get()
                    cliente_a_buscar = entry_cliente.get()
                    for item in tree.get_children():
                        tree.delete(item)
                    
                    ventas_filtradas = [
                        venta for venta in ventas
                        if (str(venta[0])== factura_a_buscar or not factura_a_buscar) and
                        (venta[1].lower() == cliente_a_buscar.lower() or not cliente_a_buscar)
                    ]
                    for venta in ventas_filtradas:
                        venta_formateada = formatear_venta(venta)
                        tree.insert("", "end", values=venta_formateada)
                
                    
            def formatear_venta(venta):
                    venta = list(venta)
                    venta[3] = "{:,.2f}".format(venta[3])
                    venta[5] = "{:,.2f}".format(venta[5])
                    try:
                        venta[6] = datetime.datetime.strptime(venta[6],"%Y-%m-%d").strftime("%d-%m-%Y")
                        
                    except ValueError:
                            print("Error al formatear fecha")
                    return venta    
                
                
                        
            # Etiqueta de título
            Label_ventas_realizadas = tk.Label(ventana_ventas, text="Ventas Realizadas", font="sans 26 bold", bg="#A0DFF5", anchor="center")
            Label_ventas_realizadas.place(x=420, y=10)
            
            #filtro frame
            filtro_frame = tk.Frame(ventana_ventas, bg="#A0DFF5")
            filtro_frame.place(x=20, y=60, width=1060, height=60)
            
            #etiqueta label Nº Factura
            label_factura = tk.Label(filtro_frame, text="Nº de Factura: ",bg="#A0DFF5", font="sans 16 bold")
            label_factura.place(x=10, y=15)
            
            #caja de entry factura
            entry_factura = ttk.Entry(filtro_frame, font="sans 14 bold")
            entry_factura.place(x=200, y=10, width=200, height=40)
            
            #etiqueta label Cliente
            label_cliente = tk.Label(filtro_frame, text="Cliente: ",bg="#A0DFF5", font="sans 16 bold")
            label_cliente.place(x=480, y=15)
            
            #caja de entry cliente
            entry_cliente = ttk.Entry(filtro_frame, font="sans 14 bold")
            entry_cliente.place(x=620, y=10, width=200, height=40)
            
            btn_filtrar = tk.Button(filtro_frame, text="Filtrar", font="sans 14 bold", command=filtrar_ventas)
            btn_filtrar.place(x=840, y=10)
            
            tree_frame = tk.Frame(ventana_ventas, bg="white")  
            tree_frame.place(x=20,y=130,width=1060,height=500)  
            
          
            
            # Scrollbars
            scroll_y = ttk.Scrollbar(tree_frame, orient=VERTICAL)
            scroll_y.pack(side=RIGHT, fill=Y)
    
            scroll_x = ttk.Scrollbar(tree_frame, orient=HORIZONTAL)
            scroll_x.pack(side=BOTTOM, fill=X)
            
            # Treeview para mostrar las ventas
            tree = ttk.Treeview(tree_frame, columns=("Factura", "Cliente", "Producto", "Precio", "Cantidad", "Total","Fecha","Hora"), show="headings", yscrollcommand=scroll_y.set, xscrollcommand=scroll_x.set)
            tree.pack(expand=True, fill=BOTH)
            
            scroll_y.config(command=tree.yview)
            scroll_x.config(command=tree.xview)
            
            tree.heading("Factura", text= "factura")
            tree.heading("Cliente", text="Cliente")
            tree.heading("Producto", text="Producto")
            tree.heading("Precio", text="Precio")
            tree.heading("Cantidad", text="Cantidad")
            tree.heading("Total", text="Total")
            tree.heading("Fecha", text="Fecha")
            tree.heading("Hora", text="Hora")
            
            tree.column("Factura", width=60, anchor="center")
            tree.column("Cliente", width=120, anchor="center")
            tree.column("Producto", width=60, anchor="center")
            tree.column("Precio", width=80, anchor="center")
            tree.column("Cantidad", width=120, anchor="center")
            tree.column("Total", width=80, anchor="center")
            tree.column("Fecha", width=80, anchor="center")
            tree.column("Hora", width=80, anchor="center")
            
        except sqlite3.Error as e:
            print(f"Error al conectar con la base de datos: {e}")
            
            
            def formatear_venta(venta):
                for venta in ventas:
                    venta = list(venta)
                    venta[3] = "{:,.2f}".format(venta[3])
                    venta[5] = "{:,.2f}".format(venta[5])
                try:
                    venta[6] = datetime.datetime.strptime(venta[6],"%Y-%m-%d").strftime("%d-%m-%Y")
                
                except ValueError:
                        print("Error al formatear fecha")
                return venta  
            
            
            def filtrar_ventas():
                factura_a_buscar = entry_factura.get()
                cliente_a_buscar = entry_cliente.get()
                for item in tree.get_children():
                    tree.delete(item)
            
                ventas_filtradas = [
                        venta for venta in ventas
                        if (str(venta[0])== factura_a_buscar or not factura_a_buscar) and
                        (venta[1].lower() == cliente_a_buscar.lower() or not cliente_a_buscar)
                    ]
                for venta in ventas_filtradas:
                    venta_formateada = formatear_venta(venta)
                    tree.insert("", "end", values=venta_formateada)
                
                
                
        except sqlite3.Error as e:
            messagebox.showerror("Error", f"Error al obtener las ventas", {e})
            
    def generar_factura_pdf(self, total_venta, cliente):
        try:
            if not os.path.exists('facturas'):
                os.makedirs('facturas')
            
            factura_path = f"facturas/factura_{self.numero_factura}.pdf"
            c = canvas.Canvas(factura_path, pagesize=letter)
            
            logo_path = "logo/logo CD.png"  # Cambia esto por la ruta de tu logo
            try:
            # Ajusta las coordenadas (x,y) y el tamaño (width, height) según necesites
                c.drawImage(logo_path, 250, 50, width=100, height=100, preserveAspectRatio=True)
            except:
                print("No se pudo cargar el logo")
            
            empresa_nombre    = "mini Market Version 1.0"
            empresa_direccion = "Santa Paul 470"
            empresa_telefono  = "+51 901 426 737"
            empresa_email     = "info@creciendodigital.com"
            empresa_website   =  "Creciendodigital.tv"
            
            
            
            c.setFont("Helvetica-Bold", 18)
            c.setFillColor(colors.darkblue)
            c.drawCentredString(300 , 750, "FACTURA DE SERVICIOS")
            
            c.setFillColor(colors.black)
            c.setFont("Helvetica-Bold", 12)
            c.drawString(50, 700, f"{empresa_nombre}")
            c.setFont("Helvetica", 12)
            c.drawString(50, 680, f"Dirección: {empresa_direccion}")
            c.drawString(50, 650, f"Telefono: {empresa_telefono}")
            c.drawString(50, 630, f"Email: {empresa_email}")
            c.drawString(50, 610, f"Website: {empresa_website}")
            
            c.setLineWidth(0.5)
            c.setStrokeColor(colors.gray)
            c.line(50, 600, 550, 600)
            
            c.setFont("Helvetica", 12)
            c.drawString(50, 580, f"Numero de factura: {self.numero_factura}")
            c.drawString(50, 560, f"Fecha: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            
            c.line(50, 550, 550, 550)
            
            c.drawString(50, 530, f"Cliente: {cliente}")
            c.drawString(50, 510, "Descripción de productos: ")
            
            y_offset = 500
            c.setFont("Helvetica-Bold",12)
            c.drawString(70, y_offset, "Producto")
            c.drawString(270, y_offset, "Cantidad")
            c.drawString(370, y_offset, "Precio")
            c.drawString(470, y_offset, "Total")
            
            c.line(50, y_offset - 10, 550, y_offset -10 )
            y_offset -= 30
            c.setFont("Helvetica", 12)
            for item in self.productos_seleccionados:
                factura, cliente, producto, precio, cantidad, total, costo = item
                c.drawString(70, y_offset, producto)
                c.drawString(270, y_offset, str(cantidad))
                c.drawString(370, y_offset, "S/{:,.2f}".format(precio))
                c.drawString(470, y_offset, total)
                y_offset -= 20
                
            c.line(50, y_offset, 550, y_offset)
            y_offset-= 20
            
            c.setFont("Helvetica-Bold", 14)
            c.setFillColor(colors.darkblue)
            c.drawString(50 , y_offset, f"Total a pagar: S/ {total_venta:,.2f}")
            c.setFillColor(colors.black)
            c.setFont("Helvetica", 12)
            
            y_offset -= 20
            c.line(50, y_offset, 550, y_offset)
            
            c.setFont("Helvetica-Bold", 16)
            c.drawString(150, y_offset - 60, " ¡Gracias por tu compra, vuelve pronto!")
            
            y_offset -= 100
            c.setFont("Helvetica", 10)
            c.drawString(50, y_offset,  " Terminos y condiciones: ")
            c.drawString(50, y_offset - 20, " 1. Los productos comprados no tienen devolución.")
            c.drawString(50, y_offset - 40, " 2. Conserve esta factura como comprobante de su compra. ")
            c.drawString(50, y_offset - 60, " 3. Para mas información, visite nuestro sitio web o contacte a servicio al cliente")
            
            c.save()
            
            messagebox.showinfo("Factura generada", f"Se ha generado la factura en: {factura_path}")
            os.startfile(os.path.abspath(factura_path))
            
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo generar la factura: {e}")
    
    
    
    
    
    
    #Interfaz grafica de Ventas        
    def widgets(self):
        #caja de ventas font y fondo label 1
        labelframe = tk.LabelFrame(self, font="sans 12 bold", bg="#A0DFF5") 
        #dimensiones de caja de venta
        labelframe.place(x=25, y=25, width=1045, height=180)   
        
        #etiqueta de cliente:
        label_cliente = tk.Label(labelframe, text="Cliente: ", font="sans 14 bold", bg="#A0DFF5") 
        label_cliente.place(x=10, y=11)
        #entry o caja de busqueda
        self.entry_cliente = ttk.Combobox(labelframe, font="sans 14 bold")
        self.entry_cliente.place(x=120, y=8, width=260, height=40)
        self.entry_cliente.bind("<KeyRelease>", self.filtrar_clientes) 
        
        #etiqueta de producto:
        label_producto = tk.Label(labelframe, text="Producto: ", font="sans 14 bold", bg="#A0DFF5") 
        label_producto.place(x=10, y=70)
        #entry o caja de producto
        self.entry_producto = ttk.Combobox(labelframe, font="sans 14 bold")
        self.entry_producto.place(x=120, y=66, width=260, height=40)
        self.entry_producto.bind("<KeyRelease>", self.filtrar_productos) 
    
        
        #etiqueta de Cantidad
        label_cantidad =tk.Label(labelframe, text="Cantidad: ", font="sans 14 bold", bg="#A0DFF5") 
        label_cantidad.place(x=400, y=11)
        #entry o caja de busqueda de cantidad
        self.entry_cantidad = ttk.Entry(labelframe, font="sans 14 bold")
        self.entry_cantidad.place(x=510, y=8, width=100, height=40)
        
        #etiqueta de stock
        self.label_stock = tk.Label(labelframe, text="Stock: ", font="sans 14 bold", bg= "#A0DFF5")
        self.label_stock.place(x=400, y=70)
        self.entry_producto.bind("<<ComboboxSelected>>", self.actualizar_stock)
        
        
        #etiqueta de Nº de factura
        label_factura = tk.Label(labelframe, text="Nº de Factura: ", font="sans 14 bold", bg= "#A0DFF5")
        label_factura.place(x=630, y=11) 
        
        self.label_numero_factura = tk.Label(labelframe, text=f"{self.numero_factura}", font="sans 14 bold", bg= "#A0DFF5")
        self.label_numero_factura.place(x=950, y=11)
        
        #boton de agregar articulo
        boton_agregar = tk.Button(labelframe, text="Agregar articulo", font="sans 14 bold", command=self.agregar_articulos)
        boton_agregar.place(x=90, y=120, width=200, height=40)
        #boton de eliminar articulo
        boton_eliminar = tk.Button(labelframe, text=" Eliminar articulo", font="sans 14 bold", command=self.eliminar_articulo)
        boton_eliminar.place(x=310, y=120, width=200, height=40)
        #boton de editar articulo
        boton_editar = tk.Button(labelframe, text="Editar articulo", font="sans 14 bold", command=self.editar_articulo)
        boton_editar.place(x=530, y=120, width=200, height=40)
        #boton de limpiar lista
        boton_limpiar = tk.Button(labelframe, text="Limpiar lista", font="sans 14 bold", command=self.limpiar_lista)
        boton_limpiar.place(x=750, y=120, width=200, height=40)
        
        #========================================================================================================
        
        #caja Nº 2
        trefame = tk.Frame(self, bg="white")
        trefame.place(x=60,y=220, width=980, height=320)
        
        #Scroll bar Y
        scrol_y = ttk.Scrollbar(trefame, orient=VERTICAL)
        scrol_y.pack(side=RIGHT, fill=Y)
        #Scroll bar X
        scrol_x = ttk.Scrollbar(trefame, orient=HORIZONTAL)
        scrol_x.pack(side=BOTTOM, fill=X)
        
        #para que pueda funcionar la barra de desplazamiento horizontal y vertical, columns= encabezados de las columnas
        self.tre = ttk.Treeview(trefame, yscrollcommand=scrol_y.set, xscrollcommand=scrol_x.set, height=40, columns=("Factura", "Cliente", "Producto", "Precio", "Cantidad", "Total"), show="headings")
        self.tre.pack(expand=TRUE, fill=BOTH) #posicionar 
        
        #Configurar Scroll bar (y,x)
        scrol_y.config(command=self.tre.yview)
        scrol_x.config(command=self.tre.xview)
        
        #Nombre de encabezados
        self.tre.heading("Factura",   text="Factura")
        self.tre.heading("Cliente",   text="Cliente")
        self.tre.heading("Producto",  text="Producto")
        self.tre.heading("Precio",    text="Precio")
        self.tre.heading("Cantidad",  text="Cantidad")
        self.tre.heading("Total",     text="Total")
        
        #Nombre de las columnas
        self.tre.column("Factura",  width=70,   anchor="center")
        self.tre.column("Cliente",  width=250,   anchor="center")
        self.tre.column("Producto", width=250,   anchor="center")
        self.tre.column("Precio",   width=120,   anchor="center")
        self.tre.column("Cantidad", width=120,   anchor="center")
        self.tre.column("Total",    width=150,   anchor="center")
        
        #Nombre de etiqueta "Precio a pagar"
        self.label_precio_total = tk.Label(self, text="Precio a pagar: S/ 0", font="sans 20 bold", bg="#87CEEB")
        self.label_precio_total.place(x=680, y=550)
        
        #boton de pagar
        boton_pagar = tk.Button(self, text="Pagar", font="sans 14 bold", command=self.Realizar_pago)
        boton_pagar.place(x=60,y=550,width=180,height=40)
        
        #boton de ver ventas realizadas
        boton_ventas = tk.Button(self, text="Ver Ventas Realizadas", font="sans 14 bold", command=self.ver_ventas_realizadas)
        boton_ventas.place(x=290,y=550,width=280,height=40)
        
        
        
                                            