'''
	Puissance 4

	JOURDAIN Anaïs
	CAICEDO LEMOS Vanessa
	GHARIB ALI BARURA Sama

	Programme réalisé dans le cadre du projet d'IN200
'''

import tkinter as tk
import numpy as np
from math import *
import time
from PIL import Image, ImageTk

#Options

WINDOW_SIZE            = np.array([700, 600])
BACKGROUND             = "steelblue2" 
GRID_POS               = WINDOW_SIZE / 4
GRID_SIZE              = WINDOW_SIZE / 2
GRID_DIMS              = np.array([7, 6])
SLOT_SIZE              = GRID_SIZE / GRID_DIMS
TOKEN_BOX              = SLOT_SIZE * 4/5
TOKEN_COLLISION_RADIUS = SLOT_SIZE[1] / 2
GRAVITY                = 2

#Variables globales

root = tk.Tk()
root.geometry(str(WINDOW_SIZE[0])+'x'+str(WINDOW_SIZE[1]) + "+0+0")
root.title("Puissance 4")
root.resizable(False, False)

canvas = tk.Canvas(root, width = WINDOW_SIZE[0], height = WINDOW_SIZE[1], bg = BACKGROUND)
canvas.grid()

widgets = [] #Toutes les widget crées doivent être dans cette liste afin de pouvoir les supprimer

tokens_pos = [] #position des jetons dans le monde physique
tokens_speed = [] #vitesse des jetons
tokens_visu = [] #Representation graphique des jetons
is_static = [] #Définit si un jeton est un objet physique ou non

click_time = 0

slot_image = Image.open("slot.png")
slot_image = slot_image.resize(np.array(SLOT_SIZE + (1, 1), dtype = int))
slot_imagetk = ImageTk.PhotoImage(slot_image)

logo_image = Image.open("puiss4nce.jpg")
logo_image = logo_image.resize(np.array(WINDOW_SIZE, dtype=int))
logo_imagetk = ImageTk.PhotoImage(logo_image)

play_image=Image.open("slot.png")
play_image=play_image.resize((100,100))
play_imagetk=ImageTk.PhotoImage(play_image)

fade_delay = 1500
fade_duration = 500

player1 = ""
player2 = ""

matrice_base = np.zeros([GRID_DIMS[1],GRID_DIMS[0]]) #crée une matrice représentant la grille


#Outils

def rectangle(pos, size):
	return canvas.create_rectangle(pos[0], pos[1], pos[0] + size[0], pos[1] + size[1])
def oval(pos, size):
	oval = canvas.create_oval(pos[0], pos[1], pos[0] + size[0], pos[1] + size[1], width = 0)
	canvas.lower(oval) # On dessine les ovales derrière les images
	return oval
def create_slot(pos):
	pos += SLOT_SIZE/2
	slot = canvas.create_image(pos[0], pos[1], image = slot_imagetk)
	canvas.tkraise(slot) # On dessine les images devant les ovales
	return slot
def set_pos(obj, pos, size):
	canvas.coords(obj, pos[0], pos[1], pos[0] + size[0], pos[1] + size[1])
def delete_widgets():
	for i in range(len(widgets)):
		widgets[i].place_forget()
	widgets.clear()

#Jeu

playing = True
turn = False #False : Jeton jaune / True : Jeton rouge

def game_keys(event):
	global playing

	if event.keysym == "Escape":
		playing = False
		turn = False
		tokens_pos.clear()
		tokens_speed.clear()
		tokens_visu.clear()
		is_static.clear()

		delete_widgets()

		root.after(1, main_menu)


