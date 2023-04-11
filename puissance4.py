'''
	Puissance 4

	JOURDAIN Anaïs
	CAICEDO LEMOS Vanessa
	GHARIB ALI BARURA Sama

	Programme réalisé dans le cadre du projet d'IN200
'''

import tkinter as tk
from tkinter import filedialog
import numpy as np
from math import *
import time
from PIL import Image, ImageTk
import random


#Variables globales


#Options
COLOR_PALETTE          = {
	"Red" : "#f63f34",
	"Yellow" : "#efbd20",
	"Cyan" : "#65abaf",
	"Grey" : "#9cafb7",
	"Turquoise" : "#59e38c"	

}
WINDOW_SIZE            = np.array([700, 600])
BACKGROUND             = "snow3"
GRID_DIMS              = np.array([7, 6])
GRID_POS               = WINDOW_SIZE / 4
GRID_SIZE              = WINDOW_SIZE / 2
SLOT_SIZE              = GRID_SIZE / GRID_DIMS
TOKEN_BOX              = SLOT_SIZE * 4/5
TOKEN_COLLISION_RADIUS = SLOT_SIZE[1] / 2
GRAVITY                = 2
WINNING_STREAK         = 4
NAME_PLAYER_1          = "Turing"
NAME_PLAYER_2          = "Conway"
COLOR_PLAYER_1         = COLOR_PALETTE["Red"]
COLOR_PLAYER_2         = COLOR_PALETTE["Yellow"]
SCORE_PLAYER_1         = 0 
SCORE_PLAYER_2         = 0
N_SET                  = 0

#Visual
root = tk.Tk()
root.geometry(str(WINDOW_SIZE[0])+'x'+str(WINDOW_SIZE[1]) + "+0+0")
root.title("Puissance 4")
root.resizable(False, False)

canvas = tk.Canvas(root, width = WINDOW_SIZE[0], height = WINDOW_SIZE[1], bg = BACKGROUND)

canvas.grid()

widgets = [] #Toutes les widget crées doivent être dans cette liste afin de pouvoir les supprime à chaque changement d'écran
tokens_pos = [] #position des jetons dans le monde physique
tokens_speed = [] #vitesse des jetons
tokens_visu = [] #Representation graphique des jetons
is_static = [] #Définit si un jeton est un objet physique ou non

click_time = 0 # Permet d'empêcher le joueur de spammer les cliques

slot_image = Image.open("slot.png") # Image des cases
slot_image = slot_image.resize(np.array(SLOT_SIZE + (1, 1), dtype = int))
slot_imagetk = ImageTk.PhotoImage(slot_image)

logo_image = Image.open("puiss4nce.jpg") # Logo de l'écran de démarrage
logo_image = logo_image.resize(np.array(WINDOW_SIZE, dtype=int))
logo_imagetk = ImageTk.PhotoImage(logo_image)

image_play=Image.open("background.jpeg") # Fond d'écran du menu principal
image_play_tk = ImageTk.PhotoImage(image_play)

fade_delay = 1500
fade_duration = 500

#Outils

# Fonctions permettant d'utiliser des tableaux numpy 1x2 (Vecteurs) pour créer des formes
def rectangle(pos, size):
	'''
		Retourne l'id tkinter d'un rectangle dont le côté supérieur gauche est à "pos" et qui mesure "size".
	'''
	return canvas.create_rectangle(pos[0], pos[1], pos[0] + size[0], pos[1] + size[1])
def oval(pos, size):
	'''
		Retourne l'id tkinter de l'oval inscrit dans le rectangle dont le point supérieur gauche est à "pos" et qui mesure "size"
	'''
	oval = canvas.create_oval(pos[0], pos[1], pos[0] + size[0], pos[1] + size[1], width = 0, fill = "red")
	canvas.lower(oval) # On dessine les ovales derrière les images
	return oval
def create_slot(pos):
	'''
		Crée une case de puissance quatre à pos
	'''
	pos += SLOT_SIZE/2
	slot = canvas.create_image(pos[0], pos[1], image = slot_imagetk)
	canvas.tkraise(slot) # On dessine les images devant les ovales
	return slot
def set_pos(obj, pos, size):
	'''
		Change la position et la taille d'un item du canvas
	'''
	canvas.coords(obj, pos[0], pos[1], pos[0] + size[0], pos[1] + size[1])

