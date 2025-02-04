from tkinter import *
import tkinter as tk
from ventas import Ventas
from inventario import Inventario
from clientes import Clientes
from pedidos import Pedidos
from proveedor import Proveedor
from informacion import Informacion

import sys
import os

class Container(tk.Frame):
    def __init__(self, padre, controlador):
        super().__init__(padre)
        self.controlador = controlador
        self.pack()
        self.place(x=0, y=0, width= 1100, height=650)
        self.widgets()
        self.frames = {}
        self.buttons = []
        for i in (Ventas, Inventario, Clientes, Pedidos, Proveedor, Informacion):
            frame = i(self)
            self.frames[i] = frame
            frame.pack()
            frame.config(bg="#87CEEB", highlightbackground= "gray", highlightthickness=1)
            frame.place(x=0, y=40, width=1100, height=610)
        self.show_frames(Ventas)
        
    def show_frames(self, container):
        frame = self.frames[container]
        frame.tkraise()
        
    def ventas(self):
        self.show_frames(Ventas)    
    
    def Inventario(self):
        self.show_frames(Inventario)    
        
    def Clientes(self):
        self.show_frames(Clientes)    
    
    def Pedidos(self):
        self.show_frames(Pedidos)    
    
    def Proveedor(self):
        self.show_frames(Proveedor)    
        
    def Informacion(self):
        self.show_frames(Informacion)          
        
    def widgets (self):
        frame2 = tk.Frame(self)
        frame2.place(x=0, y=0, width=1100, height=40)
        
        self.btn_ventas = Button(frame2, fg= "gray", text= "Ventas", font= "Arial 16 bold", command=self.ventas)
        self.btn_ventas.place(x=0, y=0, width=184, height=40)
        
        self.btn_inventario = Button(frame2, fg= "gray", text= "Inventario", font= "sans 16 bold", command=self.Inventario)
        self.btn_inventario.place(x=184, y=0, width=184, height=40)
        
        self.btn_clientes = Button(frame2, fg= "gray", text= "Clientes", font= "sans 16 bold", command=self.Clientes)
        self.btn_clientes.place(x=369, y=0, width=184, height=40)
        
        self.btn_pedidos = Button(frame2, fg= "gray", text= "Pedidos", font= "sans 16 bold", command=self.Pedidos)
        self.btn_pedidos.place(x=554, y=0, width=184, height=40)
        
        self.btn_proveedor = Button(frame2, fg= "gray", text= "Proveedor", font= "sans 16 bold", command=self.Proveedor)
        self.btn_proveedor.place(x=739, y=0, width=184, height=40)
        
        self.btn_informacion = Button(frame2, fg= "gray", text= "Informacion", font= "sans 16 bold", command=self.Informacion)
        self.btn_informacion.place(x=923, y=0, width=184, height=40)
        
        self.buttons ={self.btn_ventas, self.btn_inventario, self.btn_clientes, self.btn_pedidos, self.btn_proveedor, self.btn_informacion} 