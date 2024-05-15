from tkinter import *
from tkinter import messagebox as tkMessageBox
from collections import deque
import random
import platform
from datetime import datetime

# Definir constantes

# Tamaño del tablero
TAM_X = 10
TAM_Y = 10

# Estados
ESTADO_POR_DEFECTO = 0
ESTADO_PULSADO = 1
ESTADO_BANDERA = 2

BTN_PULSAR = "<Button-1>"
BTN_BANDERA = "<Button-2>" if platform.system() == 'Darwin' else "<Button-3>"

ventana = None

class Buscaminas:
    """ Clase buscaminas

    Crea el tablero de juego y tiene la logica del juego
    """

    def __init__(self, tk):
        """ Crea el tablero de juego

        Args: tk (Tk) - ventana principal

        Returns: None
        """

        # importar imágenes
        self.imagenes = {
            "normal": PhotoImage(file = "images/tile_plain.gif"),
            "pulsado": PhotoImage(file = "images/tile_clicked.gif"),
            "mina": PhotoImage(file = "images/tile_mine.gif"),
            "bandera": PhotoImage(file = "images/tile_flag.gif"),
            "incorrecta": PhotoImage(file = "images/tile_wrong.gif"),
            "numeros": []
        }
        for i in range(1, 9):
            self.imagenes["numeros"].append(PhotoImage(file = "images/tile_"+str(i)+".gif"))

        # configurar el marco
        self.tk = tk
        self.marco = Frame(self.tk)
        self.marco.pack()

        # configurar etiquetas/UI
        self.etiquetas = {
            "tiempo": Label(self.marco, text = "00:00:00"),
            "minas": Label(self.marco, text = "Minas: 0"),
            "banderas": Label(self.marco, text = "Banderas: 0")
        }
        # parte superior completa
        self.etiquetas["tiempo"].grid(row = 0, column = 0, columnspan = TAM_Y)

        # inferior izquierda
        self.etiquetas["minas"].grid(row = TAM_X+1, column = 0, columnspan = int(TAM_Y/2))

        # inferior derecha
        self.etiquetas["banderas"].grid(row = TAM_X+1, column = int(TAM_Y/2)-1, columnspan = int(TAM_Y/2))

        # iniciar juego
        self.reiniciar()

        # iniciar temporizador
        self.actualizarTemporizador() 

    def configurar(self):
        # crear variables de banderas y celdas pulsadas
        self.contadorBanderas = 0
        self.contadorBanderasCorrectas = 0
        self.contadorPulsadas = 0
        self.tiempoInicio = None

        # crear botones
        self.celdas = dict({})
        self.minas = 0
        for x in range(0, TAM_X):
            for y in range(0, TAM_Y):
                if y == 0:
                    self.celdas[x] = {}

                id = str(x) + "_" + str(y)
                esMina = False

                # imagen de celda modificable por razones de depuración:
                gfx = self.imagenes["normal"]

                # cantidad de minas actualmente aleatorias
                if random.uniform(0.0, 1.0) < 0.1:
                    esMina = True
                    self.minas += 1

                celda = {
                    "id": id,
                    "esMina": esMina,
                    "estado": ESTADO_POR_DEFECTO,
                    "coordenadas": {
                        "x": x,
                        "y": y
                    },
                    "boton": Button(self.marco, image = gfx),
                    "minas": 0 # calculado después de construir el grid
                }

                celda["boton"].bind(BTN_PULSAR, self.alPulsar(x, y))
                celda["boton"].bind(BTN_BANDERA, self.alClicDerecho(x, y))
                celda["boton"].grid( row = x+1, column = y ) # desplazado por 1 fila para el temporizador

                self.celdas[x][y] = celda

        # recorrer de nuevo para encontrar minas cercanas y mostrar número en celda
        for x in range(0, TAM_X):
            for y in range(0, TAM_Y):
                mc = 0
                for n in self.obtenerVecinos(x, y):
                    mc += 1 if n["esMina"] else 0
                self.celdas[x][y]["minas"] = mc

    def reiniciar(self):
        self.configurar()
        self.actualizarEtiquetas()

    def actualizarEtiquetas(self):
        self.etiquetas["banderas"].config(text = "Banderas: "+str(self.contadorBanderas))
        self.etiquetas["minas"].config(text = "Minas: "+str(self.minas))

    def finJuego(self, ganado):
        for x in range(0, TAM_X):
            for y in range(0, TAM_Y):
                if self.celdas[x][y]["esMina"] == False and self.celdas[x][y]["estado"] == ESTADO_BANDERA:
                    self.celdas[x][y]["boton"].config(image = self.imagenes["incorrecta"])
                if self.celdas[x][y]["esMina"] == True and self.celdas[x][y]["estado"] != ESTADO_BANDERA:
                    self.celdas[x][y]["boton"].config(image = self.imagenes["mina"])

        self.tk.update()

        msg = "¡Has ganado! ¿Jugar de nuevo?" if ganado else "¡Has perdido! ¿Jugar de nuevo?"
        res = tkMessageBox.askyesno("Fin del juego", msg)
        if res:
            self.reiniciar()
        else:
            self.tk.quit()

    def actualizarTemporizador(self):
        ts = "00:00:00"
        if self.tiempoInicio != None:
            delta = datetime.now() - self.tiempoInicio
            ts = str(delta).split('.')[0] # eliminar ms
            if delta.total_seconds() < 36000:
                ts = "0" + ts # rellenar con cero
        self.etiquetas["tiempo"].config(text = ts)
        self.marco.after(100, self.actualizarTemporizador)

    def obtenerVecinos(self, x, y):
        vecinos = []
        coordenadas = [
            {"x": x-1,  "y": y-1},  # arriba derecha
            {"x": x-1,  "y": y},    # arriba medio
            {"x": x-1,  "y": y+1},  # arriba izquierda
            {"x": x,    "y": y-1},  # izquierda
            {"x": x,    "y": y+1},  # derecha
            {"x": x+1,  "y": y-1},  # abajo derecha
            {"x": x+1,  "y": y},    # abajo medio
            {"x": x+1,  "y": y+1},  # abajo izquierda
        ]
        for n in coordenadas:
            try:
                vecinos.append(self.celdas[n["x"]][n["y"]])
            except KeyError:
                pass
        return vecinos

    def alPulsar(self, x, y):
        return lambda Boton: self.pulsarCelda(self.celdas[x][y])

    def alClicDerecho(self, x, y):
        return lambda Boton: self.clicDerecho(self.celdas[x][y])

    def pulsarCelda(self, celda):
        if self.tiempoInicio == None:
            self.tiempoInicio = datetime.now()

        if celda["esMina"] == True:
            # fin del juego
            self.finJuego(False)
            return

        # cambiar imagen
        if celda["minas"] == 0:
            celda["boton"].config(image = self.imagenes["pulsado"])
            self.despejarCeldasVecinas(celda["id"])
        else:
            celda["boton"].config(image = self.imagenes["numeros"][celda["minas"]-1])
        # si aún no está marcada como pulsada, cambiar estado y contar
        if celda["estado"] != ESTADO_PULSADO:
            celda["estado"] = ESTADO_PULSADO
            self.contadorPulsadas += 1
        if self.contadorPulsadas == (TAM_X * TAM_Y) - self.minas:
            self.finJuego(True)

    def clicDerecho(self, celda):
        if self.tiempoInicio == None:
            self.tiempoInicio = datetime.now()

        # si no está pulsada
        if celda["estado"] == ESTADO_POR_DEFECTO:
            celda["boton"].config(image = self.imagenes["bandera"])
            celda["estado"] = ESTADO_BANDERA
            celda["boton"].unbind(BTN_PULSAR)
            # si es una mina
            if celda["esMina"] == True:
                self.contadorBanderasCorrectas += 1
            self.contadorBanderas += 1
            self.actualizarEtiquetas()
        # si está marcada, desmarcar
        elif celda["estado"] == ESTADO_BANDERA:
            celda["boton"].config(image = self.imagenes["normal"])
            celda["estado"] = ESTADO_POR_DEFECTO
            celda["boton"].bind(BTN_PULSAR, self.alPulsar(celda["coordenadas"]["x"], celda["coordenadas"]["y"]))
            # si es una mina
            if celda["esMina"] == True:
                self.contadorBanderasCorrectas -= 1
            self.contadorBanderas -= 1
            self.actualizarEtiquetas()

    def despejarCeldasVecinas(self, id):
        cola = deque([id])

        while len(cola) != 0:
            clave = cola.popleft()
            partes = clave.split("_")
            x = int(partes[0])
            y = int(partes[1])

            for celda in self.obtenerVecinos(x, y):
                self.despejarCelda(celda, cola)

    def despejarCelda(self, celda, cola):
        if celda["estado"] != ESTADO_POR_DEFECTO:
            return

        if celda["minas"] == 0:
            celda["boton"].config(image = self.imagenes["pulsado"])
            cola.append(celda["id"])
        else:
            celda["boton"].config(image = self.imagenes["numeros"][celda["minas"]-1])

        celda["estado"] = ESTADO_PULSADO
        self.contadorPulsadas += 1

### FIN DE CLASES ###

def principal():
    # crear instancia de Tk
    ventana = Tk()
    # establecer título del programa
    ventana.title("Buscaminas")
    # crear instancia del juego
    buscaminas = Buscaminas(ventana)
    # ejecutar bucle de eventos
    ventana.mainloop()

if __name__ == "__main__":
    principal()