def delete_widgets():
	'''
		Supprime tous les widgets
	'''
	
	#canvas.delete("all")

	for i in range(len(widgets)):
		widgets[i].place_forget()
	widgets.clear()

def raycast(o_start, stride):
	'''
		Lance un "rayon" de "o_start" jusqu'à 4*"stride" avec un pas de "stride" s'intérompant
		lorsqu'il tombe sur un jeton d'une couleur différente et renvoie le nombre de jetons 
		d'une même couleur touchés. 
	'''

	global WINNING_STREAK

	start = o_start.copy() # On copie o_start pour éviter de le modifier globalement

	count = 1
	other_token = False
	ray = start
	verifying = ""

	for i in range(WINNING_STREAK):

		current_color = ""
		found = False
		for i_ in range(len(tokens_pos)):
			pos = tokens_pos[i_]
			if ray[0] >= pos[0] and ray[0] <= pos[0] + SLOT_SIZE[0] \
		   and ray[1] >= pos[1] and ray[1] <= pos[1] + SLOT_SIZE[1]: # <=> Si le rayon touche un jeton
				current_color = canvas.itemcget(tokens_visu[i_], "fill")
				found = True
				break
		if not found:
			break
		if i==0:
			verifying = current_color # La couleur que l'on vérifie est la couleur du premier jeton touché par le rayon
		elif current_color == verifying:
			count += 1
		else:
			break

		ray += stride

	return count

# Chargement / Sauvegarde

def save(path):

	try:
		out = open(path, "w")

		out.write(str(GRID_DIMS[0]) + ";" + str(GRID_DIMS[1]) + ";\n")

		for i in range(len(tokens_pos)):

			out.write(str(tokens_pos[i][0]) + ";" + str(tokens_pos[i][1]) + ";" 
				    + str(tokens_speed[i][0]) + ";" + str(tokens_speed[i][1]) + ";" + str(int(is_static[i])) + ";" + canvas.itemcget(tokens_visu[i], "fill")  + ";" + "\n")

		out.close()

		return True
	except:
		return False

def load(path):

	global COLOR_PLAYER_1
	global COLOR_PLAYER_2
	global SLOT_SIZE
	global GRID_DIMS
	global slot_image
	global slot_imagetk

	try:
		inn = open(path, "r")

		def_color = 0

		header = True
		reading = True
		while reading:
			
			line = inn.readline()

			if line and header:
				buffer = ""
				step = 0

				for c in line:
					if c == ";":
						GRID_DIMS[step] = int(buffer)
						buffer = ""
						step += 1
					else:
						buffer += c

				header = False

				SLOT_SIZE = GRID_SIZE / GRID_DIMS

				slot_image = slot_image.resize((int(SLOT_SIZE[0]), int(SLOT_SIZE[1])))
				slot_imagetk = ImageTk.PhotoImage(slot_image)

			elif line:
				
				buffer = ""
				phase = 0

				for c in line:

					if c == ";":
						if phase == 0:
							tokens_pos.append(np.array([float(buffer), 0]))
						elif phase == 1:
							tokens_pos[-1][1] = float(buffer)
						elif phase == 2:
							tokens_speed.append(np.array([float(buffer), 0]))
						elif phase == 3:
							tokens_speed[-1][1] = float(buffer)
						elif phase == 4:
							is_static.append(bool(buffer))
						elif phase == 5:
							oval((0, 0), (100, 100))
							visu = oval(tokens_pos[-1], SLOT_SIZE)
							canvas.itemconfig(visu, fill = buffer)
							tokens_visu.append(visu)

							if def_color == 0:
								COLOR_PLAYER_1 = buffer
								def_color += 1
							elif def_color == 1 and buffer != COLOR_PLAYER_1:
								COLOR_PLAYER_2 = buffer

						phase += 1
						buffer = ""
						continue

					buffer += c
			else:
				reading = False

		inn.close()

		return True # La lecture du fichier s'est bien passée
	except:
		return False # Le fichier n'a pas pu être lu.

def launch_load(path):

	delete_widgets()

	path = filedialog.askopenfilename()
	if load(path):
		root.after(1, game)
	else:
		widgets.append(tk.Label(canvas, text = "Erreur : Le fichier \"" + str(path) + "\" n'a pas pu être chargé !", fg = "red"))
		widgets.append(tk.Button(canvas, text = "OK", command = retourner))
		widgets[-2].place(x = 10, y = 10)
		widgets[-1].place(x = 10, y = 50)


