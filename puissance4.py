'''
	Puissance 4

	JOURDAIN Anaïs
	CAICEDO LEMOS Vanessa
	GHARIB ALI BARURA Sama

	Programme réalisé dans le cadre du projet d'IN200
'''

import tkinter as tk
import numpy as np

#Options

WINDOW_SIZE = np.array([700, 700])
BACKGROUND  = "royalblue" 
GRID_POS    = WINDOW_SIZE / 4
GRID_SIZE   = WINDOW_SIZE / 2
GRID_DIMS   = np.array([7, 6])
SLOT_SIZE   = GRID_SIZE / GRID_DIMS
TOKEN_BOX   = SLOT_SIZE * 4/5
GRAVITY     = 2

#Variables globales

root = tk.Tk()
root.geometry(str(WINDOW_SIZE[0])+'x'+str(WINDOW_SIZE[1]) + "+0+0")
root.title("Puissance 4")
root.resizable(False, False)

canvas = tk.Canvas(root, width = WINDOW_SIZE[0], height = WINDOW_SIZE[1], bg = BACKGROUND)
canvas.grid()

tokens_pos = [] #position des jetons dans le monde physique
tokens_speed = [] #vitesse des jetons
tokens_visu = [] #Representation graphique des jetons

#Outils

def rectangle(pos, size):
	return canvas.create_rectangle(pos[0], pos[1], pos[0] + size[0], pos[1] + size[1])
def oval(pos, size):
	return canvas.create_oval(pos[0], pos[1], pos[0] + size[0], pos[1] + size[1])
def set_pos(obj, pos, size):
	canvas.coords(obj, pos[0], pos[1], pos[0] + size[0], pos[1] + size[1])

#Jeu

playing = True
turn = False #False : Jeton jaune / True : Jeton rouge

def game_keys(event):
	global playing

	if event.keysym == "Escape":
		playing = False
		tokens_pos.clear()
		tokens_speed.clear()
		tokens_visu.clear()

		root.after(1, main_menu)

def game_clicks(event):
	global turn

	turn = not turn

	pos = np.array((event.x, event.y)) - SLOT_SIZE/2
	visu = oval(pos, SLOT_SIZE)
	if turn:
		canvas.itemconfig(visu, fill = "firebrick")
	else:
		canvas.itemconfig(visu, fill = "gold")

	tokens_pos.append(pos)
	tokens_speed.append(np.array((0, 0)))
	tokens_visu.append(visu)


def game_physics():
	global playing

	for i in range(len(tokens_pos)):
		
		if tokens_pos[i][1] + tokens_speed[i][1] + SLOT_SIZE[1] <= GRID_POS[1] + GRID_SIZE[1]:
			tokens_pos[i] += tokens_speed[i]
		else:
			tokens_speed[i][1] = -3/4 * tokens_speed[i][1]
		
		tokens_speed[i][1] += GRAVITY
		set_pos(tokens_visu[i], tokens_pos[i], SLOT_SIZE)

	if playing:
		root.after(int(1000/60), game_physics)


def game_visu():

	canvas.delete("all")

	for y in range(GRID_DIMS[1]):
		for x in range(GRID_DIMS[0]):
			oval((x, y) * SLOT_SIZE + GRID_POS, SLOT_SIZE)

def game():
	global playing

	playing = True

	canvas.bind("<Button-1>", game_clicks)
	root.bind("<Key>", game_keys)

	game_visu()
	root.after(1, game_physics)

#Menu principal

def main_menu_clicks(event):
	
	root.after(1, game)

def main_menu_visu():
	#instruction pour les joueurs 
	instruction=tk.Label(canvas, text = "Nom des joueurs : ", fg="black")
	#instruction.grid(row = 0, column = 0)
	instruction.place(x = 10, y = 10)

	#zone de saisie pour que les joueurs rentrent leurs noms 
	saisie=tk.Entry()	
	joueur1=saisie.get()

	saisie2=tk.Entry()
	joueur2=saisie2.get()

	canvas.delete("all")



def main_menu():

	canvas.bind("<Button-1>", main_menu_clicks)
	main_menu_visu()

main_menu()

root.mainloop()