def game_clicks(event):
	global turn
	global click_time
	global matrice_base
	global player1
	global player2

	#cree une "matrice" (liste imbriquée) des coordonnées des jetons
	coordonnees_jetons_statiques = np.array([])
	for y in range (400,50,-50): #coordonnées en y des jetons lorsqu'ils sont statiques 
		for x in range(175,525,50): #coordonnées en x des jetons lorsqu'ils sont statiques
			coordonnees_jetons_statiques = np.append(coordonnees_jetons_statiques,([x,y]))

	coordonnees_en_paires = []
	for i in range (0, len(coordonnees_jetons_statiques)-1, 2): #couple les coordonnées x et y de chaque position
		coordonnees_en_paires.append([coordonnees_jetons_statiques[i],coordonnees_jetons_statiques[i+1]])
	
	matrice_coordonées = []
	for i in range (0, len(coordonnees_en_paires), GRID_DIMS[0]): #positionne les couples aux indices qui leur correspondent
		matrice_coordonées.append(coordonnees_en_paires[i:i+GRID_DIMS[0]])

	if event.x <= GRID_POS[0] or event.x >= GRID_POS[0] + GRID_SIZE[0]:
		return # Si le clique est en dehors de la grille, on ne crée pas de jeton
	
	pos = np.array((GRID_POS[0] + SLOT_SIZE[0] * int((event.x - GRID_POS[0])/SLOT_SIZE[0]), GRID_POS[1] - SLOT_SIZE[1])) # On met le jeton dans la bonne colonne
	
	for t in tokens_pos:
		if pos[0] + SLOT_SIZE[0] <= t[0]\
		or pos[0] >= t[0] + SLOT_SIZE[0]\
		or pos[1] + SLOT_SIZE[1] * 2 <= t[1]\
		or pos[1] >= t[1] + SLOT_SIZE[1]:
			pass # Il n'y a pas de jeton qui obstrue le point d'appartition du nouveau jeton
		else:
			return # Un jeton obstrue le point d'apparition

	turn = not turn

	visu = oval(pos, SLOT_SIZE)
	if turn == True: #au rouge de jouer
		canvas.itemconfig(visu, fill = "firebrick")
		widgets[0]["text"] = "Au tour de " + player2
		for i in range(len(matrice_coordonées)):
			if (list(pos))in matrice_coordonées[i]:
				matrice_base[i-1,(matrice_coordonées[i].index(list(pos)))] = 1 #cherche l'indice des coordonées du jeton et affecte la matrice base dans ce même indice
		linea4_rojo_horizontal()
		linea4_rojo_vertical()	
	else: #au jaune de jouer
		canvas.itemconfig(visu, fill = "gold")
		widgets[0]["text"] = "Au tour de " + player1
		for i in range(len(matrice_coordonées)):
			if (list(pos))in matrice_coordonées[i]:
				matrice_base[i-1,(matrice_coordonées[i].index(list(pos)))] = 2
		linea4_amarillo_horizontal()
		linea4_amarillo_vertical()
	print(matrice_base)

	tokens_pos.append(pos)
	tokens_speed.append(np.array((0, 0)))
	tokens_visu.append(visu)
	is_static.append(False)

	click_time = time.time()

def game_physics():
	global playing

	for i in range(len(tokens_pos)):

		if is_static[i]:
			continue # Nous n'appliquons pas le comportement physique à un jeton statique

		collides_another = False

		for j in range(len(tokens_pos)):
			if i==j or tokens_pos[j][1] < tokens_pos[i][1]:
				continue # On évite de tester si le jeton se collisione lui même ou avec un jeton plus haut


			if tokens_pos[i][0] > tokens_pos[j][0] + SLOT_SIZE[0]-1 or tokens_pos[i][0] + SLOT_SIZE[0]-1 < tokens_pos[j][0]:
				pass
			elif tokens_pos[i][1] + SLOT_SIZE[1] + tokens_speed[i][1] > tokens_pos[j][1] + tokens_speed[j][1]:
				collides_another = True
				break
			

		if not collides_another and tokens_pos[i][1] + tokens_speed[i][1] + SLOT_SIZE[1] <= GRID_POS[1] + GRID_SIZE[1]:
			tokens_pos[i] += tokens_speed[i]
		else:
			tokens_speed[i][1] = -1/2 * tokens_speed[i][1]
			if abs(tokens_speed[i][1]) < 1:
				tokens_pos[i] = GRID_POS + SLOT_SIZE * np.array( (tokens_pos[i] - GRID_POS) / SLOT_SIZE, dtype = int)
				is_static[i] = True

		tokens_speed[i][1] += GRAVITY
		set_pos(tokens_visu[i], tokens_pos[i], SLOT_SIZE)

	if playing:
		root.after(int(1000/60), game_physics)