#Jeu

playing = True
turn = False #False : Jeton jaune / True : Jeton rouge

def game_keys(event):
	'''
		Gère les entrées clavier lorsque le jeu tourne
	'''

	global playing

	if event.keysym == "Escape":
		retourner()
	if event.keysym == "BackSpace":
		annul_jeton()


def game_clicks(event):
	'''
		Gère les cliques lorsque le jeu tourne
	'''

	global turn
	global click_time
	global NAME_PLAYER_1
	global NAME_PLAYER_2
	global GRID_SIZE


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

	# Création d'un nouveau jeton

	visu = oval(pos, SLOT_SIZE)

	if turn:
		canvas.itemconfig(visu, fill = COLOR_PLAYER_1)
		widgets[0]["text"] = "Au tour de " + NAME_PLAYER_2
	else:
		canvas.itemconfig(visu, fill = COLOR_PLAYER_2)
		widgets[0]["text"] = "Au tour de " + NAME_PLAYER_1

	tokens_pos.append(pos)
	tokens_speed.append(np.array((0, 0)))
	tokens_visu.append(visu)
	is_static.append(False)
	
	click_time = time.time()

def annul_jeton():
	'''
		Annule le dernier jeton.
	'''
	global turn

	if len(tokens_pos) == 0: # Si il n'y a plus de jeton, nous interrompons la fonction
		return

	canvas.delete(tokens_visu[-1])
	tokens_pos.pop()
	tokens_speed.pop()
	tokens_visu.pop()
	is_static.pop()
	turn = not turn

def nouvelle_manche():
	for i in range (len(tokens_visu)):
		canvas.delete(tokens_visu[i])
	tokens_pos.clear()
	tokens_speed.clear()
	tokens_visu.clear()
	is_static.clear()


def jeu_set_match(N_SET):
	if SCORE_PLAYER_1 > (N_SET/2):
		widgets.append(tk.Label(canvas, text = str(NAME_PLAYER_1) + " emporte le set!", font = ("Comic Sans MS", 15), bg = "white"))
		widgets[-1].place(x = int(WINDOW_SIZE[0]/2 - 50), y = 90)
	elif SCORE_PLAYER_2 > (N_SET/2):
		widgets.append(tk.Label(canvas, text = str(NAME_PLAYER_2) + " emporte le set!", font = ("Comic Sans MS", 15), bg = "white"))
		widgets[-1].place(x = int(WINDOW_SIZE[0]/2 - 50), y = 90)


def game_physics():
	'''
		Comportement physique des jetons (gravité, rebonds et collisions)
	'''

	global playing
	global WINNING_STREAK
	global SCORE_PLAYER_1
	global SCORE_PLAYER_2
	global N_SET

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

				horiz = raycast(tokens_pos[i] + TOKEN_BOX/2, (SLOT_SIZE[0], 0)) + raycast(tokens_pos[i] + TOKEN_BOX/2, (-SLOT_SIZE[0], 0)) - 1
				verti = raycast(tokens_pos[i] + TOKEN_BOX/2, (0, SLOT_SIZE[1])) + raycast(tokens_pos[i] + TOKEN_BOX/2, (0, -SLOT_SIZE[1])) - 1
				diag1 = raycast(tokens_pos[i] + TOKEN_BOX/2, (SLOT_SIZE[0], SLOT_SIZE[1])) + raycast(tokens_pos[i] + TOKEN_BOX/2, (-SLOT_SIZE[0], -SLOT_SIZE[1])) - 1
				diag2 = raycast(tokens_pos[i] + TOKEN_BOX/2, (SLOT_SIZE[0], -SLOT_SIZE[1])) + raycast(tokens_pos[i] + TOKEN_BOX/2, (-SLOT_SIZE[0], SLOT_SIZE[1])) - 1

				if horiz >= WINNING_STREAK or verti >= WINNING_STREAK or diag1 >= WINNING_STREAK or diag2 >= WINNING_STREAK:
					if turn == True:
						widgets.append(tk.Label(canvas, text = "Victoire de " + NAME_PLAYER_1 + "!!!", fg="red", font=("Calibri", 30), bg="white"))
						widgets[-1].place(x=10,y=270)
						SCORE_PLAYER_1+=1
					else: 
						widgets.append(tk.Label(canvas, text = "Victoire de " + NAME_PLAYER_2 + "!!!", fg="red", font=("Calibri", 30), bg="white"))
						widgets[-1].place(x=10,y=270)
						SCORE_PLAYER_2+=1
					print(SCORE_PLAYER_1, SCORE_PLAYER_2)
					widgets.append(tk.Label(canvas, text = "SCORE: " + str(SCORE_PLAYER_1) + " - " + str(SCORE_PLAYER_2), font = ("Comic Sans MS", 15), bg = "white"))
					widgets[-1].place(x = int(WINDOW_SIZE[0]/2 - 50), y = 90)
					jeu_set_match(N_SET)
					if SCORE_PLAYER_1 or SCORE_PLAYER_2 >= (N_SET/2):
						break
					else: 
						root.after(2000, nouvelle_manche)

		
		tokens_speed[i][1] += GRAVITY
		set_pos(tokens_visu[i], tokens_pos[i], SLOT_SIZE)
	


	if playing:
		root.after(int(1000/60), game_physics)



