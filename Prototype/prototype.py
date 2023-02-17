import tkinter as tk
from math import *

GRID_WIDTH = 7
GRID_HEIGHT = 6

WINDOW_WIDTH = 7 * 100
WINDOW_HEIGHT = 6 * 100
BACKGROUND_COLOR = "#D05090"

window = tk.Tk()

window.geometry(str(WINDOW_WIDTH) + "x" + str(WINDOW_HEIGHT))
window.title("IN200 - Puissance 4")
window.resizable(False, False)

#Menu

menu = tk.Canvas(width = WINDOW_WIDTH, height = WINDOW_HEIGHT, background = BACKGROUND_COLOR)

play_rect = menu.create_rectangle(3*WINDOW_WIDTH/8, 2*WINDOW_HEIGHT/12, 5*WINDOW_WIDTH/8, 4*WINDOW_HEIGHT/12, outline = "black")
text_pos = menu.coords(play_rect)
play_text = menu.create_text(text_pos[0] + (text_pos[2] - text_pos[0]) / 2, text_pos[1] + (text_pos[3] - text_pos[1]) / 2, text = "Play", font = ("Comic Sans MS", int(text_pos[3] - text_pos[1]) - 30))

quit_rect = menu.create_rectangle(3*WINDOW_WIDTH/8, 8*WINDOW_HEIGHT/12, 5*WINDOW_WIDTH/8, 10*WINDOW_HEIGHT/12, outline = "black")
quit_pos = menu.coords(quit_rect)
quit_text = menu.create_text(quit_pos[0] + (quit_pos[2] - quit_pos[0]) / 2, quit_pos[1] + (quit_pos[3] - quit_pos[1]) / 2, text = "Quit", font = ("Comic Sans MS", int(quit_pos[3] - quit_pos[1]) - 30))

def menu_mouse(event):

	if event.x > text_pos[0] and event.x < text_pos[2] and event.y > text_pos[1] and event.y < text_pos[3]:
		menu.pack_forget()
		game.pack()
		window.bind("<Button-1>", game_mouse)

	if event.x > quit_pos[0] and event.x < quit_pos[2] and event.y > quit_pos[1] and event.y < quit_pos[3]:
		window.destroy()

#game

game = tk.Canvas(width = WINDOW_WIDTH, height = WINDOW_HEIGHT, background = BACKGROUND_COLOR)
slots = []

for y in range(GRID_HEIGHT):
	for x in range(GRID_WIDTH):
		slots.append(game.create_oval((WINDOW_WIDTH / GRID_WIDTH)*x, (WINDOW_HEIGHT / GRID_HEIGHT)*y, (WINDOW_WIDTH / GRID_WIDTH)*(x+1), (WINDOW_HEIGHT / GRID_HEIGHT)*(y+1)))

tokens = []


grid = [[0 for x in range(WINDOW_WIDTH)] for y in range(WINDOW_HEIGHT)]

turn = False

def game_mouse(event):
	global turn

	turn = not turn
	token_color = ""

	if turn:
		token_color = "yellow"
	else:
		token_color = "red"

	column = int(event.x * GRID_WIDTH / WINDOW_WIDTH)
	row = GRID_HEIGHT - 1

	for y in range(GRID_HEIGHT - 1):
		if grid[y + 1][column] != 0:
			row = y
			break

	grid[row][column] = int(turn) + 1
	tokens.append(game.create_oval(column * (WINDOW_WIDTH/GRID_WIDTH), row * (WINDOW_HEIGHT/GRID_HEIGHT), (column + 1)*(WINDOW_WIDTH/GRID_WIDTH), (row + 1)*(WINDOW_HEIGHT/GRID_HEIGHT), fill = token_color))
	


	print(check_column())

def check_line():

	count = 0
	counting = 0

	for y in range(GRID_HEIGHT):
		for x in range(GRID_WIDTH):	
			if counting != grid[y][x]:
				counting = grid[y][x]
				count = 0
			count += 1

			if count == 4 and counting != 0:
				return counting
		count = 0
		counting = 0

	return 0

def check_column():

	count = 0
	counting = 0

	for x in range(GRID_WIDTH):
		for y in range(GRID_HEIGHT):
			if counting != grid[y][x]:
				counting = grid[y][x]
				count = 0
			count += 1

			if count == 4 and counting != 0:
				return counting
		count = 0
		counting = 0

	return 0

'''
def check_right_diag():

	for x in range(GRID_WIDTH):
		for y in range(GRID_HEIGHT):

			i = 0

			while x + i 

	return 0
'''
menu.pack()

window.bind("<Button-1>", menu_mouse)

window.mainloop()