def game_visu():

	canvas.delete("all")

	for y in range(GRID_DIMS[1]):
		for x in range(GRID_DIMS[0]):
			#oval((x, y) * SLOT_SIZE + GRID_POS, SLOT_SIZE)
			create_slot((x, y) * SLOT_SIZE + GRID_POS)

	turn_info = tk.Label(canvas, text = "Au tour de " + player1, font = ("Comic Sans MS", WINDOW_SIZE[1]//16), bg = BACKGROUND)
	turn_info.place(x = 10, y = 10)

	widgets.append(turn_info)

def game():
	global playing

	playing = True

	canvas.bind("<Button-1>", game_clicks)
	root.bind("<Key>", game_keys)

	game_visu()
	root.after(1, game_physics)

#Menu principal

def main_menu_clicks(event):
	global player1
	global player2

	player1 = widgets[1].get()
	player2 = widgets[2].get()

	delete_widgets()

	root.after(1, game)

def main_menu_visu():

	canvas.delete("all")

	#bouton de lancement
	
	canvas.create_image(200,200,image=play_imagetk)

	#instruction pour les joueurs

	font_size = int(WINDOW_SIZE[1]/23)

	instruction = tk.Label(canvas, text = "Veuillez entrer le nom des joueurs avant de commencer", fg="black", font = ("Comic Sans MS", font_size), bg = BACKGROUND)
	instruction.place(x = WINDOW_SIZE[0]/100, y = WINDOW_SIZE[1]/6 +200)

	#zone de saisie pour que les joueurs rentrent leurs noms 
	saisie1 = tk.Entry(canvas)
	saisie1.insert(0, "Joueur 1")
	saisie1.place(x=WINDOW_SIZE[0]/100+10, y=WINDOW_SIZE[1]/6 +300)

	saisie2 = tk.Entry(canvas)
	saisie2.insert(0, "Joueur 2")
	saisie2.place(x=WINDOW_SIZE[0]/10 +400, y=WINDOW_SIZE[1]/6 +300)

	widgets.append(instruction)
	widgets.append(saisie1)
	widgets.append(saisie2)


def main_menu():

	canvas.bind("<Button-1>", main_menu_clicks)
	main_menu_visu()

#Ecran de lancement

logo = canvas.create_image(WINDOW_SIZE[0] / 2, WINDOW_SIZE[1] / 2, image = logo_imagetk)
fade = rectangle((0, 0), WINDOW_SIZE)
canvas.itemconfig(fade, fill = "")

def process_fade():
	global fade
	
	root.after(0, lambda : canvas.itemconfig(fade, fill = "black", stipple = "gray12"))

	root.after(1 * fade_duration // 5, lambda : canvas.itemconfig(fade, stipple = "gray25"))

	root.after(2 * fade_duration // 5, lambda : canvas.itemconfig(fade, stipple = "gray50"))

	root.after(3 * fade_duration //5, lambda : canvas.itemconfig(fade, stipple = "gray75"))

	root.after(4 * fade_duration //5, lambda : canvas.itemconfig(fade, stipple = ""))

	root.after(fade_duration, main_menu)

root.after(fade_delay, process_fade)

#main_menu()



#Fonctions pour vérifier le gagnant

def linea4_rojo_horizontal(): #vérifie s'il y a 4 jetons rouges de suite horizontalement
	for y in range (len(matrice_base)):
		counter = 0
		for x in range (len(matrice_base[0])):
			if matrice_base[y][x] == 1:
				counter+=1
				if x in range ((len(matrice_base[0])-1)):
					if matrice_base[y][x+1]!=1:
						break
		if counter == 4: 
			print("Linea 4 rojo horizontal")

def linea4_rojo_vertical(): #vérifie s'il y a 4 jetons rouges de suite verticalement
	for x in range (len(matrice_base[0])):
		counter = 0
		for y in range (len(matrice_base)):
			if matrice_base[y][x] == 1:
				counter+=1
				if y in range ((len(matrice_base)-1)):
					if matrice_base[y+1][x]!=1:
						break
		if counter == 4: 
			print("Linea 4 rojo vertical")

def linea4_amarillo_horizontal(): #vérifie s'il y a 4 jetons jaunes de suite horizontalement
	for y in range (len(matrice_base)):
		counter = 0
		for x in range (len(matrice_base[0])):
			if matrice_base[y][x] == 2:
				counter+=1
				if x in range ((len(matrice_base[0])-1)):
					if matrice_base[y][x+1]!=2:
						break
		if counter == 4: 
			print("Linea 4 amarillo horizontal")

def linea4_amarillo_vertical(): #vérifie s'il y a 4 jetons jaunes de suite horizontalement
	for x in range (len(matrice_base[0])):
		counter = 0
		for y in range (len(matrice_base)):
			if matrice_base[y][x] == 2:
				counter+=1
				if y in range ((len(matrice_base)-1)):
					if matrice_base[y+1][x]!=2:
						break
		if counter == 4: 
			print("Linea 4 amarillo vertical")

root.mainloop()