from tkinter import *
from tkinter import ttk
from login import Login, Registro
from container import Container

class Manager(Tk):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.title("Market 1.0")
        self.geometry("1100x650+120+20")
        self.resizable(False, False)
        
        container = Frame(self)
        container.pack(side=TOP, fill=BOTH, expand=True)
        container.configure(bg="#87CEEB")

        self.frames = {}
        for i in (Login, Registro, Container):
            frame = i(container, self)  # Pasa self como master y controlador
            self.frames[i] = frame
            

        self.show_frame(Container)

        try:
            self.style = ttk.Style()
            self.style.theme_use("clam")
        except:
            print("El tema 'clam' no está disponible. Se usará el predeterminado.")

    def show_frame(self, frame_class):
        frame = self.frames[frame_class]
        frame.tkraise()

def main():
    app = Manager()
    app.mainloop()

if __name__ == "__main__":
    main()
