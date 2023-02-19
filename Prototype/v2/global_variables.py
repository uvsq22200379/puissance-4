import tkinter as tk
from tools import *

WINDOW_SIZE = Vector(800, 800)
BACKGROUND  = "#EE60AA" 
GRID_RECT = Rectangle(Vector(100, 100), Vector(700, 600))
GRID_DIMS = Vector(7, 6)

game_running = True

window = tk.Tk()
window.geometry(str(WINDOW_SIZE.x) + "x" + str(WINDOW_SIZE.y))
window.title("IN200 - Puissance 4")

canvas = tk.Canvas(width = WINDOW_SIZE.x, height = WINDOW_SIZE.y, background = BACKGROUND)
canvas.pack()