def game_visu():
	'''
		Crée les widgets et la grille du jeu
	'''
	global SCORE_PLAYER_1
	global SCORE_PLAYER_2

	for y in range(GRID_DIMS[1]):
		for x in range(GRID_DIMS[0]):
			#oval((x, y) * SLOT_SIZE + GRID_POS, SLOT_SIZE)
			create_slot((x, y) * SLOT_SIZE + GRID_POS)

	turn_info = tk.Label(canvas, font = ("Comic Sans MS", WINDOW_SIZE[1]//20), bg = BACKGROUND)
	if turn == 0:
		turn_info["text"] = NAME_PLAYER_1 + " commence !"
	else:
		turn_info["text"] = NAME_PLAYER_2 + " commence !"

	turn_info.place(x = 10, y = 10)

	widgets.append(turn_info)
	widgets.append(tk.Button(text = "Annuler le dernier jeton", font = ("Comic Sans MS", 12), command = annul_jeton))
	widgets[-1].place(x = int(WINDOW_SIZE[0] - 200), y = 10)
	widgets.append(tk.Button(text = "Sauvegarder", command = lambda: save(filedialog.asksaveasfilename())))
	widgets[-1].place(x = int(WINDOW_SIZE[0] / 2), y = int(WINDOW_SIZE[1] - 40))

	if N_SET != 0:
		widgets.append(tk.Label(canvas, text = "Set à " + str(N_SET) + " manches", font = ("Comic Sans MS", 15), bg = "white"))
		widgets[-1].place(x = int(WINDOW_SIZE[0]/2 - 100), y = 80)





#

def game():
	'''
		Initialisation du jeu
	'''
	global tokens_visu

	colors_copy = []
	for e in tokens_visu:
		colors_copy.append(canvas.itemcget(e, "fill"))

	canvas.delete("all")
	delete_widgets()
	tokens_visu.clear()
	for i in range(len(colors_copy)):
		tokens_visu.append(oval(tokens_pos[i], SLOT_SIZE))
		canvas.itemconfig(tokens_visu[-1], fill = colors_copy[i])

	global playing
	global turn

	playing = True
	turn=random.randint(0,1)
	canvas.bind("<Button-1>", game_clicks)
	root.bind("<Key>", game_keys)
	game_visu()
	root.after(1, game_physics)


#Menu principal

def main_menu_clicks():
	'''
		/!\\ Obsolète /!\\
		Gère les cliques du menu principal
	'''
	pass

def main_menu_visu():
	'''
		Crée les widgets du menu principal
	'''

	canvas.delete("all")

	canvas.create_image(WINDOW_SIZE[0]/2, WINDOW_SIZE[1]/2, image=image_play_tk)
	#canvas.create_image(0,0, image = image_play_tk)

	#instruction pour les joueurs, boutons du menu principal 

	font_size = int(WINDOW_SIZE[1]/23)
	
	canvas.create_text(WINDOW_SIZE[0]/2, 100, text="PUISSANCE 4", fill="red", font=("Copperplate", 50))
	canvas.pack()

	charger_jeu=tk.Button(canvas,text="Charger", fg="black",font = ("Calibri bold", 25), command = lambda: launch_load("saved_games/test.game"))
	charger_jeu.place(x=WINDOW_SIZE[0]/2 -60, y=300,anchor="nw")

	#fonction qui explique les instructions dans une nouvelle fenêtre

	def instructions():
		'''
			Montre les instructions de jeu
		'''
		delete_widgets()
		canvas.delete("all")
		charger_jeu.place_forget()
		quitter_jeu.place_forget()
		jouer.place_forget()
		instructions_jeu.place_forget()
		canvas.create_text(WINDOW_SIZE[0]/2, 100, text= "Instructions:", fill="black", font=("Calibri", font_size))
		canvas.create_text(WINDOW_SIZE[0]/2, 200, text= "-Pour mettre un jeton cliquez sur la colonne souhaitée", fill="black", font=("Calibri", 15))
		canvas.create_text(WINDOW_SIZE[0]/2, 250, text= "-Pour annuler un jeton cliquez sur le bouton droit de votre souris", fill="black", font=("Calibri", 15))
		canvas.create_text(WINDOW_SIZE[0]/2, 300, text= "-Le but du jeu est de positionner 4 jetons de la même couleur consécutivement", fill="black", font=("Calibri", 15))
		canvas.create_text(WINDOW_SIZE[0]/2, 350, text= "(horizontalement, verticalement ou diagonalement)", fill="black", font=("Calibri", 15))
		canvas.create_text(WINDOW_SIZE[0]/2, 400, text= "A vous de jouer!", fill="black", font=("Calibri", 15))
		canvas.pack()

	#nouveaux boutons au menu principal 

	instructions_jeu = tk.Button(canvas, text="Instructions", font=("Calibri bold", 25), command = instructions)
	instructions_jeu.place(x=WINDOW_SIZE[0]/2-78, y=350, anchor="nw")


	quitter_jeu=tk.Button(canvas,text="QUITTER",fg="red",font = ("Calibri bold", 15), command = quitter)
	quitter_jeu.place(x=WINDOW_SIZE[0]-110, y=WINDOW_SIZE[1]-50)

	retour = tk.Button(canvas, text="RETOURNER AU MENU PRINCIPAL", font = ("Calibri bold", 12), command = retourner)
	retour.place(x=25, y=WINDOW_SIZE[1]-50)

	jouer = tk.Button(canvas, text = "Jouer", font = ("Calibri bold", 25), command = game)
	jouer.place(x=300, y=250,anchor="nw") 


	options = tk.Button(canvas, text = "Options", font = ("Calibri bold", 24), command = menu_perso_jeu)
	options.place(x = 300, y = 450)

	widgets.append(jouer)
	#widgets.append(retour)
	#widgets.append(quitter_jeu)
	widgets.append(instructions_jeu)
	widgets.append(charger_jeu)
	widgets.append(options)

	

def main_menu():
	'''
		fonctions préliminaires au menu principal
	'''
	main_menu_visu()

#Ecran de lancement

logo = canvas.create_image(WINDOW_SIZE[0] / 2, WINDOW_SIZE[1] / 2, image = logo_imagetk)
fade = rectangle((0, 0), WINDOW_SIZE)
canvas.itemconfig(fade, fill = "")

def process_fade():
	'''
		Gère le dégradé du menu de lancement.
	'''

	global fade
	
	root.after(0, lambda : canvas.itemconfig(fade, fill = "black", stipple = "gray12"))

	root.after(1 * fade_duration // 5, lambda : canvas.itemconfig(fade, stipple = "gray25"))

	root.after(2 * fade_duration // 5, lambda : canvas.itemconfig(fade, stipple = "gray50"))

	root.after(3 * fade_duration //5, lambda : canvas.itemconfig(fade, stipple = "gray75"))

	root.after(4 * fade_duration //5, lambda : canvas.itemconfig(fade, stipple = ""))

	root.after(fade_duration, main_menu)

root.after(fade_delay, process_fade)

#main_menu()

def quitter():
	'''
		Inutile...
	'''
	root.destroy()

def retourner():
	'''
		Retourne au menu principal
	'''
	global playing
	global turn

	#canvas.delete("all")
	playing = False
	turn = False
	tokens_pos.clear()
	tokens_speed.clear()
	tokens_visu.clear()
	is_static.clear()
	canvas.unbind("<Button-1>")
	delete_widgets()
	root.after(1, main_menu)


def player_name_menu():

	global widgets

	canvas.delete("all")
	delete_widgets()

	def validate_names():
		global NAME_PLAYER_1
		global NAME_PLAYER_2
		global widgets

		NAME_PLAYER_1 = widgets[1].get()
		NAME_PLAYER_2 = widgets[2].get()

		root.after(1, retourner)

	widgets = [
		tk.Label (canvas, text = "Veuillez saisir vos noms", font = ("Copperplate", 30, "bold"), bg=BACKGROUND),
		tk.Entry(canvas, font = ("Copperplate", 25)),
		tk.Entry(canvas, font = ("Copperplate", 25)),
		tk.Button(canvas, text = "Valider", font = ("Copperplate", 23), command = validate_names)
	]
	widgets[0].place(x = WINDOW_SIZE[0]/2, y = 10, anchor = "n")
	widgets[1].insert(0, NAME_PLAYER_1)
	widgets[2].insert(0, NAME_PLAYER_2)
	

	for i in range(1, len(widgets)):
		widgets[i].place(x = 10, y = 50 + i * 66)
	

def grid_dimensions_menu():
	
	global GRID_DIMS
	global SLOT_SIZE
	global widgets
	global slot_image
	global slot_imagetk

	canvas.delete("all")
	delete_widgets()

	def validate_dims():
		global GRID_DIMS
		global SLOT_SIZE
		global widgets
		global slot_image
		global slot_imagetk

		try:
			GRID_DIMS[0] = int(widgets[0]["text"])
			GRID_DIMS[1] = int(widgets[1]["text"])
		except:
			GRID_DIMS[0] = 7
			GRID_DIMS[1] = 6

		SLOT_SIZE = GRID_SIZE / GRID_DIMS

		slot_image = slot_image.resize((int(SLOT_SIZE[0]), int(SLOT_SIZE[1])))
		slot_imagetk = ImageTk.PhotoImage(slot_image)

		root.after(1, retourner)


	widgets.append(tk.Label(canvas, text = str(GRID_DIMS[0])))
	widgets.append(tk.Label(canvas, text = str(GRID_DIMS[1])))
	widgets[0].place(x = 10, y = 10)
	widgets[1].place(x = 10, y = 60)

	def add_figure(index, fig):
		widgets[index]["text"] += fig
	def remove_figure(index):
		if len(widgets[index]["text"]) > 0:
			widgets[index]["text"] = widgets[index]["text"][:len(widgets[index]["text"]) - 1]

	for i in range(2):
		for j in range(10):
			widgets.append(tk.Button(canvas, text = str(j), command = lambda arg0 = i, arg1 = j: add_figure(arg0, str(arg1))))
			widgets[10 * i + j + 2].place(x = 10 + j * 50, y = 120 + i * 50)

	widgets.append(tk.Button(canvas, text = "Remove figure", command = lambda: remove_figure(0)))
	widgets[-1].place(x = 510, y = 120)
	widgets.append(tk.Button(canvas, text = "Remove figure", command = lambda: remove_figure(1)))
	widgets[-1].place(x = 510, y = 170)

	widgets.append(tk.Button(canvas, text = "Valider", font = ("Copperplate", 28), command = validate_dims))
	widgets[-1].place(x = 10, y = 300)

def tokens_color_menu():
	global COLOR_PLAYER_1
	global COLOR_PLAYER_2

	canvas.delete("all")
	delete_widgets()

	widgets.append(tk.Canvas(canvas, width = 50, height = 50, bg = COLOR_PLAYER_1, relief = "flat", bd = 10))
	widgets[-1].place(x = 10, y = 200)
	widgets.append(tk.Canvas(canvas, width = 50, height = 50, bg = COLOR_PLAYER_2, relief = "flat", bd = 10))
	widgets[-1].place(x = 10, y = 350)

	def validate_colors():
		global COLOR_PLAYER_1
		global COLOR_PLAYER_2

		COLOR_PLAYER_1 = widgets[0]["bg"]
		COLOR_PLAYER_2 = widgets[1]["bg"]

		root.after(1, retourner)

	def change_color(index, color_index):
		widgets[index]["bg"] = COLOR_PALETTE[list(COLOR_PALETTE.keys())[color_index]]

	for i in range(2):
		for j in range(len(list(COLOR_PALETTE.keys()))):
			widgets.append(tk.Button(canvas, relief = "sunken", bd = 8, bg = COLOR_PALETTE[list(COLOR_PALETTE.keys())[j]], command = lambda arg0 = i, arg1 = j: change_color(arg0, arg1)))
			widgets[-1].place(x = 350 + j * 48, y = 200 + i * 150)

	widgets.append(tk.Label(canvas, text = "Couleurs", font = ("Copperplate", 50, "bold"), bg = BACKGROUND))
	widgets[-1].place(x = WINDOW_SIZE[0]/2, y = 0, anchor = "n")

	widgets.append(tk.Label(canvas, text = "Couleur pour player 1 :", font = ("Copperplate", 24)))
	widgets[-1].place(x = 10, y = 150)

	widgets.append(tk.Label(canvas, text = "Couleurs pour player 2 :", font = ("Copperplate", 24)))
	widgets[-1].place(x = 10, y = 300)

	widgets.append(tk.Button(canvas, text = "Valider", font = ("Copperplate", 25), command = validate_colors))
	widgets[-1].place(x = 10, y = 450)

def winning_streak_menu():
	
	global WINNING_STREAK

	canvas.delete("all")
	delete_widgets()

	widgets.append(tk.Label(canvas, text = str(WINNING_STREAK)))
	widgets[0].place(x = 10, y = 10)

	def validate_winning_streak():
		global WINNING_STREAK

		try:
			WINNING_STREAK = int(widgets[0]["text"])
		except:
			WINNING_STREAK = 4

		root.after(1, retourner)

	def add_figure(fig):
		widgets[0]["text"] += fig
	def remove_figure():
		if len(widgets[0]["text"]) > 0:
			widgets[0]["text"] = widgets[0]["text"][:len(widgets[0]["text"]) - 1]

	for j in range(10):
		widgets.append(tk.Button(canvas, text = str(j), command = lambda arg = j: add_figure(str(arg))))
		
		if j != 9:
			widgets[j + 1].place(x = 10 + (j%3) * 50, y = 120 + int(j/3) * 50)
		else:
			widgets[j + 1].place(x = 10 + 50, y = 120 + int(j/3) * 50)

	widgets.append(tk.Button(canvas, text = "Remove figure", command = lambda: remove_figure()))
	widgets[-1].place(x = 510, y = 120)


	widgets.append(tk.Button(canvas, text = "Valider", font = ("Copperplate", 28), command = validate_winning_streak))
	widgets[-1].place(x = 10, y = 350)

def jeu_set_match_menu():

	global N_SET
	canvas.delete("all")
	delete_widgets()

	#(fonctions à améliorer après)
	def set_3():
		global N_SET
		N_SET = 3
		retourner()
	set3 = tk.Button(canvas, text = "3", font = ("Copperplate", 25), command = set_3)
	widgets.append(set3)
	set3.place(x = 390, y = 120)

	def set_5():
		global N_SET
		N_SET = 5
		retourner()
	set5 = tk.Button(canvas, text = "5", font = ("Copperplate", 25), command = set_5)
	widgets.append(set5)
	set5.place(x = 450, y = 120)
	
	def set_7():
		global N_SET
		N_SET = 7
		retourner()

	set7 = tk.Button(canvas, text = "7", font = ("Copperplate", 25), command = set_7)
	widgets.append(set7)
	set7.place(x = 510, y = 120)
	

def menu_perso_jeu():
	'''
		Menu avec pour modifier/personnaliser le jeu avant de commencer
	'''

	global widgets

	canvas.delete("all")
	delete_widgets()

	font_size = int(WINDOW_SIZE[1]/23)
	

	widgets = [
		tk.Label (canvas, text = "Options", font = ("Copperplate", font_size * 2), bg="#9cafb7")
	,	  tk.Button(canvas, text = "Player names", font = ("Copperplate", font_size), command = player_name_menu)
	, 	  tk.Button(canvas, text = "Grid dimensions", font = ("Copperplate", font_size), command = grid_dimensions_menu)
	, 	  tk.Button(canvas, text = "Tokens color", font = ("Copperplate", font_size), command = tokens_color_menu)
	, 	  tk.Button(canvas, text = "Winning streak", font = ("Copperplate", font_size), command = winning_streak_menu)
	,     tk.Button(canvas, text = "Set / Match", font = ("Copperplate", font_size), command = jeu_set_match_menu)
	]
	
	widgets[0].place(x = 240, y = 10)
	for i in range(1, len(widgets)):
		widgets[i].place(x = 10, y = font_size * 3 + 10 + (font_size * 2 + 10) * i)



root.mainloop()